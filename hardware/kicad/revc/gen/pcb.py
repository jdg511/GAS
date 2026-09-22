"""Build <board>.kicad_pcb with pcbnew from a core.Board: footprints, nets, placement, outline, rules."""
import os, sys, math, collections
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
import core
import gen_sch

MM = pcbnew.FromMM


def lib_path(lib):
    if lib == "GAS_Parts":
        return core.GASFP
    return os.path.join(core.FPDIR, lib + ".pretty")


def load_fp(fpid):
    lib, name = fpid.split(":")
    fp = pcbnew.FootprintLoad(lib_path(lib), name)
    if fp is None:
        raise RuntimeError(f"footprint not found {fpid}")
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp


def courtyard(fp):
    cy = fp.GetCourtyard(pcbnew.F_CrtYd)
    if cy.OutlineCount():
        bb = cy.BBox()
        return pcbnew.ToMM(bb.GetX()), pcbnew.ToMM(bb.GetY()), pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom())
    bb = fp.GetBoundingBox(False)
    return pcbnew.ToMM(bb.GetX()), pcbnew.ToMM(bb.GetY()), pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom())


def build(board, first_unit_uuid, out_path, gap=1.0, cluster_w=None):
    W, H = board.outline
    brd = pcbnew.BOARD()
    brd.SetCopperLayerCount(2)
    ds = brd.GetDesignSettings()
    ds.m_TrackMinWidth = MM(0.2)
    ds.m_MinClearance = MM(0.2)
    ds.m_ViasMinSize = MM(0.6)
    ds.m_MinThroughDrill = MM(0.3)
    ds.m_CopperEdgeClearance = MM(getattr(board, "edge_clearance", 0.5))
    ds.m_HoleClearance = MM(0.25)
    nc = ds.m_NetSettings.GetDefaultNetclass()
    nc.SetClearance(MM(0.2)); nc.SetTrackWidth(MM(0.25)); nc.SetViaDiameter(MM(0.6)); nc.SetViaDrill(MM(0.3))
    pwr = pcbnew.NETCLASS("Power")
    pwr.SetClearance(MM(0.25)); pwr.SetTrackWidth(MM(0.6)); pwr.SetViaDiameter(MM(0.8)); pwr.SetViaDrill(MM(0.4))
    ds.m_NetSettings.SetNetclass("Power", pwr)

    # outline: rectangle (default) or circle / clip / cutouts (board.shape)
    shape = outline_poly(board)
    for oi in range(shape.OutlineCount()):
        chains = [shape.Outline(oi)] + [shape.Hole(oi, hi) for hi in range(shape.HoleCount(oi))]
        for ch in chains:
            n = ch.PointCount()
            for i in range(n):
                a, c = ch.CPoint(i), ch.CPoint((i + 1) % n)
                seg = pcbnew.PCB_SHAPE(brd)
                seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
                seg.SetStart(pcbnew.VECTOR2I(a.x, a.y)); seg.SetEnd(pcbnew.VECTOR2I(c.x, c.y))
                seg.SetLayer(pcbnew.Edge_Cuts); seg.SetWidth(MM(0.1))
                brd.Add(seg)
    for (tx, ty, txt, size, layer) in getattr(board, "texts", []):
        t = pcbnew.PCB_TEXT(brd)
        t.SetText(txt); t.SetPosition(pcbnew.VECTOR2I(MM(tx), MM(ty)))
        t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size))); t.SetTextThickness(MM(size * 0.15))
        layer = {"F.SilkS": pcbnew.F_SilkS, "B.SilkS": pcbnew.B_SilkS, "F.Fab": pcbnew.F_Fab, "B.Fab": pcbnew.B_Fab}[layer] if isinstance(layer, str) else layer
        t.SetLayer(layer)
        if layer in (pcbnew.B_SilkS, pcbnew.B_Fab):
            t.SetMirrored(True)
        brd.Add(t)

    # nets
    netinfo = {}
    all_nets = sorted(board.nets().keys())
    for n in all_nets:
        ni = pcbnew.NETINFO_ITEM(brd, n)
        brd.Add(ni)
        netinfo[n] = ni
    for n in all_nets:
        if n in board.power_nets:
            ds.m_NetSettings.SetNetclassPatternAssignment(n, "Power")

    fps = {}
    for p in board.parts:
        if p["ref"].startswith("#"):
            continue
        fp = load_fp(p["fp"])
        fp.SetReference(p["ref"])
        fp.SetValue(p["value"])
        for k, v in p["props"].items():
            if k == "DNP":
                fp.SetDNP(v == "yes"); fp.SetExcludedFromPosFiles(v == "yes"); continue
            try:
                fld = fp.GetFieldByName(k)
            except Exception:
                fld = None
            if fld is None:
                fld = pcbnew.PCB_FIELD(fp, pcbnew.FIELD_T_USER, k)
                fld.SetVisible(False); fld.SetLayer(pcbnew.F_Fab)
                fld.SetText(str(v))
                fp.Add(fld)
            else:
                fld.SetText(str(v))
        if p["lib"].startswith("Mechanical"):
            fp.Reference().SetVisible(False)
        uid = first_unit_uuid.get(p["ref"])
        if uid:
            fp.SetPath(pcbnew.KIID_PATH("/" + gen_sch.sheet_uuid(board.name) + "/" + uid) if False else pcbnew.KIID_PATH("/" + uid))
        # pad nets
        padnet = {}
        for u, pins in p["units"].items():
            for pin, net in pins.items():
                if net is None:
                    continue
                for pad in p["pinmap"].get(pin, [pin]):
                    padnet[pad] = net
        for pad in fp.Pads():
            n = padnet.get(pad.GetNumber())
            if n:
                pad.SetNet(netinfo[n])
        brd.Add(fp)
        fps[p["ref"]] = (fp, p)

    # ---------------------------------------------------------------- placement
    occupied = []   # rects in mm

    def put(fp, x, y, rot=0, side="F"):
        fp.SetOrientationDegrees(rot)
        if side == "B" and not fp.IsFlipped():
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        fp.SetPosition(pcbnew.VECTOR2I(MM(0), MM(0)))
        x1, y1, x2, y2 = courtyard(fp)
        # position so that the courtyard centre is at x, y ? no: x, y is the footprint origin
        fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        cx1, cy1, cx2, cy2 = courtyard(fp)
        occupied.append((cx1, cy1, cx2, cy2))

    for ref, (x, y, rot, side) in board.fixed.items():
        put(fps[ref][0], x, y, rot, side)
    fixed_refs = list(board.fixed.keys())
    for i, a in enumerate(fixed_refs):
        ra = courtyard(fps[a][0])
        for b_ in fixed_refs[i + 1:]:
            rb = courtyard(fps[b_][0])
            if ra[0] < rb[2] and ra[2] > rb[0] and ra[1] < rb[3] and ra[3] > rb[1]:
                print(f"WARNING fixed parts overlap: {a} / {b_}")
    for (x0, y0, x1, y1) in getattr(board, "keepout_rects", []):
        occupied.append((x0, y0, x1, y1))
    # 1 mm copper keepout band along the board edge (Freerouting honours rule areas)
    band = 1.0
    if getattr(board, "shape", None):
        band = getattr(board, "edge_band", 0.6)
    if getattr(board, "shape", None) and band > 0:
        ring = shape.CloneDropTriangulation()
        inner = shape.CloneDropTriangulation()
        inner.Deflate(MM(band), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, MM(0.05))
        ring.BooleanSubtract(inner)
        for oi in range(ring.OutlineCount()):
            ka = pcbnew.ZONE(brd)
            ka.SetIsRuleArea(True)
            ka.SetDoNotAllowTracks(True); ka.SetDoNotAllowVias(True); ka.SetDoNotAllowZoneFills(False)
            ka.SetDoNotAllowPads(False); ka.SetDoNotAllowFootprints(False)
            ka.SetLayerSet(pcbnew.LSET.AllCuMask())
            ol = ka.Outline()
            ol.NewOutline()
            ch = ring.Outline(oi)
            for i in range(ch.PointCount()):
                ol.Append(ch.CPoint(i).x, ch.CPoint(i).y)
            for hi in range(ring.HoleCount(oi)):
                ol.NewHole()
                ch = ring.Hole(oi, hi)
                for i in range(ch.PointCount()):
                    ol.Append(ch.CPoint(i).x, ch.CPoint(i).y, 0, hi)
            brd.Add(ka)
    edges = () if getattr(board, "shape", None) else ((0, 0, W, band), (0, H - band, W, H), (0, 0, band, H), (W - band, 0, W, H))
    for (x0, y0, x1, y1) in edges:
        ka = pcbnew.ZONE(brd)
        ka.SetIsRuleArea(True)
        ka.SetDoNotAllowTracks(True); ka.SetDoNotAllowVias(True); ka.SetDoNotAllowZoneFills(False)
        ka.SetDoNotAllowPads(False); ka.SetDoNotAllowFootprints(False)
        ka.SetLayerSet(pcbnew.LSET.AllCuMask())
        ol = ka.Outline(); ol.NewOutline()
        for (px, py) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            ol.Append(MM(px), MM(py))
        brd.Add(ka)

    # connectivity graph (signal nets only)
    adj = collections.defaultdict(collections.Counter)
    net_members = collections.defaultdict(set)
    for ref, (fp, p) in fps.items():
        for pins in p["units"].values():
            for net in pins.values():
                if net and net not in board.power_nets and not net.startswith("SPARE_"):
                    net_members[net].add(ref)
    for net, mem in net_members.items():
        if len(mem) > 12:
            continue
        for a in mem:
            for b in mem:
                if a != b:
                    adj[a][b] += 1

    by_block = collections.OrderedDict()
    for ref, (fp, p) in fps.items():
        if ref in board.fixed:
            continue
        by_block.setdefault(p["block"], []).append(ref)

    def area(ref):
        x1, y1, x2, y2 = courtyard(fps[ref][0])
        return (x2 - x1) * (y2 - y1)

    clusters = []
    for block, refs in by_block.items():
        start = max(refs, key=area)
        order, seen, queue = [], {start}, [start]
        while queue or len(order) < len(refs):
            if not queue:
                rest = [r for r in refs if r not in seen]
                nxt = max(rest, key=area); seen.add(nxt); queue.append(nxt)
            cur = queue.pop(0)
            order.append(cur)
            for nb, _ in adj[cur].most_common():
                if nb in refs and nb not in seen:
                    seen.add(nb); queue.append(nb)
        # shelf pack the cluster (several widths, tried in order at placement time)
        tot = sum(area(r) for r in refs)
        base = cluster_w or max(22.0, min(W - 8, math.sqrt(tot * 2.2)))
        minw = max(courtyard(fps[r][0])[2] - courtyard(fps[r][0])[0] for r in refs) + gap
        variants = []
        mults = (1.0,) if not getattr(board, "shape", None) else (1.0, 0.75, 1.35, 0.55, 1.8, 0.4, 2.5)
        for m in mults:
            cw = max(base * m, minw)
            local, x, y, sh = {}, 0.0, 0.0, 0.0
            for r in order:
                fp = fps[r][0]
                fp.SetOrientationDegrees(0)
                fp.SetPosition(pcbnew.VECTOR2I(0, 0))
                x1, y1, x2, y2 = courtyard(fp)
                w, h = x2 - x1 + gap, y2 - y1 + gap
                if x + w > cw and x > 0:
                    y += sh; x = 0.0; sh = 0.0
                local[r] = (x - x1, y - y1)
                x += w; sh = max(sh, h)
            variants.append((local, cw, y + sh))
        clusters.append((block, variants))

    # place clusters on the board: shelf pack avoiding occupied rectangles
    usable = shape.CloneDropTriangulation()
    usable.Deflate(MM(getattr(board, "place_margin", 3.0)), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, MM(0.05))
    RES = 0.5
    NX, NY = int(W / RES) + 2, int(H / RES) + 2
    mask = None
    if getattr(board, "shape", None):
        mask = [bytearray(NX) for _ in range(NY)]
        for j in range(NY):
            row = mask[j]
            for i in range(NX):
                if usable.Contains(pcbnew.VECTOR2I(MM(i * RES), MM(j * RES))):
                    row[i] = 1

    def inside(rx1, ry1, rx2, ry2):
        i1, i2 = int(rx1 / RES), int(rx2 / RES) + 1
        j1, j2 = int(ry1 / RES), int(ry2 / RES) + 1
        if i1 < 0 or j1 < 0 or i2 >= NX or j2 >= NY:
            return False
        for j in range(j1, j2 + 1):
            if 0 in mask[j][i1:i2 + 1]:
                return False
        return True

    def free(rx1, ry1, rx2, ry2):
        if rx1 < 3.5 or ry1 < 3.5 or rx2 > W - 3.5 or ry2 > H - 3.5:
            return False
        for (a, b, c, d) in occupied:
            if rx1 < c + gap and rx2 > a - gap and ry1 < d + gap and ry2 > b - gap:
                return False
        if mask is not None and not inside(rx1, ry1, rx2, ry2):
            return False
        return True

    unplaced = []
    step = 1.0
    if getattr(board, "shape", None):
        clusters.sort(key=lambda c: -max(max(v[1] - 0, 0) * v[2] for v in c[1]) if False else -min(v[1] * v[2] for v in c[1]))
    for block, variants in clusters:
        spot = None
        pref = board.block_pref.get(block) if hasattr(board, "block_pref") else None
        for local, cw, ch in variants:
            ys = [round(v, 1) for v in frange(3.5, H - ch, step)]
            xs = [round(v, 1) for v in frange(3.5, W - cw, step)]
            if pref:
                px, py = pref
                cands = sorted(((x, y) for y in ys for x in xs), key=lambda c: (c[0] - px) ** 2 + (c[1] - py) ** 2)
            else:
                cands = ((x, y) for y in ys for x in xs)
            for (x, y) in cands:
                if free(x, y, x + cw, y + ch):
                    spot = (x, y); break
            if spot:
                break
        if spot is None:
            unplaced.append(block)
            continue
        for r, (lx, ly) in local.items():
            fps[r][0].SetPosition(pcbnew.VECTOR2I(MM(spot[0] + lx), MM(spot[1] + ly)))
        occupied.append((spot[0], spot[1], spot[0] + cw, spot[1] + ch))

    brd.BuildConnectivity()
    pcbnew.SaveBoard(out_path, brd)
    return unplaced


