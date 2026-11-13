import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
import residence07_build as b
import residence07_geometry as g
source=ROOT/"projeto/fontes/mobiliario-industrial.blend"
before=g.sha(source)
count=b.prepare()
assert count>0 and g.sha(source)==before
(ROOT/"relatorios/industrial-v06/biblioteca-reuso-base.json").write_text(json.dumps({"source":str(source.relative_to(ROOT)),"sha256":before,"reused_objects":count,"prepare_completed":True,"source_unchanged":True,"native_save_operation":False},indent=2)+"\n")
print("BASE_LIBRARY_PREPARE_OK",count)
