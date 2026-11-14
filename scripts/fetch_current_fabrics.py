"""Capturas CC0 dos tecidos; verifica tamanho e MD5 oficiais antes da gravação."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1]
ASSETS=['scuba_suede','bi_stretch','waffle_pique_cotton']

def request(url):
    assert url.startswith(('https://api.polyhaven.com/','https://dl.polyhaven.org/'))
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'CasaInteriores/1.0'}),timeout=90) as f:return f.read()
        except Exception:
            if i==2:raise
            time.sleep(1)

def main():
    catalog=json.loads((ROOT/'relatorios/atual/fontes/fabric-assets.json').read_text());tasks=[]
    for asset in ASSETS:
        d=json.loads((ROOT/'relatorios/atual/fontes'/(asset+'-files.json')).read_text())
        for channel in ['Diffuse','Rough','nor_gl','anisotropy_strength','anisotropy_rotation','spec_ior']:
            resolution='4k' if channel in ['Diffuse','Rough','nor_gl'] else '2k';fmt='exr' if channel in ['nor_gl','anisotropy_strength','anisotropy_rotation','spec_ior'] else 'jpg';record=d[channel][resolution][fmt];tasks.append((asset,channel,resolution,record))
    def fetch(task):
        asset,channel,resolution,r=task;dest=ROOT/'assets/atual-fiel-v02/tecidos'/asset/r['url'].split('/')[-1]
        b=dest.read_bytes() if dest.exists() else request(r['url']);assert len(b)==r['size'] and hashlib.md5(b).hexdigest()==r['md5'],str(dest)
        if not dest.exists():
            dest.parent.mkdir(parents=True,exist_ok=True);tmp=dest.with_name(dest.name+'.part');tmp.write_bytes(b);tmp.replace(dest)
        print('FABRIC_VERIFIED',asset,channel,round(len(b)/1048576,2),'MiB',flush=True)
        return {'asset':asset,'channel':channel,'resolution':resolution,'path':dest.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(b).hexdigest(),'md5':r['md5'],'bytes':len(b),'source':r['url'],'source_page':'https://polyhaven.com/a/'+asset,'license':'CC0-1.0','license_url':'https://polyhaven.com/license','dimensions_m':[v/1000 for v in catalog[asset]['dimensions']],'authors':catalog[asset]['authors']}
    with ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(fetch,tasks))
    from PIL import Image
    for r in records:
        if r['channel']!='Diffuse':continue
        im=Image.open(ROOT/r['path']).convert('RGB');im.thumbnail((128,128));values=[]
        for pixel in im.getdata():
            linear=[v/255/12.92 if v/255<=.04045 else ((v/255+.055)/1.055)**2.4 for v in pixel];values.append(sum(a*b for a,b in zip(linear,[.2126,.7152,.0722])))
        r['luminance_linear_mean']=sum(values)/len(values)
    out=ROOT/'assets/atual-fiel-v02/tecidos/manifesto.json';out.write_text(json.dumps({'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'records':records},ensure_ascii=False,indent=2)+'\n')
    print('CURRENT2_FABRICS_READY',len(records),flush=True)
if __name__=='__main__':main()
