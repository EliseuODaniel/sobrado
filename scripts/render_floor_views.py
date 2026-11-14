"""Renderiza depois as duas cenas de pavimento do Blender aberto."""
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
scenes=[s for s in bpy.data.scenes if s.name.startswith('VISUALIZACAO_')]
if len(scenes)<2:raise RuntimeError('Abra um dos projeto/<versao>/visualizacao-pavimentos.blend antes de executar.')
for scene in scenes:
 parts=scene.name.split('_',2);key,mode=parts[1:]
 filename='comparacao-lado-a-lado' if mode=='COMPARACAO' else mode
 dest=ROOT/'renders'/key/'vistas-pavimentos'/(filename+'.png');dest.parent.mkdir(parents=True,exist_ok=True)
 scene.render.filepath=str(dest)
 bpy.context.window.scene=scene
 bpy.ops.render.render(write_still=True,scene=scene.name)
 print('IMAGEM_OK',dest,flush=True)
