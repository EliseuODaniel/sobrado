"""Verifica o nativo v04 em processo limpo, sem render ou alteração do modelo."""
import json
from pathlib import Path
import sys

import bpy

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import refine_industrial as design


def main():
    model=design.validate()
    assert not bpy.data.libraries
    assert bpy.context.scene.name=='DESIGN_Sala_Integrada'
    images=[im for im in bpy.data.images if im.source=='FILE']
    assert images and all(im.packed_file for im in images)
    chairs=[o for o in bpy.data.objects if o.name.startswith('DESIGN Cadeira jantar ')]
    assert len(chairs)==4 and all(not o.hide_render for o in chairs)
    expected=[(.82,5.30),(.82,6.30),(2.22,5.30),(2.22,6.30)]
    assert sorted((round(o.location.x,2),round(o.location.y,2)) for o in chairs)==sorted(expected)
    assert all(o.hide_render for o in bpy.data.objects if o.name.startswith('HQ cadeira jantar'))
    assert len([o for o in bpy.data.objects if o.name.startswith('DESIGN Assento couro')])==3
    assert len([o for o in bpy.data.objects if o.name.startswith('DESIGN Encosto couro')])==3
    assert not bpy.data.objects['PHOTO Almofadas beliche 0.46'].hide_render
    assert not bpy.data.objects['PHOTO Almofadas beliche 1.48'].hide_render
    for name in ['DESIGN Manta com caída','DESIGN Painel TV arredondado']:
        assert bpy.data.objects[name].data.uv_layers
    assert bpy.data.objects['Painel TV branco'].hide_render
    scenes={}
    world=None
    for job in design.CFG['jobs']:
        scene=bpy.data.scenes[job['scene']]
        assert 'DESIGN04' in scene.collection.children
        assert scene.render.engine=='CYCLES' and scene.render.resolution_percentage==100
        assert [scene.render.resolution_x,scene.render.resolution_y]==design.CFG['resolution']
        assert scene.cycles.samples==design.CFG['samples'] and scene.cycles.use_light_tree
        assert scene.camera and scene.camera.data.dof.focus_object
        if 'position' in job:
            assert all(abs(scene.camera.location[i]-job['position'][i])<1e-5 for i in range(3))
            assert abs(scene.camera.data.lens-job['lens'])<1e-5
        if world is None:world=scene.world
        assert scene.world==world
        scenes[scene.name]={'camera':scene.camera.name,'resolution':[scene.render.resolution_x,scene.render.resolution_y],
            'samples_max':scene.cycles.samples,'light_tree':True,'world':world.name}
    for item in model['new_assets']:
        path=ROOT/item['path'];assert design.prior.sha(path)==item['sha256']
    previous=json.loads((ROOT/'relatorios/industrial-v03/modelo.json').read_text())
    assert model['base_sha256']==previous['blend_sha256']
    data={'timestamp_utc':design.stamp(),'blend_sha256':model['blend_sha256'],'base_sha256':model['base_sha256'],
        'blender_version':bpy.app.version_string,'geometry_compared':len(model['geometry_before']),
        'packed_file_images':len(images),'external_libraries':[],'dining_chairs_visible':4,
        'sofa_seats':3,'bedroom_pillows_preserved':True,'scenes':scenes,'all_passed':True}
    (design.REPORT/'recursos-nativos.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print('DESIGN_RESOURCE_AUDIT_PASSED',len(images),'packed images; 4 chairs; 3 sofa seats')


if __name__=='__main__':main()
