"""Resumo pequeno dos recibos da casa atual; nenhuma alteração de arquivos."""
import json
from pathlib import Path
import current_photoreal_data as data

def read(name,fallback):
    p=data.REPORT/name
    if not p.exists():return fallback
    try:return json.loads(p.read_text())
    except json.JSONDecodeError:return fallback
m=read('modelo.json',{});sha=m.get('blend_sha256');previews=[r for r in read('previas.json',[]) if r.get('blend_sha256')==sha];renders=[r for r in read('renders.json',[]) if r.get('blend_sha256')==sha and not r.get('preview')]
print(json.dumps({'model_sha256':sha,'previews':len(previews),'finals':len(renders),'total':len(m.get('jobs',[])),'final_ids':[r['id'] for r in renders],'gallery_ready':(data.REPORT/'revisao-refinamento/galeria.html').exists(),'delivery_ready':read('entrega-validacao.json',{}).get('model_sha256')==sha,'last_preview':previews[-1]['id'] if previews else None,'last_final':renders[-1]['id'] if renders else None},ensure_ascii=False))
