"""Renderizar ângulos de comparação e plantas a partir do arquivo revisado salvo."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from blender_primitives import configure_device


def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=Path('.'));p.add_argument('--preview',action='store_true');p.add_argument('--ground-only',action='store_true');p.add_argument('--facade-only',action='store_true');p.add_argument('--device',choices=['cpu','auto'],default='cpu');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    root=args.project_root.resolve();file=Path(bpy.data.filepath);original=hashlib.sha256(file.read_bytes()).hexdigest();device=configure_device(args.device)
    cfg=json.loads((root/'config/planta-casa.json').read_text());revision=f"revisao-{cfg.get('revision_number',2):02d}"
    jobs=[('FOTO_Sala_Fundos','sala-fundos.png'),('FOTO_Sala_Frente','sala-frente.png'),('FOTO_Detalhe_Escada','escada-acesso.png'),('FOTO_Cozinha','cozinha.png'),('FOTO_Cozinha_Reversa','cozinha-reversa.png'),('FOTO_Bar','bar.png')]
    facade_jobs=[('FOTO_Fachada','fachada-frontal.png'),('FOTO_Fachada_Obliqua','fachada-obliqua.png')]
    if cfg.get('revision_number',2)>=5:jobs=facade_jobs+jobs+[('FOTO_Lavanderia','lavanderia.png'),('FOTO_Lavabo','lavabo.png')]
    if args.facade_only:jobs=facade_jobs
    if args.ground_only:jobs=[('PLANTA_Terreo','terreo-3d.png'),('PLANTA_Terreo_Cotas','planta-terreo.png'),('PLANTA_Terreo_Portas','porta-lavabo.png')]
    elif not args.preview and not args.facade_only:jobs += [('PLANTA_Terreo','terreo-3d.png'),('PLANTA_Terreo_Cotas','planta-terreo.png'),('PLANTA_Terreo_Portas','porta-lavabo.png'),('PLANTA_Superior','superior-pendente.png'),('PLANTA_Superior_Cotas','superior-envoltoria.png'),('ESTUDOS_Superior','estudos-superior.png'),('CASA_Completa','volumetria.png')]
    if not args.preview and not args.facade_only and cfg.get('revision_number',2)>=4:jobs.append(('CORTE_Lavabo_Escada','lavabo-sob-escada.png'))
    outputs=[]
    for name,target in jobs:
        scene=bpy.data.scenes[name];scene.cycles.device='GPU' if device['backend']=='OPTIX' else 'CPU';scene.cycles.samples=16 if args.preview else 64;scene.render.resolution_percentage=50 if args.preview else 100
        folder=root/'renders/atual'/('previas' if args.preview else '');folder.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(folder/target)
        bpy.ops.render.render(write_still=True,scene=name);outputs.append(str(Path(scene.render.filepath).relative_to(root)));print('REVISION_RENDER',name,flush=True)
    assert hashlib.sha256(file.read_bytes()).hexdigest()==original
    report={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'blend':str(file.relative_to(root)),'sha256':original,'version':bpy.app.version_string,'preview':args.preview,'device':device,'outputs':outputs,'saved_file_unchanged':True}
    (root/'relatorios/atual'/('renders-previa.json' if args.preview else 'renders-finais.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
