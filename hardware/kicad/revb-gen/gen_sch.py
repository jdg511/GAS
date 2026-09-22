"""Generate circuit-board.kicad_sch (KiCad 10 format) from design.py.

Connectivity is by local net labels: every pin gets a short stub wire and a label.
"""
import os, sys, uuid, copy, collections
sys.path.insert(0, os.path.dirname(__file__))
from sexp import parse, dump, find, find_all, Sym
import design

SYMDIR = "/home/claude/kicad-symbols"
OUT = "/home/claude/gas-revb/out"
os.makedirs(OUT, exist_ok=True)

PROJECT = "circuit-board"
import json as _json
try:
    MPN_MAP = _json.load(open(os.path.join(OUT, "mpn_map.json")))
except Exception:
    MPN_MAP = {}
SHEET_UUID = "7b1c0d2e-3f40-4a51-8b62-9c73d0e1f2a3"

def U(seed):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "gas-revb/" + seed))

# ---------------------------------------------------------------- symbol library
_lib_cache = {}

def load_lib_symbol(lib, name):
    """Return the flattened symbol tree for lib:name (extends resolved)."""
    key = (lib, name)
    if key in _lib_cache:
        return _lib_cache[key]
    if lib == "GAS_Parts":
        tree = copy.deepcopy(CUSTOM_SYMBOLS[name])
    else:
        path = f"{SYMDIR}/{lib}.kicad_symdir/{name}.kicad_sym"
        top = parse(open(path).read())[0]
        tree = None
        for c in top:
            if isinstance(c, list) and c and c[0] == "symbol":
                tree = c
                break
        ext = find(tree, "extends")
        if ext:
            parent = copy.deepcopy(load_lib_symbol(lib, ext[1]))
            parent_name = ext[1]
            # take parent, then override with child properties
            child_props = {p[1]: p for p in find_all(tree, "property")}
            merged = [c for c in parent if not (isinstance(c, list) and c and c[0] == "property")]
            # keep parent props not overridden
            for p in find_all(parent, "property"):
                if p[1] not in child_props:
                    merged.append(p)
            for p in child_props.values():
                merged.append(p)
            # rename sub-symbols
            for c in merged:
                if isinstance(c, list) and c and c[0] == "symbol":
                    c[1] = c[1].replace(parent_name, name, 1)
            merged[1] = name
            tree = merged
    # remove any lingering extends
    tree = [c for c in tree if not (isinstance(c, list) and c and c[0] == "extends")]
    _lib_cache[key] = tree
    return tree

def pins_of(tree, unit):
    """Return list of (number, name, x, y, angle, length, etype) for a unit (unit 0 = common)."""
    out = []
    for sub in find_all(tree, "symbol"):
        nm = sub[1]
        parts = nm.rsplit("_", 2)
        if len(parts) < 3:
            continue
        u = int(parts[1])
        if u not in (0, unit):
            continue
        for p in find_all(sub, "pin"):
            at = find(p, "at")
            ln = find(p, "length")
            num = find(p, "number")[1]
            name = find(p, "name")[1]
            out.append((num, name, float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0.0,
                        float(ln[1]) if ln else 0.0, str(p[1])))
    return out

def bbox(tree):
    xs, ys = [0], [0]
    for sub in find_all(tree, "symbol"):
        for shape in sub:
            if not isinstance(shape, list):
                continue
            if shape[0] in ("rectangle",):
                s, e = find(shape, "start"), find(shape, "end")
                xs += [float(s[1]), float(e[1])]; ys += [float(s[2]), float(e[2])]
            elif shape[0] == "polyline":
                for xy in find_all(find(shape, "pts"), "xy"):
                    xs.append(float(xy[1])); ys.append(float(xy[2]))
            elif shape[0] == "pin":
                at = find(shape, "at"); xs.append(float(at[1])); ys.append(float(at[2]))
            elif shape[0] == "circle":
                c = find(shape, "center"); r = float(find(shape, "radius")[1])
                xs += [float(c[1]) - r, float(c[1]) + r]; ys += [float(c[2]) - r, float(c[2]) + r]
    return min(xs), min(ys), max(xs), max(ys)

# ---------------------------------------------------------------- custom symbols
def _prop(name, val, x, y, hide=False):
    p = [Sym("property"), name, val, [Sym("at"), x, y, 0], [Sym("show_name"), Sym("no")], [Sym("do_not_autoplace"), Sym("no")]]
    if hide:
        p.append([Sym("hide"), Sym("yes")])
    p.append([Sym("effects"), [Sym("font"), [Sym("size"), 1.27, 1.27]]])
    return p

