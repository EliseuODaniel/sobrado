"""Fila retomável da casa atual, com cópia verificada e Cycles/OptiX nativo."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
import current_photoreal_data as data

if os.name == 'nt':
    BLENDER=Path(os.environ['ProgramFiles'])/'Blender Foundation/Blender 5.2/blender.exe'
    STAGE=Path(tempfile.gettempdir())/'CasaInteriores/atual-fiel-v02'
else:
    BLENDER=Path('/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe')
    STAGE=Path('/mnt/c/Users/edann/AppData/Local/Temp/CasaInteriores/atual-fiel-v02')

def native(args,m):
    import bpy
    assert data.sha(bpy.data.filepath)==m['blend_sha256']
    assert data.sha(data.CONFIG)==m['config_sha256']
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    assert any(d.type=='OPTIX' for d in prefs.devices)
    for d in prefs.devices:d.use=d.type=='OPTIX'
    job=next(j for j in m['jobs'] if j['id']==args.only)
    s=bpy.data.scenes[job['scene']];bpy.context.window.scene=s;s.cycles.device='GPU'
    s.cycles.samples=data.CFG['preview_samples'] if args.preview else data.CFG['samples']
    s.cycles.adaptive_threshold=.035 if args.preview else data.CFG['adaptive_threshold']
    s.render.resolution_percentage=data.CFG['preview_percentage'] if args.preview else 100
    dest=data.REPORT/'previas'/(job['id']+'.png') if args.preview else data.ROOT/job['file'];dest.parent.mkdir(parents=True,exist_ok=True);s.render.filepath=str(dest)
    start=time.monotonic();bpy.ops.render.render(write_still=True,scene=s.name)
    row={'id':job['id'],'file':dest.relative_to(data.ROOT).as_posix(),'sha256':data.sha(dest),'blend_sha256':m['blend_sha256'],'config_sha256':m['config_sha256'],'backend':'OPTIX','render_script_sha256':data.sha(Path(__file__)),'blender_version':bpy.app.version_string,'platform':'Windows native','preview':args.preview,'resolution':[s.render.resolution_x*s.render.resolution_percentage//100,s.render.resolution_y*s.render.resolution_percentage//100],'samples':s.cycles.samples,'adaptive_threshold':s.cycles.adaptive_threshold,'seconds':round(time.monotonic()-start,2),'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
    (data.REPORT/(job['id']+'-native.json')).write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n');print('CURRENT2_OPTIX_RENDER_OK',job['id'],row['seconds'],flush=True)

def windows(p):
    if os.name == 'nt':
        return str(p.resolve())
    return subprocess.check_output(['wslpath','-w',str(p)],text=True).strip()

def queue(args,m):
    assert m['status']=='validated' and data.sha(data.ROOT/m['blend'])==m['blend_sha256']
    files={m['blend'],'scripts/current_photoreal_data.py','scripts/render_current_photoreal.py','config/atual-fiel-v02.json','relatorios/atual/modelo.json'}
    for relative in files:
        src,dst=data.ROOT/relative,STAGE/relative;dst.parent.mkdir(parents=True,exist_ok=True)
        if not dst.exists() or data.sha(src)!=data.sha(dst):shutil.copy2(src,dst)
        assert data.sha(src)==data.sha(dst)
    selected=set(args.only.split(',')) if args.only else {j['id'] for j in m['jobs']};assert selected<={j['id'] for j in m['jobs']}
    receipt=data.REPORT/('previas.json' if args.preview else 'renders.json');old=json.loads(receipt.read_text()) if receipt.exists() else []
    rows={r['id']:r for r in old if r['blend_sha256']==m['blend_sha256'] and r['config_sha256']==m['config_sha256']}
    order=['sala-foto','cozinha','bar','suite','quarto-frente','quarto-fundos','lavanderia','banheiro-social']
    jobs=sorted(m['jobs'],key=lambda j:order.index(j['id']) if j['id'] in order else 100)
    for j in jobs:
        if j['id'] not in selected:continue
        old=rows.get(j['id'])
        if args.resume and old and (data.ROOT/old['file']).exists() and data.sha(data.ROOT/old['file'])==old['sha256']:continue
        log=data.REPORT/'logs'/(j['id']+('-preview' if args.preview else '')+'.log');log.parent.mkdir(exist_ok=True)
        cmd=[str(BLENDER),'--background',windows(STAGE/m['blend']),'--python-exit-code','1','--python',windows(STAGE/'scripts/render_current_photoreal.py'),'--','--native','--only',j['id']]
        if args.preview:cmd.append('--preview')
        print('CURRENT2_START',j['id'],'preview' if args.preview else 'final',flush=True)
        with log.open('w') as stream:
            p=subprocess.run(cmd,cwd=STAGE,stdout=stream,stderr=subprocess.STDOUT,timeout=1500)
        if p.returncode:print(log.read_text(errors='replace')[-3000:]);raise SystemExit(p.returncode)
        row=json.loads((STAGE/data.CFG['report_directory']/(j['id']+'-native.json')).read_text());assert row['blend_sha256']==m['blend_sha256']
        src,dst=STAGE/row['file'],data.ROOT/row['file'];assert data.sha(src)==row['sha256'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert data.sha(dst)==row['sha256']
        from PIL import Image,ImageStat
        with Image.open(dst) as check_image:
            stats=ImageStat.Stat(check_image.convert('RGB'));assert sum(stats.mean)/3>4 and max(stats.stddev)>3,'Vista escura ou bloqueada: '+j['id']
        rows[row['id']]=row;receipt.write_text(json.dumps(list(rows.values()),ensure_ascii=False,indent=2)+'\n')
        print('CURRENT2_DONE',row['id'],row['seconds'],flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--only');parser.add_argument('--preview',action='store_true');parser.add_argument('--resume',action='store_true');parser.add_argument('--native',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
    m=json.loads((data.REPORT/'modelo.json').read_text())
    (native if args.native else queue)(args,m)
