"""Comparar proporções normalizadas dos ambientes com linhas manuais do croqui."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=Path('.'));p.add_argument('--landmarks',type=Path,required=True);args=p.parse_args()
root=args.project_root.resolve();cfg=json.loads((root/'config/planta-casa.json').read_text());previous=json.loads((root/cfg['previous_delivery']['config']).read_text());landmarks=json.loads((root/args.landmarks).read_text())
assert landmarks['source']==cfg['upper_layout_source']['path']
assert hashlib.sha256((root/landmarks['source']).read_bytes()).hexdigest()==cfg['upper_layout_source']['sha256']
left,right,top,bottom=landmarks['outer_pixel_bounds'];reference={key:[(a-left)/(right-left),(b-left)/(right-left),(c-top)/(bottom-top),(d-top)/(bottom-top)] for key,(a,b,c,d) in landmarks['room_pixel_bounds'].items()}
def compare(config):
    d=config['estimated_dimensions_m'];rows={};depth=d['upper_back_y']-d['upper_front_y']
    for room in config['rooms']:
        if room['level']!=1:continue
        x0,x1,y0,y1=room['bounds'];norm=[x0/d['width'],x1/d['width'],(d['upper_back_y']-y1)/depth,(d['upper_back_y']-y0)/depth]
        rows[room['id']]={'normalized_model':norm,'normalized_sketch':reference[room['id']],'max_edge_difference_fraction':max(abs(a-b) for a,b in zip(norm,reference[room['id']])),'approximate_clear_size_m':[x1-x0-d['wall_thickness'],y1-y0-d['wall_thickness']]}
    return {'rooms':rows,'max_edge_difference_fraction':max(row['max_edge_difference_fraction'] for row in rows.values())}
before,after=compare(previous),compare(cfg)
report={'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'source':cfg['upper_layout_source'],'landmarks':str(args.landmarks),'method':landmarks['method'],'before':before,'after':after,'improved_relative_to_sketch':after['max_edge_difference_fraction']<before['max_edge_difference_fraction'],'scope':'Coerência proporcional com o croqui, não medição do imóvel, estudo estrutural ou conciliação registral'}
(root/'relatorios/atual/proporcoes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PROPORTIONS',round(before['max_edge_difference_fraction']*100,2),round(after['max_edge_difference_fraction']*100,2),report['improved_relative_to_sketch'])
