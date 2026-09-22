import sys, pcbnew, collections
brd = pcbnew.LoadBoard(sys.argv[1])
brd.BuildConnectivity()
conn = brd.GetConnectivity()
c = collections.Counter()
for net in brd.GetNetsByName().values() if hasattr(brd, "GetNetsByName") else []:
    pass
for ni in range(1, brd.GetNetCount()):
    n = conn.GetUnconnectedCount(False) if False else None
items = []
for pad in brd.GetPads():
    pass
# use ratsnest per net
for code, net in brd.GetNetsByNetcode().items():
    if code <= 0:
        continue
    try:
        r = conn.GetRatsnestForNet(code)
    except Exception:
        r = None
    if r is None:
        continue
    edges = [e for e in r.GetEdges() if not e.IsVisible() is False]
    cnt = sum(1 for e in r.GetEdges())
    if cnt:
        c[net.GetNetname()] = cnt
print(dict(c))
