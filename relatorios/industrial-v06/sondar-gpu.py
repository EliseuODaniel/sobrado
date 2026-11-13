import bpy
p=bpy.context.preferences.addons["cycles"].preferences
print("BLENDER_VERSION",bpy.app.version_string,flush=True)
for backend in ["OPTIX","CUDA"]:
 try:
  p.compute_device_type=backend;p.get_devices();print("DEVICES",backend,[(d.name,d.type) for d in p.devices],flush=True)
 except Exception as e:print("DEVICE_ERROR",backend,type(e).__name__,str(e)[:180],flush=True)
