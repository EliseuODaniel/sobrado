"""Reconstrução completa e verificável da casa atual; não renderiza automaticamente."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import current_photoreal_data as data


def run(input_blend,script,log_name):
    log=data.REPORT/log_name
    with log.open('w') as stream:
        subprocess.run([sys.executable,str(data.ROOT/'scripts/run_blender.py'),'-b',str(input_blend),'--python',str(data.ROOT/script)],cwd=data.ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True)
    print('PASSED',script,flush=True)


def model():return json.loads((data.REPORT/'modelo.json').read_text())


def validate_and_promote():
    m=model();temporary=data.ROOT/m['temporary_blend'];assert data.sha(temporary)==m['temporary_sha256']
    run(temporary,'scripts/current_photoreal_audit.py','reabertura.log')
    assert json.loads((data.REPORT/'validacao-nativa.json').read_text())['passed']
    temporary.replace(data.ROOT/m['blend']);m['blend_sha256']=m['temporary_sha256'];m['status']='validated'
    (data.REPORT/'modelo.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.parse_args()
    assert data.sha(data.ROOT/data.CFG['base_blend'])==data.CFG['base_sha256']
    target=data.ROOT/data.CFG['output_blend']
    if target.exists():
        previous=model();assert data.sha(target)==previous['blend_sha256'],'Modelo recebeu edição externa; preservar a edição antes de reconstruir.'
        archive=data.ROOT/'arquivos/historico/estudos/atual-v02/modelos'/previous['blend_sha256'];archive.mkdir(parents=True,exist_ok=True)
        if not (archive/target.name).exists():shutil.copy2(target,archive/target.name)
        assert data.sha(archive/target.name)==previous['blend_sha256'];(archive/'modelo.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2)+'\n')
    data.REPORT.mkdir(parents=True,exist_ok=True)
    run(data.ROOT/data.CFG['base_blend'],'scripts/current_photoreal.py','construcao.log')
    run(data.ROOT/model()['temporary_blend'],'scripts/finish_current_floor.py','acabamento-piso.log')
    validate_and_promote()
    for script,log in [('scripts/finish_current_cameras.py','acabamento-cameras.log'),('scripts/finish_current_entry.py','acabamento-entrada.log'),('scripts/finish_current_surfaces.py','acabamento-superficies.log'),('scripts/finish_current_textiles.py','acabamento-tecidos.log')]:
        run(data.ROOT/model()['blend'],script,log);validate_and_promote()
    print('CURRENT2_REBUILT',model()['blend_sha256'],flush=True)


if __name__=='__main__':main()
