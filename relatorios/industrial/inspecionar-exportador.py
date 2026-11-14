import bpy
p=bpy.ops.export_scene.gltf.get_rna_type().properties
keys=["export_materials","export_format","use_active_scene","use_selection","export_apply","export_extras","export_yup","export_texcoords","export_normals","export_cameras","export_lights"]
for k in keys:
 if k in p:
  v=p[k];print(k,[a.identifier for a in v.enum_items] if v.type=="ENUM" else v.type)