def outline_poly(board):
    """SHAPE_POLY_SET of the board: rectangle, or board.shape = dict(circle=(cx, cy, r), clip=(x0, y0, x1, y1),
    cutouts=[("circle", x, y, r) | ("rect", x0, y0, x1, y1)]) in mm (KiCad coordinates)."""
    W, H = board.outline
    sp = getattr(board, "shape", None)

    def rect(x0, y0, x1, y1):
        ps = pcbnew.SHAPE_POLY_SET(); ps.NewOutline()
        for (x, y) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            ps.Append(MM(x), MM(y))
        return ps

    def circle(cx, cy, r, n=180):
        ps = pcbnew.SHAPE_POLY_SET(); ps.NewOutline()
        for i in range(n):
            a = 2 * math.pi * i / n
            ps.Append(MM(cx + r * math.cos(a)), MM(cy + r * math.sin(a)))
        return ps

    if not sp:
        return rect(0, 0, W, H)
    poly = circle(*sp["circle"]) if "circle" in sp else rect(0, 0, W, H)
    if "clip" in sp:
        poly.BooleanIntersection(rect(*sp["clip"]))
    for c in sp.get("cutouts", []):
        poly.BooleanSubtract(circle(*c[1:], n=72) if c[0] == "circle" else rect(*c[1:]))
    poly.Simplify()
    return poly


def frange(a, b, s):
    v = a
    while v <= b:
        yield v
        v += s


def sync_values(board, pcb_path):
    """Update values and fields of an already placed/routed board from the design (no connectivity change)."""
    brd = pcbnew.LoadBoard(pcb_path)
    parts = {p["ref"]: p for p in board.parts}
    n = 0
    for fp in brd.GetFootprints():
        p = parts.get(fp.GetReference())
        if not p:
            continue
        if fp.GetValue() != p["value"]:
            fp.SetValue(p["value"]); n += 1
        for k, v in p["props"].items():
            if k == "DNP":
                continue
            try:
                fld = fp.GetFieldByName(k)
            except Exception:
                fld = None
            if fld is None:
                fld = pcbnew.PCB_FIELD(fp, pcbnew.FIELD_T_USER, k); fld.SetVisible(False); fld.SetLayer(pcbnew.F_Fab); fp.Add(fld)
            fld.SetText(str(v))
    pcbnew.SaveBoard(pcb_path, brd)
    print("values changed:", n)
