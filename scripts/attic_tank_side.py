"""Revisão de estudo: caixa na lateral posterior da escada; fontes preservadas."""
from pathlib import Path
import sys, json, math, hashlib
import bpy
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from residence07_attic_roof import ceiling_z
OUT = ROOT/'arquivos/versoes-anteriores-2026-11-14/renders/atico-caixa-lateral'
DEST = ROOT/'arquivos/versoes-anteriores-2026-11-14/projeto/residencia-07-atico-v05/atico-caixa-lateral-hidraulica.blend'
assert not DEST.exists(), DEST
OUT.mkdir(parents=True, exist_ok=True)
source = Path(bpy.data.filepath)
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
center = Vector((2.8,5.0,5.45))
delta = center-Vector((1.8,3.175,5.45))
for obj in list(bpy.data.collections['ATC_Reservatorio'].objects):
    if obj.type == 'CURVE' and 'Friso' not in obj.name:
        bpy.data.objects.remove(obj, do_unlink=True)
    else:
        obj.location += delta
        obj['position_source'] = 'Proposta lateral posterior esquerda; X=2,80 Y=5,00 base=5,45. Conexões em campo pendentes.'
# Retira o compartimento antigo, liberando a circulação central.
for name in ['ATC5_Tecnica','ATC5_Tecnica_Transparente']:
    for obj in list(bpy.data.collections[name].objects):
        bpy.data.objects.remove(obj, do_unlink=True)
# Mesa gira para a antiga região técnica, sem perder o escritório.
for obj in bpy.data.collections['ATC_Mobiliario'].objects:
    if any(k in obj.name for k in ['Mesa escritorio','Pe mesa','Monitor','Cadeira','Encosto']):
        d = obj.location-Vector((1.55,5.45,0))
        obj.location.x, obj.location.y = 1.05-d.y, 3.15+d.x
        obj.rotation_euler.z += math.pi/2
bpy.context.view_layer.update()
radius = .9
top = 6.635
samples = [(center.x+radius*math.cos(i*math.tau/720),center.y+radius*math.sin(i*math.tau/720)) for i in range(720)]
roof_gap = min(ceiling_z(x,y)-top for x,y in samples)
stair_gap = math.hypot(4.1-center.x,4.15-center.y)-radius
assert stair_gap >= .6 and roof_gap >= .6, (stair_gap,roof_gap)
assert center.y+radius+.6 <= 6.5+1e-8
assert center.x-radius-.6 > 0
# Conferência dos móveis contra o círculo da caixa mais a reserva de manutenção.
furniture_gaps = {}
for obj in bpy.data.collections['ATC_Mobiliario'].objects:
    pts = [obj.matrix_world@Vector(p) for p in obj.bound_box]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    dx = max(lo[0]-center.x,0,center.x-hi[0])
    dy = max(lo[1]-center.y,0,center.y-hi[1])
    gap = math.hypot(dx,dy)-radius
    furniture_gaps[obj.name] = round(gap,3)
    assert gap >= .6, (obj.name,gap)
# Reserva de acesso no piso, apenas como indicação visual.
col = bpy.data.collections.new('PROPOSTA_Reserva_Manutencao')
mat = bpy.data.materials.new('Reserva manutenção âmbar')
mat.diffuse_color = (.8,.37,.04,1)
for i in range(40):
    curve = bpy.data.curves.new('Reserva 60 cm','CURVE');curve.dimensions='3D';curve.bevel_depth=.009
    spline=curve.splines.new('POLY');spline.points.add(1)
    for p,a in zip(spline.points,[i*math.tau/40,(i+.55)*math.tau/40]):
        p.co=(center.x+1.5*math.cos(a),center.y+1.5*math.sin(a),5.43,1)
    obj=bpy.data.objects.new('Reserva manutenção / estudo',curve);col.objects.link(obj);curve.materials.append(mat)
scenes=[]
for suffix in ['perspectiva-frontal','perspectiva-posterior']:
    scene=bpy.data.scenes['ATICO_TRANSPARENTE_'+suffix]
    scene.collection.children.link(col)
    scene.render.filepath=str(OUT/(suffix+'.png'))
    scene.cycles.samples=48
    scene['tank_proposal']='Lateral posterior esquerda; hidráulica e estrutura executivas pendentes.'
    scenes.append(scene)
plan=scenes[0].copy();plan.name='CAIXA_LATERAL_Planta';plan.use_fake_user=True
camera=scenes[0].camera.copy();camera.data=scenes[0].camera.data.copy();plan.collection.objects.link(camera);plan.camera=camera
camera.location=(3.175,3,24);camera.rotation_euler=(0,0,0);camera.data.ortho_scale=10.5
plan.render.filepath=str(OUT/'planta-superior.png');scenes.append(plan)
bpy.context.window.scene=scenes[1]
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='CUDA';prefs.get_devices()
gpu=any(d.type=='CUDA' for d in prefs.devices)
for d in prefs.devices:d.use=d.type=='CUDA'
for scene in scenes:scene.cycles.device='GPU' if gpu else 'CPU'
record={'center_xyz':list(center),'diameter_illustrative_m':1.8,'capacity_l':1000,'clearance_to_stair_corner_m':round(stair_gap,3),'minimum_ceiling_gap_above_tank_m':round(roof_gap,3),'minimum_furniture_gap_m':min(furniture_gaps.values()),'furniture_gaps':furniture_gaps,'source_sha256':source_hash,'status':'Estudo geométrico; conexões reais, pressão, laje e apoios não verificados','source_plan':'HID04.pdf, prancha 04/08, 17/09/2012','pipe_notes':'Entrada 25 mm; alimentação, limpeza e extravasor 32 mm conforme HID04. Não confundir rede 3D aproximada com as-built. Percursos novos ainda não dimensionados.'}
bpy.ops.wm.save_as_mainfile(filepath=str(DEST),compress=True)
for scene in scenes:
    bpy.context.window.scene=scene
    bpy.ops.render.render(write_still=True,scene=scene.name)
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
(OUT/'verificacao.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print('CAIXA_LATERAL_OK',record,flush=True)
