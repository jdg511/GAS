"""Sanity check: parse the generated drawio and prove no two boxes overlap."""
import xml.etree.ElementTree as ET

SRC = r"C:\Users\Jason\GAS-build\repo\hardware\gas-revc-signal-paths.drawio"
root = ET.parse(SRC).getroot()

bad = 0
for dia in root.findall("diagram"):
    name = dia.get("name")
    boxes = []
    for cell in dia.iter("mxCell"):
        if cell.get("vertex") != "1":
            continue
        g = cell.find("mxGeometry")
        x, y = float(g.get("x", 0)), float(g.get("y", 0))
        w, h = float(g.get("width", 0)), float(g.get("height", 0))
        boxes.append((cell.get("value", "")[:34].replace("&#10;", " / "), x, y, w, h))
    hits = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if (a[1] < b[1] + b[3] and b[1] < a[1] + a[3]
                    and a[2] < b[2] + b[4] and b[2] < a[2] + a[4]):
                hits.append((a[0], b[0]))
    print("%-22s %3d boxes, %d overlapping pairs" % (name, len(boxes), len(hits)))
    for h in hits:
        print("      OVERLAP:", h[0], "<->", h[1])
    bad += len(hits)

print("total overlapping pairs:", bad)
