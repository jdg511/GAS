"""Write <board>.kicad_sch (KiCad 10) from a core.Board. Netlist-by-label capture."""
import os, sys, uuid, copy, collections
sys.path.insert(0, os.path.dirname(__file__))
from sexp import parse, dump, find, find_all, Sym
import core

_libfile_cache = {}
_sym_cache = {}


def U(board, seed):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"gas-revc/{board}/{seed}"))


def sheet_uuid(board):
    return U(board, "sheet")


def _lib_tree(lib):
    if lib not in _libfile_cache:
        path = os.path.join(core.SYMDIR, lib + ".kicad_sym")
        _libfile_cache[lib] = {c[1]: c for c in parse(open(path, encoding="utf8").read())[0]
                               if isinstance(c, list) and c and c[0] == "symbol"}
    return _libfile_cache[lib]


def load_symbol(lib_id):
    if lib_id in _sym_cache:
        return _sym_cache[lib_id]
    lib, name = lib_id.split(":")
    if lib == "GAS_Parts":
        tree = copy.deepcopy(CUSTOM[name])
    else:
        tree = copy.deepcopy(_lib_tree(lib)[name])
        ext = find(tree, "extends")
        if ext:
            parent = copy.deepcopy(load_symbol(f"{lib}:{ext[1]}"))
            pname = parent[1].split(":")[-1]
            child_props = {p[1]: p for p in find_all(tree, "property")}
            merged = [c for c in parent if not (isinstance(c, list) and c and c[0] == "property")]
            for p in find_all(parent, "property"):
                if p[1] not in child_props:
                    merged.append(p)
            merged += list(child_props.values())
            for c in merged:
                if isinstance(c, list) and c and c[0] == "symbol":
                    c[1] = c[1].replace(pname, name, 1)
            merged[1] = name
            tree = merged
    tree = [c for c in tree if not (isinstance(c, list) and c and c[0] == "extends")]
    _sym_cache[lib_id] = tree
    return tree


def pins_of(tree, unit):
    out = []
    for sub in find_all(tree, "symbol"):
        parts = sub[1].rsplit("_", 2)
        if len(parts) < 3:
            continue
        if int(parts[1]) not in (0, unit):
            continue
        for p in find_all(sub, "pin"):
            at = find(p, "at")
            ln = find(p, "length")
            out.append((find(p, "number")[1], find(p, "name")[1], float(at[1]), float(at[2]),
                        float(at[3]) if len(at) > 3 else 0.0, float(ln[1]) if ln else 0.0, str(p[1])))
    return out


def bbox(tree, unit=None):
    xs, ys = [0.0], [0.0]
    for sub in find_all(tree, "symbol"):
        parts = sub[1].rsplit("_", 2)
        if unit is not None and len(parts) == 3 and int(parts[1]) not in (0, unit):
            continue
        for sh in sub:
            if not isinstance(sh, list):
                continue
            if sh[0] == "rectangle":
                s, e = find(sh, "start"), find(sh, "end")
                xs += [float(s[1]), float(e[1])]; ys += [float(s[2]), float(e[2])]
            elif sh[0] == "polyline":
                for xy in find_all(find(sh, "pts"), "xy"):
                    xs.append(float(xy[1])); ys.append(float(xy[2]))
            elif sh[0] == "pin":
                at = find(sh, "at"); xs.append(float(at[1])); ys.append(float(at[2]))
            elif sh[0] == "circle":
                c = find(sh, "center"); r = float(find(sh, "radius")[1])
                xs += [float(c[1]) - r, float(c[1]) + r]; ys += [float(c[2]) - r, float(c[2]) + r]
    return min(xs), min(ys), max(xs), max(ys)


def _prop(name, val, x, y, hide=False, size=1.27):
    p = [Sym("property"), name, val, [Sym("at"), x, y, 0], [Sym("show_name"), Sym("no")], [Sym("do_not_autoplace"), Sym("no")]]
    if hide:
        p.append([Sym("hide"), Sym("yes")])
    p.append([Sym("effects"), [Sym("font"), [Sym("size"), size, size]]])
    return p


