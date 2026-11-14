"""Topologia de apresentação: redes documentais interpretadas e ligações propostas."""
from copy import deepcopy
import residence07_studies_data as source

TANK = (5.35, 3.175, 5.45)
COLORS = {'electric': (1., .38, .015), 'cold': (.025, .19, .95),
          'hot': (.9, .035, .025), 'overflow': (.015, .65, .58),
          'drain': (.65, .075, .5)}
LABELS = {'electric': 'Elétrica / eletrodutos', 'cold': 'Água fria',
          'hot': 'Água quente', 'overflow': 'Extravasor / ligação proposta',
          'drain': 'Limpeza / ligação proposta'}


def graph():
    original = deepcopy(source.pipe_points())
    nodes = {n['id']: n for n in original['nodes'] if n['system'] in COLORS}
    edges = [e for e in original['edges'] if e['system'] in COLORS]
    # O estudo anterior gerava uma coluna por aparelho, com trechos coincidentes.
    # Conservam-se o aquecedor e os cinco pontos; a distribuição passa a ser comum.
    hot_points = {key: value for key, value in nodes.items()
                  if value['system'] == 'hot' and value['kind'] in {'heater', 'outlet'}}
    nodes = {key: value for key, value in nodes.items() if value['system'] != 'hot'}
    nodes.update(hot_points)
    edges = [e for e in edges if e['system'] != 'hot']

    def node(key, xyz, system='cold', kind='junction'):
        assert key not in nodes
        nodes[key] = dict(id=key, xyz=list(xyz), system=system, kind=kind,
                          proposed=True, source='Percurso proposto de apresentação; não é levantamento da instalação')

    def chain(keys, diameter):
        for a, b in zip(keys, keys[1:]):
            assert nodes[a]['system'] == nodes[b]['system']
            edges.append(dict(a=a, b=b, system=nodes[a]['system'],
                              nominal_diameter_m=diameter, geometry='segment', proposed=True,
                              source='Ligação esquemática de apresentação; dimensionamento executivo pendente'))

    # HID04: AQ-1 comum aos banheiros, CPVC 22 mm, "sob a laje".
    # XY é aproximado pelo registro da prancha; Z=5,15 é de apresentação, não cota documental.
    for key, xyz in [('AQ-DESVIO-AQUECEDOR', (3.35, 6.1, 1.2)),
                     ('AQ-COLUNA-BASE', (3.35, 6.3, 1.2)),
                     ('AQ-COLUNA-TOPO', (3.35, 6.3, 5.15)),
                     ('AQ-TRONCO-SOCIAL', (1.83, 6.3, 5.15)),
                     ('AQ-TRONCO-SUITE', (.18, 6.3, 5.15)),
                     ('AQ-COZINHA-BAIXO', (3.47, 6.1, .48)),
                     ('AQ-COZINHA-DESVIO-X', (4.9, 6.1, .48)),
                     ('AQ-COZINHA-DESVIO-Y', (4.9, 7.02, .48))]:
        node(key, xyz, 'hot')
    chain(['AQ-AQUECEDOR', 'AQ-DESVIO-AQUECEDOR', 'AQ-COLUNA-BASE',
           'AQ-COLUNA-TOPO', 'AQ-TRONCO-SOCIAL', 'AQ-TRONCO-SUITE'], .022)
    chain(['AQ-AQUECEDOR', 'AQ-COZINHA-BAIXO', 'AQ-COZINHA-DESVIO-X',
           'AQ-COZINHA-DESVIO-Y', 'AQ-cozinha'], .022)
    for room, x, header in [('suite', .18, 'AQ-TRONCO-SUITE'),
                            ('social', 1.83, 'AQ-TRONCO-SOCIAL')]:
        top = f'AQ-{room}-TEE-CHUVEIRO'
        low = f'AQ-{room}-TEE-LAVATORIO'
        turn = f'AQ-{room}-DESVIO-LAVATORIO'
        node(top, (x, 6.3, 4.8), 'hot')
        node(low, (x, 6.3, 3.18), 'hot')
        node(turn, (x, 3.95, 3.18), 'hot')
        chain([header, top, low, turn, f'AQ-banho-{room}-lavatorio'], .022)
        chain([top, f'AQ-banho-{room}-chuveiro'], .022)
    # O reservatório e o aquecedor são equipamentos: a conexão interna não é um tubo externo.
    equipment = [dict(kind='tank', inlet='AF-ENTRADA', outlet='AF-SAIDA')]
    for key, xyz in [('AF-AQUECEDOR-ALTO', (3.47, 3.175, 2.35)),
                     ('AF-AQUECEDOR-DESVIO', (3.47, 6.1, 2.35)),
                     ('AF-AQUECEDOR', (3.47, 6.1, 1.2))]:
        node(key, xyz, kind='heater_inlet' if key == 'AF-AQUECEDOR' else 'junction')
    chain(['AF-PISO-0', 'AF-AQUECEDOR-ALTO', 'AF-AQUECEDOR-DESVIO', 'AF-AQUECEDOR'], .025)
    equipment.append(dict(kind='heater', inlet='AF-AQUECEDOR', outlet='AQ-AQUECEDOR'))
    for system, prefix, points in [
        ('overflow', 'EX', [(5.35, 4.015, 6.35), (5.35, 4.35, 6.35),
                            (5.35, 4.35, 5.05), (5.35, 7.45, 5.05)]),
        ('drain', 'LP', [(5.35, 4.015, 5.52), (5.7, 4.015, 5.52),
                         (5.7, 4.015, 4.85), (5.7, 7.45, 4.85)])]:
        keys = []
        for i, xyz in enumerate(points):
            key = f'{prefix}-{i}'; keys.append(key)
            node(key, xyz, system, 'connection_pending' if i == len(points)-1 else 'tank_port' if i == 0 else 'junction')
        chain(keys, .032)
    return dict(nodes=list(nodes.values()), edges=edges, equipment=equipment,
                status='Estudo de apresentação, com trechos propostos identificados; não é as-built ou projeto executivo')


def clip_segment(a, b, zmin, zmax):
    """Recorta um trecho linear ao intervalo vertical, preservando a direção."""
    dz = b[2] - a[2]
    if abs(dz) < 1e-10:
        return [list(a), list(b)] if zmin <= a[2] <= zmax else None
    ends = sorted(((zmin-a[2])/dz, (zmax-a[2])/dz))
    low, high = max(0., ends[0]), min(1., ends[1])
    if high-low < 1e-9:
        return None
    return [[a[i] + (b[i]-a[i])*t for i in range(3)] for t in [low, high]]


def hot_geometry_issues(graph):
    """Detecta trechos quentes não ortogonais ou com sobreposição de comprimento positivo."""
    nodes = {n['id']: n for n in graph['nodes']}
    groups = {}; issues = []
    for i, edge in enumerate(graph['edges']):
        if edge['system'] != 'hot' or edge['geometry'] == 'junction': continue
        a, b = nodes[edge['a']]['xyz'], nodes[edge['b']]['xyz']
        axes = [j for j in range(3) if abs(a[j]-b[j]) > 1e-8]
        if len(axes) != 1:
            issues.append(dict(kind='non_orthogonal_or_zero', edge=i)); continue
        axis = axes[0]
        key = (axis, *[round(a[j], 7) for j in range(3) if j != axis])
        low, high = sorted((a[axis], b[axis]))
        for oldlow, oldhigh, oldindex in groups.get(key, []):
            if min(high, oldhigh)-max(low, oldlow) > 1e-8:
                issues.append(dict(kind='overlap', edges=[oldindex, i]))
        groups.setdefault(key, []).append((low, high, i))
    return issues
