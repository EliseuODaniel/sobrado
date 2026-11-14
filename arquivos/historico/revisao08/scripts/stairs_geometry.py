"""Escada aproximada: contagens informadas, curva estimada, posições em metros."""

def step_specs(spec, height):
    """Prismas editáveis; seis leques na curva são hipótese, não levantamento."""
    width = spec['flight_width']
    rise = height / spec['risers']
    tread = spec['first_run'] / spec['first_steps']
    steps = []
    def add(poly, phase, edge):
        index = len(steps) + 1
        steps.append(dict(index=index, phase=phase, polygon=poly, height=index*rise, riser=edge))
    for i in range(spec['first_steps']):
        x=spec['first_x_min']+i*tread;y=spec['first_y']-width/2
        add([(x,y),(x+tread,y),(x+tread,y+width),(x,y+width)],1,[(x,y),(x,y+width)])
    x=spec['turn_start_x'];right=spec['outer_x'];lo=spec['return_y']-width/2;hi=spec['first_y']+width/2;mid=(lo+hi)/2
    center=(x,mid)
    # Parametrizar a borda do retângulo permite variar a contagem provisória.
    length=(right-x)*2+hi-lo
    def border(distance):
        if distance<=right-x:return (x+distance,hi)
        distance-=right-x
        if distance<=hi-lo:return (right,hi-distance)
        return (right-(distance-(hi-lo)),lo)
    for i in range(spec['turn_steps']):
        a=border(length*i/spec['turn_steps']);b=border(length*(i+1)/spec['turn_steps'])
        # Incluir quinas atravessadas para não cortar a borda externa.
        poly=[center,a]
        for corner in [right-x,right-x+hi-lo]:
            if length*i/spec['turn_steps']<corner<length*(i+1)/spec['turn_steps']:poly.append(border(corner))
        poly.append(b);add(poly,'curva',[center,a])
    for i in range(spec['final_steps']):
        east=x-i*tread;west=east-tread;y=lo
        add([(west,y),(east,y),(east,y+width),(west,y+width)],2,[(east,y),(east,y+width)])
    return steps


def return_ceiling(spec,height,x):
    ratio=max(0,min(1,(x-spec['x_min'])/spec['run']))
    return height-.25-ratio*(height-spec['return_base_height'])


def slab_cells(bounds,holes):
    x0,x1,y0,y1=bounds
    xs=sorted({x0,x1,*[p for hole in holes for p in hole[:2] if x0<p<x1]})
    ys=sorted({y0,y1,*[p for hole in holes for p in hole[2:] if y0<p<y1]})
    for a,b in zip(xs,xs[1:]):
        for c,d in zip(ys,ys[1:]):
            if not any(h[0]<(a+b)/2<h[1] and h[2]<(c+d)/2<h[3] for h in holes):yield (a,b,c,d)


def guard(cfg):
    """Vidro somente na borda do hall, nunca na linha entre os lances."""
    import house_geometry as h
    s=cfg['layout']['stairs'];z=cfg['estimated_dimensions_m']['floor_height'];x=s['x_min'];a=s['return_y']+s['flight_width']/2;b=s['first_y']+s['flight_width']/2
    h.box('Guarda-corpo borda do hall',(x,(a+b)/2,z+.5),(.012,b-a,1.0),'Vidro transparente','Escada',.001)
    for y in [a,b]:
        h.box('Poste guarda-corpo borda do hall',(x,y,z+.48),(.026,.026,.96),'Inox','Escada',.003)
        h.box('Base guarda-corpo borda do hall',(x,y,z+.025),(.09,.09,.05),'Inox','Escada',.004)