def _pin(et, x, y, ang, name, num, length=2.54):
    return [Sym("pin"), Sym(et), Sym("line"), [Sym("at"), x, y, ang], [Sym("length"), length],
            [Sym("name"), name, [Sym("effects"), [Sym("font"), [Sym("size"), 1.27, 1.27]]]],
            [Sym("number"), num, [Sym("effects"), [Sym("font"), [Sym("size"), 1.27, 1.27]]]]]


def box_symbol(name, desc, left, right, w=15.24, ref="U"):
    n = max(len(left), len(right))
    top = (n + 1) * 2.54 / 2
    body = [Sym("rectangle"), [Sym("start"), -w / 2, top], [Sym("end"), w / 2, -top],
            [Sym("stroke"), [Sym("width"), 0.254], [Sym("type"), Sym("default")]], [Sym("fill"), [Sym("type"), Sym("background")]]]
    pins = []
    for i, (num, nm, et) in enumerate(left):
        pins.append(_pin(et, -w / 2 - 2.54, top - 2.54 * (i + 1), 0, nm, num))
    for i, (num, nm, et) in enumerate(right):
        pins.append(_pin(et, w / 2 + 2.54, top - 2.54 * (i + 1), 180, nm, num))
    return [Sym("symbol"), name, [Sym("pin_names"), [Sym("offset"), 1.016]], [Sym("exclude_from_sim"), Sym("no")],
            [Sym("in_bom"), Sym("yes")], [Sym("on_board"), Sym("yes")],
            _prop("Reference", ref, 0, top + 2.54), _prop("Value", name, 0, -top - 2.54),
            _prop("Footprint", "", 0, 0, True), _prop("Datasheet", "", 0, 0, True), _prop("Description", desc, 0, 0, True),
            [Sym("symbol"), f"{name}_0_1", body], [Sym("symbol"), f"{name}_1_1"] + pins]


CUSTOM = {
    "BAT54_SOT23": box_symbol("BAT54_SOT23", "Schottky diode 30 V, SOT-23 (1 anode, 2 NC, 3 cathode)",
                              [("1", "A", "passive"), ("2", "NC", "no_connect")], [("3", "K", "passive")], w=7.62, ref="D"),
    "BCP56": box_symbol("BCP56", "NPN 80 V 1 A, SOT-223 (1 B, 2 C, 3 E, tab C)",
                        [("1", "B", "input")], [("2", "C", "passive"), ("3", "E", "passive")], w=10.16, ref="Q"),
    "BCP53": box_symbol("BCP53", "PNP 80 V 1 A, SOT-223 (1 B, 2 C, 3 E, tab C)",
                        [("1", "B", "input")], [("2", "C", "passive"), ("3", "E", "passive")], w=10.16, ref="Q"),
    "THAT2180": box_symbol("THAT2180", "Blackmer VCA SIP-8, THAT 2180 / 2181 / Coolaudio V2181 pinout",
                           [("1", "IN", "input"), ("2", "EC+", "input"), ("3", "EC-", "input"), ("4", "SYM", "input")],
                           [("7", "V+", "power_in"), ("8", "OUT", "output"), ("6", "GND", "power_in"), ("5", "V-/ISET", "passive")]),
    "DRV135": box_symbol("DRV135", "TI DRV134/DRV135 balanced line driver, SO-8 (1 -VO, 2 -SENSE, 3 GND, 4 VIN, 5 V-, 6 V+, 7 +SENSE, 8 +VO), gain 2",
                         [("4", "VIN", "input"), ("3", "GND", "power_in"), ("6", "V+", "power_in"), ("5", "V-", "power_in")],
                         [("8", "+VO", "output"), ("7", "+SENSE", "input"), ("1", "-VO", "output"), ("2", "-SENSE", "input")]),
    "PTD904": box_symbol("PTD904", "Bourns PTD904 4-gang 9 mm potentiometer, side-adjust PC pins. Gang g = 1..4 from the panel end; pin g1 = CCW end, g2 = wiper, g3 = CW end",
                         [("13", "G1-CW", "passive"), ("12", "G1-W", "passive"), ("11", "G1-CCW", "passive"),
                          ("23", "G2-CW", "passive"), ("22", "G2-W", "passive"), ("21", "G2-CCW", "passive")],
                         [("33", "G3-CW", "passive"), ("32", "G3-W", "passive"), ("31", "G3-CCW", "passive"),
                          ("43", "G4-CW", "passive"), ("42", "G4-W", "passive"), ("41", "G4-CCW", "passive")],
                         w=20.32, ref="VR"),
    "TEL12_DUAL": box_symbol("TEL12_DUAL", "TRACO TEL 12-24xx isolated DC/DC, dual output, DIP-16 metal case (pins 1 -Vin, 16 +Vin, 9 +Vout, 8 Com, 10 -Vout)",
                             [("16", "+VIN", "power_in"), ("1", "-VIN", "power_in")],
                             [("9", "+VOUT", "power_out"), ("8", "COM", "power_out"), ("10", "-VOUT", "power_out")], w=17.78, ref="PS"),
}


