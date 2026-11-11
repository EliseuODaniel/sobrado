"""Baixa recursos CC0 oficiais; verifica tamanho e MD5 antes de gravar."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'assets/industrial-v04'


def request(url):
    assert url.startswith(('https://api.polyhaven.com/', 'https://dl.polyhaven.org/'))
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'CasaInteriores/1.0'}), timeout=45) as response:
                return response.read()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1)


def main():
    records = []
    for asset, kind in [('modern_arm_chair_01','model'), ('potted_plant_02','model'), ('calathea_orbifolia_01','model'), ('slate_floor_03','texture')]:
        data = json.loads(request('https://api.polyhaven.com/files/' + asset))
        if kind == 'model':
            blend = data['blend']['2k']['blend']
            selected = [(f'{asset}_2k.blend', blend), *blend.get('include', {}).items()]
        else:
            selected = [(item['url'].split('/')[-1], item) for channel, fmt in [('Diffuse','jpg'),('Rough','jpg'),('nor_gl','exr')] for item in [data[channel]['2k'][fmt]]]
        for name, item in selected:
            path = FOLDER / asset / name
            if path.exists():
                content = path.read_bytes()
            else:
                content = request(item['url'])
            assert len(content) == item['size'] and hashlib.md5(content).hexdigest() == item['md5'], path
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                temporary = path.with_name(path.name+'.part')
                temporary.write_bytes(content)
                temporary.replace(path)
            records.append({'asset':asset, 'path':str(path.relative_to(ROOT)), 'source':item['url'],
                'source_page':'https://polyhaven.com/a/'+asset, 'license':'CC0-1.0',
                'license_url':'https://polyhaven.com/license', 'bytes':len(content),
                'md5':item['md5'], 'sha256':hashlib.sha256(content).hexdigest()})
        print('ASSET_VERIFIED',asset,flush=True)
    (FOLDER/'manifesto.json').write_text(json.dumps({'timestamp_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'records':records},ensure_ascii=False,indent=2)+'\n')


if __name__ == '__main__':
    main()
