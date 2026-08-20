"""Requirements traceability and evidence generator."""
from pathlib import Path

import yaml


def build_matrix(root:Path)->list[dict]:
    reqs=yaml.safe_load((root/"requirements/requirements.yaml").read_text())
    rows=[]
    for req in reqs:
        implementations=[x.strip() for x in req["implementation"].split(";")];tests=[x.strip().split("::")[0] for x in req["verification"].split(";")]
        missing=[x for x in implementations+tests if not (root/x).exists()]
        rows.append({**req,"status":"MAPPED" if not missing else "BROKEN","missing":missing})
    return rows
def write_markdown(root:Path,output:Path):
    rows=build_matrix(root);lines=["# Requirements Traceability Matrix","","| ID | Requirement | Implementation | Verification | Status |","|---|---|---|---|---|"]
    lines += [f'| {r["id"]} | {r["text"]} | `{r["implementation"]}` | `{r["verification"]}` | {r["status"]} |' for r in rows]
    output.write_text("\n".join(lines)+"\n",encoding="utf-8");return rows