def _pin(etype, x, y, ang, name, num, length=2.54):
    return [Sym("pin"), Sym(etype), Sym("line"), [Sym("at"), x, y, ang], [Sym("length"), length],
            [Sym("name"), name, [Sym("effects"), [Sym("font"), [Sym("size"), 1.27, 1.27]]]],
            [Sym("number"), num, [Sym("effects"), [Sym("font"), [Sym("size"), 1.27, 1.27]]]]]

def _rect(x1, y1, x2, y2):
    return [Sym("rectangle"), [Sym("start"), x1, y1], [Sym("end"), x2, y2],
            [Sym("stroke"), [Sym("width"), 0.254], [Sym("type"), Sym("default")]],
            [Sym("fill"), [Sym("type"), Sym("background")]]]

def box_symbol(name, desc, left_pins, right_pins, w=15.24, ref="U"):
    """left_pins/right_pins: list of (number, name, etype)."""
    n = max(len(left_pins), len(right_pins))
    h = (n + 1) * 2.54
    top = h / 2
    body = _rect(-w / 2, top, w / 2, -top)
    pins = []
    for i, (num, nm, et) in enumerate(left_pins):
        y = top - 2.54 * (i + 1)
        pins.append(_pin(et, -w / 2 - 2.54, y, 0, nm, num))
    for i, (num, nm, et) in enumerate(right_pins):
        y = top - 2.54 * (i + 1)
        pins.append(_pin(et, w / 2 + 2.54, y, 180, nm, num))
    sym = [Sym("symbol"), name, [Sym("pin_names"), [Sym("offset"), 1.016]], [Sym("exclude_from_sim"), Sym("no")],
           [Sym("in_bom"), Sym("yes")], [Sym("on_board"), Sym("yes")],
           _prop("Reference", ref, 0, top + 2.54), _prop("Value", name, 0, -top - 2.54),
           _prop("Footprint", "", 0, 0, True), _prop("Datasheet", "", 0, 0, True), _prop("Description", desc, 0, 0, True),
           [Sym("symbol"), f"{name}_0_1", body],
           [Sym("symbol"), f"{name}_1_1"] + pins]
    return sym

CUSTOM_SYMBOLS = {
    "THAT2180": box_symbol("THAT2180", "THAT 2180 Blackmer VCA, SIP-8",
                           [("1", "IN", "input"), ("2", "EC+", "input"), ("3", "EC-", "input"), ("4", "SYM", "input")],
                           [("7", "V+", "power_in"), ("8", "OUT", "output"), ("6", "GND", "power_in"), ("5", "V-/ISET", "passive")]),
    "THAT2252": box_symbol("THAT2252", "THAT 2252 RMS-level detector, SIP-8",
                           [("1", "IN", "input"), ("2", "IBIAS", "input"), ("4", "SYM", "input"), ("6", "CAP", "passive")],
                           [("8", "V+", "power_in"), ("7", "OUT", "output"), ("3", "GND", "power_in"), ("5", "V-", "power_in")]),
    "VTL5C3": box_symbol("VTL5C3", "Vactrol LED/LDR optocoupler, axial",
                         [("1", "LED_A", "passive"), ("2", "LED_K", "passive")],
                         [("3", "LDR", "passive"), ("4", "LDR", "passive")], w=12.7, ref="VT"),
}

# ---------------------------------------------------------------- placement
def cell_size(tree, unit):
    x1, y1, x2, y2 = bbox(tree)
    w = (x2 - x1) + 2 * 12.7   # room for stub + label
    h = (y2 - y1) + 2 * 7.62
    w = max(w, 27.94)
    h = max(h, 20.32)
    # snap to 1.27
    return (round(w / 1.27) * 1.27, round(h / 1.27) * 1.27)

def snap(v, g=1.27):
    return round(round(v / g) * g, 4)

