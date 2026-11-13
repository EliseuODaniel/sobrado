"""Primitivas e leituras nativas compartilhadas do ático aprovado."""
import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import blender_primitives as g
from residence07_industrial import geometry_fingerprint,world

def collection(name):
    col=bpy.data.collections.new(name);g.C[name]=col;return col

def prism(name,points,direction,mat,col):
    """Extrusão fechada de um polígono planar em 3D, com normais externas."""
    n=len(points);verts=[tuple(Vector(p)+Vector(direction)*side) for side in [0,1] for p in points]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new('ATC3 '+name);mesh.from_pydata(verts,[],faces);mesh.materials.append(g.M[mat]);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    obj=bpy.data.objects.new('ATC3 '+name,mesh);col.objects.link(obj);return obj

def ghost(source,name):
    col=collection(name)
    for old in source.all_objects:
        if old.type!='MESH':continue
        obj=old.copy();obj.data=old.data.copy();obj.name='ATC4 CORTE '+old.name
        obj.parent=None;obj.matrix_world=world(old)
        obj.data.materials.clear();obj.data.materials.append(g.M['EST Parede transparente']);col.objects.link(obj)
    return col

def bvh(objects):
    vertices=[];faces=[]
    for obj in objects:
        if obj.type!='MESH':continue
        n=len(vertices);vertices.extend(world(obj)@v.co for v in obj.data.vertices)
        faces.extend(tuple(n+i for i in f.vertices) for f in obj.data.polygons)
    return BVHTree.FromPolygons(vertices,faces,all_triangles=False)

def independent_compare(source_path,expected):
    with bpy.data.libraries.load(str(source_path),link=False) as (src,dst):
        names=[n for n in src.objects if n in expected];dst.objects=list(names)
    source=dict(zip(names,dst.objects))
    return [n for n,h in expected.items() if n not in source or geometry_fingerprint(source[n])!=h]
