from pathlib import Path

from spacelinkops.traceability import write_markdown

root=Path(__file__).resolve().parents[1];rows=write_markdown(root,root/"docs/traceability_matrix.md")
if any(r["status"]!="MAPPED" for r in rows):raise SystemExit("broken traceability")
print(f"Mapped {len(rows)} requirements")
