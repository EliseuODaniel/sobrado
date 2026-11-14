"""Texturas 4K CC0 do Poly Haven, com verificação de tamanho e hashes."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_industrial_assets import request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/fotorrealismo-industrial'
API = ROOT / 'relatorios/industrial/api'


def download(task):
    asset, channel, item = task
    dest = OUT / asset / item['url'].rsplit('/', 1)[1]
    content = dest.read_bytes() if dest.exists() else request(item['url'])
    if len(content) != item['size'] or hashlib.md5(content).hexdigest() != item['md5']:
        raise ValueError(f'Integridade inválida: {asset}/{channel}')
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        temp = dest.with_suffix(dest.suffix + '.part')
        temp.write_bytes(content)
        temp.replace(dest)
    return {'asset': asset, 'channel': channel, 'path': str(dest.relative_to(ROOT)),
            'source': item['url'], 'source_page': 'https://polyhaven.com/a/' + asset,
            'license': 'CC0-1.0', 'license_url': 'https://polyhaven.com/license',
            'bytes': len(content), 'md5': item['md5'], 'sha256': hashlib.sha256(content).hexdigest()}


def main():
    tasks = []
    for asset in ['wood_table_001', 'grey_plaster', 'brown_leather', 'denim_fabric', 'floor_tiles_02', 'slate_floor_03']:
        data = json.loads((API / (asset + '.json')).read_text())
        for channel, fmt in [('Diffuse', 'jpg'), ('Rough', 'jpg'), ('nor_gl', 'png')]:
            tasks.append((asset, channel, data[channel]['4k'][fmt]))
    data = json.loads((API / 'garden_nook.json').read_text())
    tasks.append(('garden_nook', 'hdri', data['hdri']['4k']['hdr']))
    with ThreadPoolExecutor(max_workers=3) as pool:
        records = list(pool.map(download, tasks))
    (OUT / 'manifesto.json').write_text(json.dumps({'resolution': '4k', 'records': records}, ensure_ascii=False, indent=2) + '\n')
    (OUT / 'README.md').write_text('# Materiais fotográficos industriais\n\nTexturas e HDRI 4K do Poly Haven (CC0-1.0). O manifesto registra URL oficial, licença, tamanho, MD5 e SHA-256. Nenhuma imagem de referência foi aplicada como substituta de geometria.\n')
    print('PHOTOREAL_ASSETS_VERIFIED', len(records), sum(r['bytes'] for r in records), flush=True)


if __name__ == '__main__':
    main()
