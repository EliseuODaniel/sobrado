import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/"scripts"))
import residence07_industrial as b
s=bpy.data.scenes["PHOTO6_bar-dia"]
for o in s.objects:
 if o.type!="MESH":continue
 p=b.world(o).translation
 if p.x<1.0 and p.y>7 and p.z>.45:
  print(o.name,"parent",o.parent.name if o.parent else None,"faces",len(o.data.polygons),"loc",list(p))
