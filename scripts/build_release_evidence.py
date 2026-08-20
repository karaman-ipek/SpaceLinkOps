import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/"src"))
controlled=[root/"requirements/requirements.yaml",root/"pyproject.toml",*sorted((root/"scenarios").glob("*.yaml")),*sorted((root/"src/spacelinkops").glob("*.py")),*sorted((root/"tests").glob("*.py"))]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
try:revision=subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip()
except (subprocess.CalledProcessError, FileNotFoundError):revision="UNAVAILABLE"
try:
    from spacelinkops.validation import summary as _validation_summary
    frame_validation=_validation_summary()
except (ImportError, RuntimeError, ValueError) as exc:
    frame_validation={"error":str(exc)}
manifest={"generated_utc":datetime.now(UTC).isoformat(),"revision":revision,"safety_boundary":"OFFLINE_SIMULATOR_ONLY","frame_validation":frame_validation,"files":[{"path":str(p.relative_to(root)),"sha256":sha(p)} for p in controlled]}
out=root/"outputs/release_evidence.json";out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(manifest,indent=2)+"\n");print(out)
