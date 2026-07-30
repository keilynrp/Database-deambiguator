"""Prove the 6.2 parity gate can fail: break one format at a time, run, revert.

A gate that passes the moment it is written has proven nothing about the system —
only that the assertion is satisfiable. Each mutation below removes exactly the
element the contract requires, and the gate must catch it.
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path("D:/universal-knowledge-intelligence-platform")

MUTATIONS = [
    (
        "html: drop the method footer",
        "backend/reporting/html_renderer.py",
        '+ f\'\\n    <p class="method">{escape(section.method)}</p>\\n</section>\'',
        "+ '\\n</section>'",
        "html",
    ),
    (
        "html: title the section with the label instead of the takeaway",
        "backend/reporting/html_renderer.py",
        'f"\\n    <h2>{escape(section.takeaway)}</h2>\\n    "',
        'f"\\n    <h2>{escape(section.title)}</h2>\\n    "',
        "html",
    ),
    (
        "excel: drop the caveat row above tables",
        "backend/reporting/excel_renderer.py",
        "        if isinstance(block, Table):\n            row = _write_caveat(ws, section.method, row)\n",
        "",
        "excel",
    ),
    (
        "excel: sheet no longer opens with the finding",
        "backend/reporting/excel_renderer.py",
        "takeaway = ws.cell(row=1, column=1, value=section.takeaway)",
        "takeaway = ws.cell(row=1, column=1, value=section.title)",
        "excel",
    ),
    (
        "pptx: drop the speaker notes",
        "backend/reporting/pptx_renderer.py",
        "    slide.notes_slide.notes_text_frame.text = (\n"
        '        f"{section.title}\\n\\n{section.takeaway}\\n\\n{section.method}"\n'
        "    )",
        "    pass",
        "pptx",
    ),
    (
        "pptx: title the slide with the label instead of the takeaway",
        "backend/reporting/pptx_renderer.py",
        "    _text(slide, section.takeaway, Inches(0.5), Inches(0.34)",
        "    _text(slide, section.title, Inches(0.5), Inches(0.34)",
        "pptx",
    ),
]

failures = []
for name, rel, old, new, fmt in MUTATIONS:
    path = ROOT / rel
    original = path.read_text(encoding="utf-8")
    if original.count(old) != 1:
        print(f"SKIP  {name}: anchor matched {original.count(old)} times")
        continue
    path.write_text(original.replace(old, new), encoding="utf-8")
    try:
        proc = subprocess.run(
            [str(ROOT / ".venv/Scripts/python"), "-m", "pytest",
             "backend/tests/test_report_parity_guard.py",
             "-q", "-k", f"finding_and_its_method and {fmt}", "--no-header", "-p", "no:cacheprovider"],
            cwd=ROOT, capture_output=True, text=True,
        )
        tail = [ln for ln in proc.stdout.splitlines() if "passed" in ln or "failed" in ln]
        caught = proc.returncode != 0
        print(f"{'CAUGHT' if caught else 'MISSED'}  {name}\n        {tail[-1] if tail else proc.stdout[-120:]}")
        if not caught:
            failures.append(name)
    finally:
        path.write_text(original, encoding="utf-8")

print()
print("gate has teeth for every mutation" if not failures else f"GATE BLIND TO: {failures}")
sys.exit(1 if failures else 0)
