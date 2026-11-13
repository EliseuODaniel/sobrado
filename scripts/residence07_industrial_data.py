"""Contrato da proposta industrial sobre a geometria atual da residência 07."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'config/estilo-industrial-v05.json'
CFG=json.loads(CONFIG.read_text())


def references():
    return sorted(p for p in (ROOT/CFG['references']).iterdir() if p.is_file() and p.suffix.lower() in ['.png','.jpg','.webp','.jpeg'])


def jobs():
    source=json.loads((ROOT/'relatorios/residencia-07/estudo-instalacoes-atico/atual-modelo.json').read_text())
    titles={'sala-fundos':'Sala industrial integrada aos fundos','sala-frente':'Sofá de couro caramelo e jantar de madeira',
        'cozinha':'Cozinha grafite, madeira e luz quente','cozinha-reversa':'Cozinha e integração com jantar',
        'bar':'Bar industrial com quatro banquetas','suite':'Suíte com madeira e cimento',
        'quarto-frente':'Quarto frontal em tons de linho','quarto-fundos':'Dormitório dos fundos com bancada industrial',
        'planta-terreo':'Térreo industrial sobre a planta atual','planta-superior':'Superior industrial · opção com dormitórios'}
    result=[]
    for job in source['jobs']:
        result.append({**job,'scene':'IND07_'+job['id'],'source_scene':job['scene'],
            'title':titles.get(job['id'],job['title'].removeprefix('Atual · ')),
            'file':str(Path(CFG['render_directory'])/Path(job['file']).parent.name/(job['id']+'.png'))})
    extra=[
        ('sala-tv','Painel de cimento, rack metálico e luz âmbar','sala-frente',[.85,2.80,1.40],[3.20,1.40,1.35],22),
        ('mesa-jantar','Mesa de madeira inspirada na referência','sala-fundos',[2.85,3.30,1.45],[1.55,4.5,.8],23),
        ('bar-detalhe','Pedra oxidada, madeira e iluminação do bar','bar',[2.82,8.05,1.45],[1.42,10.05,1.45],23),
        ('escritorio-alternativa','Alternativa de escritório · mesa e telas','quarto-fundos',[5.73,4.65,4.15],[3.83,5.70,3.92],20),
        ('escritorio-reverso','Alternativa de escritório · estante e janela','quarto-fundos',[4.00,4.55,4.15],[5.85,6.0,3.90],20)]
    sources={j['id']:j for j in source['jobs']}
    for id,title,source_id,pos,target,lens in extra:
        result.append(dict(id=id,title=title,scene='IND07_'+id,source_scene=sources[source_id]['scene'],
            pos=pos,target=target,lens=lens,mode='office' if id.startswith('escritorio') else 'photo',
            file=str(Path(CFG['render_directory'])/'02-ambientes'/(id+'.png'))))
    return result


def validate():
    assert CFG['unit']=='07'
    assert CFG['base_blend']!=CFG['furniture_library']
    assert CFG['output_blend'] not in [CFG['base_blend'],CFG['furniture_library']]
    jobs_=jobs();assert len({j['id'] for j in jobs_})==len(jobs_)
    assert len({j['file'] for j in jobs_})==len(jobs_)
    assert len(references())==4
    return {'jobs':len(jobs_),'references':len(references())}


if __name__=='__main__':print(validate())
