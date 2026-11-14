"""Caixa no canto posterior direito junto à escada, janela livre."""
from pathlib import Path
import sys,json,math,hashlib
import bpy
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from residence07_attic_roof import ceiling_z
OUT=ROOT/'renders/atico';OUT.mkdir(parents=True,exist_ok=True)
DEST=ROOT/'projeto/atico/atico-caixa-canto-escada.blend'
assert not DEST.exists(),DEST
source=Path(bpy.data.filepath);sha=hashlib.sha256(source.read_bytes()).hexdigest()
old=Vector((2.8,5,5.45));new=Vector((5.1,5.1,5.45))
transform=Matrix.Translation(new)@Matrix.Diagonal((1.52/1.8,1.52/1.8,.97/1.185,1))@Matrix.Translation(-old)
for obj in bpy.data.collections['ATC_Reservatorio'].objects:
 obj.matrix_world=transform@obj.matrix_world
 obj['position_source']='Estudo no canto posterior direito ao lado da escada; X=5,10 Y=5,10 base=5,45 m'
 obj['envelope_status']='Envelope de referência Fortlev 1000 L: diâmetro 1,52 m, altura total 0,97 m; produto real não levantado'
# Armário baixo sai do canto ocupado pela caixa.
for obj in bpy.data.collections['ATC_Mobiliario'].objects:
 if 'Armario baixo' in obj.name and obj.location.y>3:obj.location.x=.55
# A antiga circunferência de 60 cm não é válida neste canto.
for obj in list(bpy.data.collections['PROPOSTA_Reserva_Manutencao'].objects):bpy.data.objects.remove(obj,do_unlink=True)
bpy.context.view_layer.update()
tank=[o for o in bpy.data.collections['ATC_Reservatorio'].objects if o.get('capacity_liters')][0]
pts=[tank.matrix_world@Vector(p) for p in tank.bound_box]
lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
assert abs(hi[0]-lo[0]-1.52)<1e-4
assert abs(hi[2]-lo[2]-.97)<1e-4
assert lo[0]>4.0,'Caixa deve ficar fora da faixa horizontal da janela central'
assert lo[1]>4.15,'Caixa deve ficar fora do vão da escada'
assert hi[0]<6.25 and hi[1]<7.2
samples=[(new.x+.76*math.cos(i*math.tau/720),new.y+.76*math.sin(i*math.tau/720)) for i in range(720)]
roofgap=min(ceiling_z(x,y)-hi[2] for x,y in samples)
assert roofgap>0,roofgap
furniture={}
for obj in bpy.data.collections['ATC_Mobiliario'].objects:
 p=[obj.matrix_world@Vector(v) for v in obj.bound_box]
 a=[min(v[i] for v in p) for i in range(3)];b=[max(v[i] for v in p) for i in range(3)]
 gap=math.hypot(max(a[0]-new.x,0,new.x-b[0]),max(a[1]-new.y,0,new.y-b[1]))-.76
 assert gap>0,(obj.name,gap)
 furniture[obj.name]=round(gap,3)
scenes=[]
for suffix in ['perspectiva-frontal','perspectiva-posterior']:
 s=bpy.data.scenes['ATICO_TRANSPARENTE_'+suffix];s.render.filepath=str(OUT/(suffix+'.png'));scenes.append(s)
s=bpy.data.scenes['CAIXA_LATERAL_Planta'];s.render.filepath=str(OUT/'planta-superior.png');scenes.append(s)
for s in scenes:
 s['tank_proposal']='Canto posterior direito junto à escada, fora da faixa da janela. Manutenção, estrutura e hidráulica pendentes.'
 s.cycles.samples=32
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='CUDA';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='CUDA'
for s in scenes:s.cycles.device='GPU' if any(d.type=='CUDA' for d in prefs.devices) else 'CPU'
bpy.context.window.scene=scenes[0]
bpy.ops.wm.save_as_mainfile(filepath=str(DEST),compress=True)
record={'center_xyz':list(new),'reference_dimensions_m':[1.52,1.52,.97],'capacity_l':1000,'reference_product':'https://www.fortlev.com.br/produtos/reservatorios/caixa-dagua-de-polietileno-1000l/','window_horizontal_clearance_m':round(lo[0]-4,3),'stair_rear_clearance_m':round(lo[1]-4.15,3),'party_wall_clearance_m':round(6.25-hi[0],3),'ceiling_gap_above_tank_m':round(roofgap,3),'maintenance_60cm_all_around':False,'status':'Estudo de posição: cabe no envelope e libera a janela; não aprovado para instalação, manutenção ou estrutura. Confirmar caixa real, acesso e tubulações.','furniture_clearances_m':furniture,'source_sha256':sha}
(OUT/'verificacao.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
for s in scenes:
 bpy.context.window.scene=s;bpy.ops.render.render(write_still=True,scene=s.name)
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
print('CAIXA_CANTO_OK',record,flush=True)