def cell(tree, unit):
    x1, y1, x2, y2 = bbox(tree, unit)
    w = max((x2 - x1) + 2 * 15.24, 30.48)
    h = max((y2 - y1) + 2 * 7.62, 20.32)
    return round(w / 1.27) * 1.27, round(h / 1.27) * 1.27


def snap(v, g=1.27):
    return round(round(v / g) * g, 4)


def emit(board, outdir):
    B = board.name
    SU = sheet_uuid(B)
    lib_symbols, items, texts = {}, [], []
    labels = collections.Counter()
    by_block = collections.OrderedDict()
    for p in board.parts:
        by_block.setdefault(p["block"], []).append(p)
    page_w = 1189.0 - 25
    x0, y0 = 20.0, 30.0
    cur_x, cur_y, row_h = x0, y0, 0.0
    first_unit_uuid = {}

    def place(p, unit, x, y):
        tree = load_symbol(p["lib"])
        lib_symbols[p["lib"]] = tree
        ref = p["ref"]
        is_virtual = ref.startswith("#")
        suid = U(B, f"sym/{ref}/{unit}")
        first_unit_uuid.setdefault(ref, suid)
        dnp = p["props"].get("DNP") == "yes"
        sym = [Sym("symbol"), [Sym("lib_id"), p["lib"]], [Sym("at"), x, y, 0], [Sym("unit"), unit], [Sym("body_style"), 1],
               [Sym("exclude_from_sim"), Sym("no")], [Sym("in_bom"), Sym("no" if is_virtual or p["lib"].startswith("Mechanical") else "yes")],
               [Sym("on_board"), Sym("no" if is_virtual else "yes")], [Sym("in_pos_files"), Sym("yes")],
               [Sym("dnp"), Sym("yes" if dnp else "no")], [Sym("fields_autoplaced"), Sym("yes")], [Sym("uuid"), suid]]
        x1, y1, x2, y2 = bbox(tree, unit)
        top = y - y2 - 1.27
        sym.append(_prop("Reference", ref, x, top - 2.54))
        sym.append(_prop("Value", p["value"], x, top))
        sym.append(_prop("Footprint", p["fp"], x, y, True))
        sym.append(_prop("Datasheet", p["props"].get("Datasheet", ""), x, y, True))
        sym.append(_prop("Description", p["props"].get("Description", ""), x, y, True))
        for k, v in p["props"].items():
            if k in ("Datasheet", "Description", "DNP"):
                continue
            sym.append(_prop(k, v, x, y, True))
        pins = pins_of(tree, unit)
        for (num, nm, px, py, ang, ln, et) in pins:
            sym.append([Sym("pin"), num, [Sym("uuid"), U(B, f"pin/{ref}/{unit}/{num}")]])
        sym.append([Sym("instances"), [Sym("project"), B, [Sym("path"), "/" + SU, [Sym("reference"), ref], [Sym("unit"), unit]]]])
        items.append(sym)
        nets = p["units"].get(unit, {})
        for (num, nm, px, py, ang, ln, et) in pins:
            sx, sy = snap(x + px), snap(y - py)
            net = nets.get(num, "__NC__")
            if net is None or net == "__NC__":
                items.append([Sym("no_connect"), [Sym("at"), sx, sy], [Sym("uuid"), U(B, f"nc/{ref}/{unit}/{num}")]])
                continue
            d = {0: (-1, 0), 180: (1, 0), 90: (0, 1), 270: (0, -1)}[int(ang) % 360]
            ex, ey = snap(sx + d[0] * 2.54), snap(sy + d[1] * 2.54)
            if ln == 0:
                ex, ey = sx, sy
            else:
                items.append([Sym("wire"), [Sym("pts"), [Sym("xy"), sx, sy], [Sym("xy"), ex, ey]],
                              [Sym("stroke"), [Sym("width"), 0], [Sym("type"), Sym("default")]], [Sym("uuid"), U(B, f"wire/{ref}/{unit}/{num}")]])
            rot = 0 if (d[0] >= 0 and d[1] == 0) else (180 if d[0] < 0 else (90 if d[1] < 0 else 270))
            just = {0: "left", 180: "right", 90: "left", 270: "right"}[rot]
            items.append([Sym("global_label"), net, [Sym("shape"), Sym("passive")], [Sym("at"), ex, ey, rot], [Sym("fields_autoplaced"), Sym("yes")],
                          [Sym("effects"), [Sym("font"), [Sym("size"), 1.27, 1.27]], [Sym("justify"), Sym(just)]],
                          [Sym("uuid"), U(B, f"label/{ref}/{unit}/{num}")],
                          [Sym("property"), "Intersheetrefs", "${INTERSHEET_REFS}", [Sym("at"), ex, ey, 0], [Sym("show_name"), Sym("no")],
                           [Sym("do_not_autoplace"), Sym("no")], [Sym("hide"), Sym("yes")], [Sym("effects"), [Sym("font"), [Sym("size"), 1.27, 1.27]]]]])
            labels[net] += 1

    for block, plist in by_block.items():
        texts.append((block, cur_x, cur_y))
        cur_y += 7.62
        for p in plist:
            tree = load_symbol(p["lib"])
            for unit in sorted(p["units"].keys()):
                w, h = cell(tree, unit)
                if cur_x + w > page_w:
                    cur_y += row_h + 2.54
                    cur_x, row_h = x0, 0.0
                x1, y1, x2, y2 = bbox(tree, unit)
                place(p, unit, snap(cur_x + w / 2 - (x1 + x2) / 2), snap(cur_y + h / 2 + (y1 + y2) / 2))
                cur_x += w
                row_h = max(row_h, h)
        cur_y += row_h + 12.7
        cur_x, row_h = x0, 0.0
    total_h = cur_y + 20
    paper = [Sym("paper"), "A0"] if total_h <= 820 else [Sym("paper"), "User", 1189, snap(total_h + 30)]
    tb = [Sym("title_block"), [Sym("title"), board.title], [Sym("date"), board.date], [Sym("rev"), board.rev],
          [Sym("company"), "Illicit Apothecary"]]
    for i, c in enumerate(board.comments[:8]):
        tb.append([Sym("comment"), i + 1, c])
    sch = [Sym("kicad_sch"), [Sym("version"), 20260306], [Sym("generator"), "eeschema"], [Sym("generator_version"), "10.0"],
           [Sym("uuid"), SU], paper, tb]
    ls = [Sym("lib_symbols")]
    for lid in sorted(lib_symbols):
        t = copy.deepcopy(lib_symbols[lid]); t[1] = lid
        ls.append(t)
    sch.append(ls)
    for (txt, x, y) in texts:
        sch.append([Sym("text"), txt, [Sym("exclude_from_sim"), Sym("no")], [Sym("at"), snap(x), snap(y), 0],
                    [Sym("effects"), [Sym("font"), [Sym("size"), 2.54, 2.54], [Sym("bold"), Sym("yes")]], [Sym("justify"), Sym("left")]],
                    [Sym("uuid"), U(B, "text/" + txt)]])
    sch.extend(items)
    sch.append([Sym("sheet_instances"), [Sym("path"), "/", [Sym("page"), "1"]]])
    sch.append([Sym("embedded_fonts"), Sym("no")])
    os.makedirs(outdir, exist_ok=True)
    open(os.path.join(outdir, B + ".kicad_sch"), "w", encoding="utf8").write(dump(sch) + "\n")
    single = sorted(n for n, c in labels.items() if c < 2)
    return first_unit_uuid, single


def write_symbol_lib(path):
    lib = [Sym("kicad_symbol_lib"), [Sym("version"), 20241209], [Sym("generator"), "gas_revc"]]
    for name, t in CUSTOM.items():
        lib.append(copy.deepcopy(t))
    open(path, "w", encoding="utf8").write(dump(lib) + "\n")