# ---------------------------------------------------------------- emit
def emit():
    lib_symbols = {}
    items = []
    labels_used = collections.Counter()
    pin_net_records = []   # (ref, unit, pin, net)

    # group parts by block
    by_block = collections.OrderedDict()
    for p in design.parts:
        by_block.setdefault(p["block"], []).append(p)

    page_w = 1189.0 - 20   # A0 landscape width usable
    x0, y0 = 20.0, 25.0
    cur_x, cur_y = x0, y0
    row_h = 0.0
    texts = []

    def place_symbol(p, unit, x, y):
        nonlocal items
        lib, name = p["lib"].split(":")
        tree = load_lib_symbol(lib, name)
        lib_symbols[p["lib"]] = tree
        ref = p["ref"]
        sym = [Sym("symbol"), [Sym("lib_id"), p["lib"]], [Sym("at"), x, y, 0], [Sym("unit"), unit], [Sym("body_style"), 1],
               [Sym("exclude_from_sim"), Sym("no")], [Sym("in_bom"), Sym("no" if (ref.startswith("#") or (ref.startswith("H") and ref[1:].isdigit())) else "yes")],
               [Sym("on_board"), Sym("yes" if not ref.startswith("#") else "no")], [Sym("in_pos_files"), Sym("yes")],
               [Sym("dnp"), Sym("yes" if p["props"].get("DNP") == "yes" else "no")], [Sym("fields_autoplaced"), Sym("yes")], [Sym("uuid"), U(f"sym/{ref}/{unit}")]]
        x1, y1, x2, y2 = bbox(tree)
        top = y - y2 - 1.27
        sym.append(_prop("Reference", ref, x, top - 2.54))
        sym.append(_prop("Value", p["value"], x, top))
        sym.append(_prop("Footprint", p["fp"], x, y, True))
        sym.append(_prop("Datasheet", p["props"].get("Datasheet", ""), x, y, True))
        sym.append(_prop("Description", p["props"].get("Description", ""), x, y, True))
        props = dict(p["props"])
        if ref in MPN_MAP and "MPN" not in props:
            props["MPN"], props["Manufacturer"] = MPN_MAP[ref]
        elif ref in MPN_MAP:
            props["Manufacturer"] = MPN_MAP[ref][1]
        for k, v in props.items():
            if k in ("Datasheet", "Description", "DNP"):
                continue
            sym.append(_prop(k, v, x, y, True))
        # pins (all pins of the whole symbol must be listed once per instance? KiCad lists pins of the unit)
        for (num, nm, px, py, ang, ln, et) in pins_of(tree, unit):
            sym.append([Sym("pin"), num, [Sym("uuid"), U(f"pin/{ref}/{unit}/{num}")]])
        sym.append([Sym("instances"), [Sym("project"), PROJECT, [Sym("path"), "/" + SHEET_UUID,
                    [Sym("reference"), ref], [Sym("unit"), unit]]]])
        items.append(sym)
        # stubs + labels
        nets = p["units"].get(unit, {})
        for (num, nm, px, py, ang, ln, et) in pins_of(tree, unit):
            if num not in nets:
                if et in ("power_in", "power_out", "input", "output", "passive") and num in ("",):
                    continue
                # unlisted pin: mark no-connect (e.g. mounting hole has no pins)
                sx, sy = snap(x + px), snap(y - py)
                items.append([Sym("no_connect"), [Sym("at"), sx, sy], [Sym("uuid"), U(f"nc/{ref}/{unit}/{num}")]])
                continue
            net = nets[num]
            sx, sy = snap(x + px), snap(y - py)
            if net is None:
                items.append([Sym("no_connect"), [Sym("at"), sx, sy], [Sym("uuid"), U(f"nc/{ref}/{unit}/{num}")]])
                continue
            # outward direction = opposite of pin angle (angle 0 -> pin body to the right -> outward is left)
            d = {0: (-1, 0), 180: (1, 0), 90: (0, 1), 270: (0, -1)}[int(ang) % 360]
            ex, ey = snap(sx + d[0] * 2.54), snap(sy + d[1] * 2.54)
            if ln == 0:  # PWR_FLAG has zero-length pin
                ex, ey = sx, sy
            else:
                items.append([Sym("wire"), [Sym("pts"), [Sym("xy"), sx, sy], [Sym("xy"), ex, ey]],
                              [Sym("stroke"), [Sym("width"), 0], [Sym("type"), Sym("default")]],
                              [Sym("uuid"), U(f"wire/{ref}/{unit}/{num}")]])
            rot = 0 if d[0] >= 0 and d[1] == 0 else (180 if d[0] < 0 else (90 if d[1] < 0 else 270))
            just = {0: "left bottom", 180: "right bottom", 90: "left bottom", 270: "right bottom"}[rot]
            lab = [Sym("global_label"), net, [Sym("shape"), Sym("passive")], [Sym("at"), ex, ey, rot], [Sym("fields_autoplaced"), Sym("yes")],
                   [Sym("effects"), [Sym("font"), [Sym("size"), 1.27, 1.27]], [Sym("justify")] + [Sym(j) for j in just.split()]],
                   [Sym("uuid"), U(f"label/{ref}/{unit}/{num}")],
                   [Sym("property"), "Intersheetrefs", "${INTERSHEET_REFS}", [Sym("at"), ex, ey, 0], [Sym("show_name"), Sym("no")], [Sym("do_not_autoplace"), Sym("no")],
                    [Sym("hide"), Sym("yes")], [Sym("effects"), [Sym("font"), [Sym("size"), 1.27, 1.27]]]]]
            items.append(lab)
            labels_used[net] += 1
            pin_net_records.append((ref, unit, num, net))

    for block, plist in by_block.items():
        # new row for each block with a title text
        if cur_x != x0:
            cur_y += row_h + 12.7
            cur_x, row_h = x0, 0.0
        texts.append((block, cur_x, cur_y - 5.08))
        cur_y += 5.08
        for p in plist:
            lib, name = p["lib"].split(":")
            tree = load_lib_symbol(lib, name)
            for unit in sorted(p["units"].keys()):
                w, h = cell_size(tree, unit)
                if cur_x + w > page_w:
                    cur_y += row_h + 5.08
                    cur_x, row_h = x0, 0.0
                x1, y1, x2, y2 = bbox(tree)
                cx = snap(cur_x + w / 2 - (x1 + x2) / 2)
                cy = snap(cur_y + h / 2 + (y1 + y2) / 2)
                place_symbol(p, unit, cx, cy)
                cur_x += w
                row_h = max(row_h, h)
        cur_y += row_h + 12.7
        cur_x, row_h = x0, 0.0
    total_h = cur_y + 20

    # ------------------------------------------------------------ checks
    single = sorted(n for n, c in labels_used.items() if c < 2)
    # build sheet
    sch = [Sym("kicad_sch"), [Sym("version"), 20260306], [Sym("generator"), "eeschema"], [Sym("generator_version"), "10.0"],
           [Sym("uuid"), SHEET_UUID], [Sym("paper"), "A0"] if total_h <= 841 else [Sym("paper"), "User", 1189, snap(total_h + 20)],
           [Sym("title_block"), [Sym("title"), "GAS Rev B - Circuit Board (Drive, HPF, 7-mode circuit, LPF)"],
            [Sym("date"), "2026-09-13"], [Sym("rev"), "B"], [Sym("company"), "Illicit Apothecary"],
            [Sym("comment"), 1, "Replaces Rev A filter-clipper board. Modes: Clean, Tube, Tape, Tube Screamer, Opto, FET, VCA"],
            [Sym("comment"), 2, "Generated from design.py (netlist-by-label capture). See hardware/rev-b-circuit-board-definition.md"]]]
    ls = [Sym("lib_symbols")]
    for lid in sorted(lib_symbols):
        t = copy.deepcopy(lib_symbols[lid])
        lib, name = lid.split(":")
        t[1] = lid
        ls.append(t)
    sch.append(ls)
    for (txt, x, y) in texts:
        sch.append([Sym("text"), txt, [Sym("exclude_from_sim"), Sym("no")], [Sym("at"), snap(x), snap(y), 0],
                    [Sym("effects"), [Sym("font"), [Sym("size"), 2.54, 2.54], [Sym("bold"), Sym("yes")]], [Sym("justify"), Sym("left")]],
                    [Sym("uuid"), U("text/" + txt)]])
    sch.extend(items)
    sch.append([Sym("sheet_instances"), [Sym("path"), "/", [Sym("page"), "1"]]])
    sch.append([Sym("embedded_fonts"), Sym("no")])
    open(f"{OUT}/{PROJECT}.kicad_sch", "w").write(dump(sch) + "\n")

    # custom symbol library file
    lib = [Sym("kicad_symbol_lib"), [Sym("version"), 20241209], [Sym("generator"), "gas_revb"]]
    for name, t in CUSTOM_SYMBOLS.items():
        lib.append(copy.deepcopy(t))
    open(f"{OUT}/GAS_Parts.kicad_sym", "w").write(dump(lib) + "\n")

    # netlist report
    nets = collections.defaultdict(list)
    for (ref, unit, num, net) in pin_net_records:
        nets[net].append(f"{ref}.{num}")
    with open(f"{OUT}/netlist-report.txt", "w") as f:
        for n in sorted(nets):
            f.write(f"{n}: {' '.join(nets[n])}\n")
    print("parts:", len(design.parts), "placed symbols:", sum(1 for i in items if i[0] == "symbol"),
          "nets:", len(nets), "sheet height mm:", round(total_h))
    if single:
        print("SINGLE-PIN NETS:", single)
    return single

if __name__ == "__main__":
    emit()
