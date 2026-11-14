"""Extrai uma biblioteca de cobertura/forro sem propostas de acesso ao ático."""
import argparse
import json
from pathlib import Path
import sys

import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
import residence07_geometry as geo
from residence07_industrial import geometry_fingerprint

COLLECTIONS=['ATC3_Cobertura','ATC3_Fachadas_Mansardas','ATC3_Janelas','ATC3_Detalhes','ATC_Oitoes',
    'ATC4_Forro','ATC4_Forro_Fixacao','ATUAL_Fundos','ATUAL_Cobertura_Fundos','R07_Contexto',
    'ATC3_Cobertura_Transparente','ATC3_Fachadas_Transparentes','ATC_Oitoes_Transparentes',
    'ATC4_Forro_Transparente','ATC4_Cobertura_Corte','ATC4_Forro_Corte','ATC_Reservatorio',
    'ATC_Mobiliario','R07_Iluminacao']


def main(dest):
    dest=Path(dest).resolve();assert not dest.exists(),dest
    original=Path(bpy.data.filepath);original_hash=geo.sha(original)
    before={o.name:geometry_fingerprint(o) for name in COLLECTIONS for o in bpy.data.collections[name].all_objects}
    old=bpy.data.collections['ATUAL_Arquitetura']
    for obj in list(old.objects):bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.collections.remove(old)
    current=geo.ROOT/'arquivos/versoes-anteriores-2026-11-14/projeto/residencia-07-atual/casa-07-atual.blend'
    with bpy.data.libraries.load(str(current),link=False) as (src,dst):dst.collections=['ATUAL_Arquitetura']
    body=dst.collections[0]
    # Materiais de degraus/guardas são componentes, não propostas de geometria.
    for name in ['ATC4 Granito','ATC4 Branco','ATC4 Metal','ATC4 Percurso','ATC4 Faixa alta','ATC4 Faixa baixa']:
        if name in bpy.data.materials:bpy.data.materials[name].use_fake_user=True
    scene=bpy.data.scenes.new('BIBLIOTECA_Cobertura_Forro_Sem_Acesso_Atico')
    scene.world=bpy.data.worlds.get('R07 Ceu diurno')
    for name in COLLECTIONS:scene.collection.children.link(bpy.data.collections[name])
    scene.collection.children.link(body)
    bpy.context.window.scene=scene
    for oldscene in list(bpy.data.scenes):
        if oldscene!=scene:bpy.data.scenes.remove(oldscene)
    bpy.ops.outliner.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
    assert not any('U Piso' in o.name or 'V05 Piso' in o.name or 'helicoidal' in o.name or 'Degrau novo' in o.name for o in bpy.data.objects)
    after={o.name:geometry_fingerprint(o) for name in COLLECTIONS for o in bpy.data.collections[name].all_objects}
    assert after==before
    assert len([o for o in body.objects if o.get('stair_index')])==16
    dest.parent.mkdir(parents=True,exist_ok=True);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
    assert geo.sha(original)==original_hash
    record={'file':str(dest.relative_to(geo.ROOT)),'sha256':geo.sha(dest),'original_library_file':str(original.relative_to(geo.ROOT)),
        'original_sha256':original_hash,'preserved_geometry':before,'no_attic_access_objects':True,
        'scope':'Biblioteca de cobertura, forro, mobiliário e reservatório; apenas a escada original da casa, sem acesso antigo ao ático.'}
    (geo.ROOT/'arquivos/versoes-anteriores-2026-11-14/relatorios/limpeza-escadas/base-sem-acesso.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print('ATTIC_SOURCE_OK',len(before),'objetos; nenhuma escada de ático')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);main(a.output)
