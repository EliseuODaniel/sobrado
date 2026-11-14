"""Preservar os rascunhos v05: conferir o temporário antes de promover."""
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from industrial_bar_policy import bar_fridges, remove_bar_fridges
from industrial_photoreal_data import sha
from residence07_industrial import geometry_fingerprint

REPORT=ROOT/'relatorios/industrial-v06'
FOLDER=ROOT/'historico/rascunhos/industrial-v05'
receipt=REPORT/'rascunhos-industriais-sem-geladeira.json'
rows=json.loads(receipt.read_text())


def fingerprints():return {o.name:geometry_fingerprint(o) for o in bpy.data.objects}


def preserve_and_verify(path, expected, count):
    # Bibliotecas/cenas sem usuário efetivo precisam de retenção explícita.
    for scene in bpy.data.scenes:scene.use_fake_user=True
    for collection in bpy.data.collections:collection.use_fake_user=True
    bpy.context.window.scene=next(iter(bpy.data.scenes))
    temporary=path.with_name(path.stem+'.verificado.blend')
    assert not temporary.exists()
    bpy.ops.wm.save_as_mainfile(filepath=str(temporary),compress=True)
    bpy.ops.wm.open_mainfile(filepath=str(temporary))
    assert fingerprints()==expected
    assert len(bpy.data.scenes)==count and not bar_fridges()
    temporary.replace(path)
    return sha(path)


r2=FOLDER/'previa02.blend'
previous=next((row for row in rows if row['file']==str(r2.relative_to(ROOT))),None)
assert sha(r2)==(previous['after_sha256'] if previous else '7c3930291dd1f7b1cc94e0d1803ebc43f3069951da3567cff2c570b6412cb144')
bpy.ops.wm.open_mainfile(filepath=str(r2))
removed_family={o for root in bar_fridges() for o in [root,*root.children_recursive]}
expected={o.name:geometry_fingerprint(o) for o in bpy.data.objects if o not in removed_family}
removed=previous['removed'] if previous else remove_bar_fridges()
assert len(removed)==6 and fingerprints()==expected and not bar_fridges()
r2_hash=sha(r2) if previous else preserve_and_verify(r2,expected,25)
if not previous:rows.append({'file':str(r2.relative_to(ROOT)), 'before_sha256':'7c3930291dd1f7b1cc94e0d1803ebc43f3069951da3567cff2c570b6412cb144',
             'after_sha256':r2_hash,'removed':removed,'non_bar_geometry_unchanged':True,'verified_after_reopen':True,
             'presentation_scenes_verified':25,'retention_flags_explicit':True,'images':[]})
receipt.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print('DRAFT_V05_R2_PRESERVED',len(expected),25,flush=True)

r1=FOLDER/'previa01.blend'
assert sha(r1)=='f9c5fa1a40e55fb6fb6a2ca706f82bb300a3815fb6c8cea62adb23cbccfc9441'
bpy.ops.wm.open_mainfile(filepath=str(r1))
original=fingerprints(); assert len(original)==2225 and not bar_fridges()
meta=json.loads(r1.with_suffix('.json').read_text()); meta2=json.loads(r2.with_suffix('.json').read_text())
assert meta['jobs']==meta2['jobs'] and meta['config_sha256']==meta2['config_sha256']
assert all(original.get(n)==h for n,h in meta['protected_geometry'].items())
# Recuperar a organização da revisão seguinte, com mesmas 25 câmeras documentadas.
# Remapear cada ID já existente para preservar os móveis, luzes e materiais da R1.
kinds=['objects','collections','materials','worlds','images','meshes','curves','lights','cameras']
existing={kind:dict(getattr(bpy.data,kind).items()) for kind in kinds}
with bpy.data.libraries.load(str(r2),link=False) as (source,target):
    names={kind:list(getattr(source,kind)) for kind in kinds}
    scene_names=list(source.scenes);target.scenes=list(scene_names)
    for kind in kinds:setattr(target,kind,list(names[kind]))
imported={kind:dict(zip(names[kind],getattr(target,kind))) for kind in kinds}
restored_cameras=[]
for kind in kinds:
    for name,new in imported[kind].items():
        if name in existing[kind]:
            old=existing[kind][name]
            if new!=old:new.user_remap(old)
        elif new:
            new.name=name
            if kind=='objects' and new.type=='CAMERA':restored_cameras.append(name)
# Remover somente duplicatas importadas, nunca os IDs retidos da primeira revisão.
for kind in kinds:
    ids=getattr(bpy.data,kind)
    for name,new in imported[kind].items():
        if name not in existing[kind] or new==existing[kind][name]:continue
        new.use_fake_user=False
        ids.remove(new,do_unlink=True)
for scene in list(bpy.data.scenes):
    if scene.name not in scene_names:bpy.data.scenes.remove(scene)
assert len(restored_cameras)==25
for job in meta['jobs']:
    scene=bpy.data.scenes[job['scene']];camera=scene.camera
    assert camera and (camera.location-Vector(job['pos'])).length<1e-5
    scene.render.filepath=str(ROOT/job['file'])
expected=fingerprints()
assert all(expected.get(n)==h for n,h in original.items())
assert set(expected)==set(original)|set(restored_cameras)
r1_hash=preserve_and_verify(r1,expected,25)
assert all(geometry_fingerprint(bpy.data.objects[n])==h for n,h in meta['protected_geometry'].items())
rows.append({'file':str(r1.relative_to(ROOT)), 'before_sha256':'97c99f83740d085ab638f8ab475fa52f3105f781be9b175b245f6625d5b92642',
             'after_sha256':r1_hash,'removed':removed,'non_bar_geometry_unchanged':True,'verified_after_reopen':True,'images':[],
             'presentation_scenes_verified':25,'restored_cameras':restored_cameras,
             'recovery':{'reason':'O primeiro salvamento descartou referências de cenas/coleções sem usuário efetivo. Detectado na reabertura.',
                         'layout_source':str(r2.relative_to(ROOT)),'layout_source_sha256':r2_hash,
                         'same_documented_jobs_and_config':True,'retained_object_fingerprints_verified':len(original),
                         'protected_fingerprints_verified':len(meta['protected_geometry']),
                         'note':'25 cenas/câmeras e suas coleções restauradas da revisão seguinte. Objetos, materiais e luzes retidos da R1 remapeados sem substituir sua geometria.'}})
rows.sort(key=lambda row:row['file'])
receipt.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print('DRAFT_V05_R1_RECOVERED',len(expected),25,'ALL_ARCHIVE_MODELS',len(rows),flush=True)
