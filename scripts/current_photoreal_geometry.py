"""Geometria editável dos acabamentos; sem alterar paredes, lajes ou escada."""
import math
import random
import bpy
from mathutils import Vector
import blender_primitives as g
from current_photoreal_materials import M

RNG=random.Random(71)
CREATED=[]

def col(name):
    c=bpy.data.collections.new('FIEL2_'+name);c.use_fake_user=True;g.C[c.name]=c
    if bpy.context.scene.name=='FIEL2_BUILD':bpy.context.scene.collection.children.link(c)
    return c

def mark(o,reference=None):
    o['photo_reconstruction']=True
    if reference:o['reference_photo']=reference
    CREATED.append(o.name);return o

def box(name,pos,size,mat,c,bevel=.008):return mark(g.box('FIEL2 '+name,pos,size,M.get(mat,mat),c.name,bevel))
def sphere(name,pos,size,mat,c):return mark(g.sphere('FIEL2 '+name,pos,size,M.get(mat,mat),c.name))
def rod(name,a,b,r,mat,c):return mark(g.rod('FIEL2 '+name,a,b,r,M.get(mat,mat),c.name))
def cyl(name,pos,r,h,mat,c,rotation=None):return mark(g.cylinder('FIEL2 '+name,pos,r,h,M.get(mat,mat),c.name,vertices=48,rotation=rotation))
def mesh(name,vertices,faces,mat,c,smooth=False):
    d=bpy.data.meshes.new('FIEL2 '+name);d.from_pydata(vertices,[],faces);d.materials.append(M.get(mat,mat));d.update();o=bpy.data.objects.new(d.name,d);c.objects.link(o)
    for p in d.polygons:p.use_smooth=smooth
    return mark(o)

def line(name,points,r,mat,c,closed=False):
    d=bpy.data.curves.new('FIEL2 '+name,'CURVE');d.dimensions='3D';d.resolution_u=1;d.bevel_depth=r;d.bevel_resolution=3
    sp=d.splines.new('POLY');sp.points.add(len(points)-1)
    for p,xyz in zip(sp.points,points):p.co=(*xyz,1)
    sp.use_cyclic_u=closed;d.materials.append(M.get(mat,mat));o=bpy.data.objects.new(d.name,d);c.objects.link(o);return mark(o)

def rounded_loop(center,size,r=.04,axes=(0,1),samples=8):
    pts=[];a,b=axes
    for sa,sb,angle in [(1,1,0),(-1,1,90),(-1,-1,180),(1,-1,270)]:
        ca=sa*(size[0]/2-r);cb=sb*(size[1]/2-r)
        for i in range(samples+1):
            t=math.radians(angle+i*90/samples);p=list(center);p[a]+=ca+r*math.cos(t);p[b]+=cb+r*math.sin(t);pts.append(p)
    return pts

def remove_objects(objects,protected=()):
    for o in list(objects):
        assert o.name not in protected,o.name
        bpy.data.objects.remove(o,do_unlink=True)

def pillow(name,pos,size,mat,c,power=.25,wrinkle=.0018,rotation=None):
    """Superelipsoide estofado com abaulamento e pequenas dobras junto às bordas."""
    verts=[];faces=[];nu,nv=96,48
    spow=lambda v,p:math.copysign(abs(v)**p,v)
    for j in range(nv+1):
        v=-math.pi/2+math.pi*j/nv;cv=spow(math.cos(v),power);sv=spow(math.sin(v),power)
        for i in range(nu):
            u=math.tau*i/nu;xx=cv*spow(math.cos(u),power);yy=cv*spow(math.sin(u),power)
            z=sv*size[2]/2
            edge=max(abs(xx),abs(yy));w=wrinkle*math.sin(27*u+3*math.sin(7*u))*math.exp(-((edge-.87)/.13)**2)*math.sin(v*2)
            verts.append((xx*size[0]/2,yy*size[1]/2,z+w))
    for j in range(nv):
        for i in range(nu):faces.append((j*nu+i,j*nu+(i+1)%nu,(j+1)*nu+(i+1)%nu,(j+1)*nu+i))
    o=mesh(name,verts,faces,mat,c,True);o.location=pos
    if rotation:o.rotation_euler=rotation
    return o

def curtain(name,x0,x1,y,z0,z1,c,mat='Cortina branca',fold=.045):
    nu=max(120,int((x1-x0)*130));nv=35;verts=[];faces=[]
    for j in range(nv+1):
        v=j/nv;z=z0+(z1-z0)*v
        for i in range(nu+1):
            u=i/nu;x=x0+(x1-x0)*u
            yy=y+fold*(.72+.28*(1-v))*math.sin(u*(x1-x0)*math.tau/.115)+.006*math.sin(35*u+3*v)
            zz=z+.012*math.sin(61*u)*(1-v)**8
            verts.append((x,yy,zz))
    for j in range(nv):
        for i in range(nu):
            k=j*(nu+1)+i;faces.append((k,k+1,k+nu+2,k+nu+1))
    o=mesh(name,verts,faces,mat,c,True);sol=o.modifiers.new('Espessura tecido 0.4 mm','SOLIDIFY');sol.thickness=.0004
    for zz in [z0+.025,z1-.06]:
        pts=[(x0+(x1-x0)*i/nu,y+fold*math.sin(i/nu*(x1-x0)*math.tau/.115),zz) for i in range(nu+1)]
        line(name+' bainha',pts,.0012,mat,c)
    return o

def bowl(name,center,w,d,depth,c,mat='Inox'):
    # Superfície aberta, com quatro cantos arredondados, fundo e ralo rebaixados.
    vertices=[];faces=[];n=64
    for z,scale in [(0,1),(-.015,.97),(-depth+.035,.80),(-depth,.68)]:
        for i in range(n):
            t=math.tau*i/n;sp=lambda v:math.copysign(abs(v)**.24,v)
            vertices.append((center[0]+w/2*scale*sp(math.cos(t)),center[1]+d/2*scale*sp(math.sin(t)),center[2]+z))
    for k in range(3):
        for i in range(n):faces.append((k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i))
    faces.append(tuple(reversed(range(3*n,4*n))))
    o=mesh(name,vertices,faces,mat,c,True)
    line(name+' aro',rounded_loop(center,(w,d),.065, samples=16),.006,mat,c,True)
    cyl(name+' ralo',(center[0],center[1],center[2]-depth+.002),.029,.004,'Cromado',c)
    for i in range(7):
        t=math.tau*i/7;cyl(name+' furos ralo',(center[0]+.017*math.cos(t),center[1]+.017*math.sin(t),center[2]-depth+.005),.0025,.002,'Borracha',c)
    return o
