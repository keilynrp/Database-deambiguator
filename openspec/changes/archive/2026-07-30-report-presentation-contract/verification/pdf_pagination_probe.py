"""7.2, second pass — is a late method orphaned, or does it follow its own content?

The first pass compared the method's page against its section's *heading*, which
is the wrong question: a section longer than a page legitimately spans pages, and
a caveat on the same page as the section's spilled-over table is still adjacent to
the figures it qualifies. What would be a real defect is a caveat alone on a page,
or on a page carrying none of its own section's content.
"""
import json

from weasyprint import HTML

MARKERS = {
    "exhibit-label": "eyebrow",
    "method": "method",
    "summary-list": "summary",
    "grid": "stats",
    "callout": "prose",
    "bar-wrap": "meter",
}


def collect(box, page_no, out):
    element = getattr(box, "element", None)
    if element is not None:
        classes = set((element.get("class") or "").split())
        for cls, kind in MARKERS.items():
            if cls in classes:
                out.append({"kind": kind, "page": page_no, "y": round(box.position_y, 1)})
                break
        else:
            if element.tag == "h2":
                out.append({"kind": "heading", "page": page_no, "y": round(box.position_y, 1)})
            elif element.tag == "table":
                out.append({
                    "kind": "table", "page": page_no,
                    "y": round(box.position_y, 1),
                    "bottom": round(box.position_y + box.height, 1),
                })
    for child in getattr(box, "children", ()) or ():
        collect(child, page_no, out)


doc = HTML(filename="/work/sample_report.html").render()
doc.write_pdf("/work/sample_report.pdf")

raw = []
for i, page in enumerate(doc.pages, start=1):
    collect(page._page_box, i, raw)
    raw.append({"kind": "PAGE_END", "page": i, "y": 9999})

# Collapse the box tree's nested repeats of the same element.
seen, flat = set(), []
for item in raw:
    key = (item["kind"], item["page"], item["y"])
    if key in seen:
        continue
    seen.add(key)
    flat.append(item)

print(json.dumps({"pages": len(doc.pages), "flow": flat}, ensure_ascii=False))
