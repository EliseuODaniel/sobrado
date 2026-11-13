"""Conferência determinística da entrega atual, independente da geração visual."""
import json
import struct
from pathlib import Path
import fitz
from PIL import Image
import current_photoreal_data as data

m=json.loads((data.REPORT/'modelo.json').read_text());rows=json.loads((data.REPORT/'renders.json').read_text());delivery=json.loads((data.REPORT/'entrega.json').read_text());checks=[]
def check(label,ok):
    checks.append({'check':label,'passed':bool(ok)})
    if not ok:raise AssertionError(label)
check('Modelo final corresponde ao recibo',data.sha(data.ROOT/m['blend'])==m['blend_sha256'])
check('Fonte anterior preservada',data.sha(data.ROOT/data.CFG['base_blend'])==data.CFG['base_sha256'])
check('Conjunto exato de vistas',{r['id'] for r in rows}=={j['id'] for j in m['jobs']} and len(rows)==len(m['jobs']))
for r in rows:
    p=data.ROOT/r['file'];check('Imagem íntegra '+r['id'],p.is_file() and data.sha(p)==r['sha256'])
    check('Imagem do modelo corrente '+r['id'],r['blend_sha256']==m['blend_sha256'] and r['config_sha256']==m['config_sha256'])
    check('Configuração final nativa '+r['id'],not r['preview'] and r['backend']=='OPTIX' and r['samples']==data.CFG['samples'])
    with p.open('rb') as f:
        header=f.read(29)
    check('PNG nativo RGB16 em 4K '+r['id'],header[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',header[16:24])==tuple(data.CFG['resolution']) and header[24]==16 and header[25]==2)
    with Image.open(p) as im:im.verify()
for r in delivery['artifacts']:check('Artefato '+r['file'],data.sha(data.ROOT/r['file'])==r['sha256'])
pairs=json.loads((data.REPORT/'comparacoes.json').read_text());check('Comparações por ambiente',len(pairs)==16)
with fitz.open(data.ROOT/data.CFG['render_directory']/'00-cadernos/caderno-atual.pdf') as pdf:check('Caderno completo',len(pdf)==delivery['pdf_pages'] and len(pdf)>=43)
check('Fotos originais preservadas',all(data.sha(data.ROOT/r['file'])==r['sha256'] for r in m['references']))
result={'passed':True,'total':len(checks),'checks':checks,'model_sha256':m['blend_sha256'],'renders':len(rows),'comparisons':len(pairs),'scope':'Integridade dos arquivos; não certifica fotorealismo por pontuação automática.'}
(data.REPORT/'entrega-validacao.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('CURRENT2_DELIVERY_VALIDATED',len(checks),'checks')
