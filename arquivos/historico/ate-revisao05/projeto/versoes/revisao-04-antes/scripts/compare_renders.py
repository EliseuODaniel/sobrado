"""Comparações locais, sem usar referências como texturas do render."""
import argparse
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops,ImageStat

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('render',type=Path);p.add_argument('--name',default='comparacao');args=p.parse_args()
ref=Image.open(root/'referencias/01-cena-final.png').convert('RGB')
render=Image.open(args.render if args.render.is_absolute() else root/args.render).convert('RGB')
assert abs(ref.width/ref.height-render.width/render.height)<.003,'Proporções diferentes'
render=render.resize(ref.size,Image.Resampling.LANCZOS)
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=ImageFont.truetype(fontpath,26) if Path(fontpath).exists() else ImageFont.load_default()
out=Image.new('RGB',(ref.width*2,ref.height+60),(20,23,23))
out.paste(ref,(0,60));out.paste(render,(ref.width,60));d=ImageDraw.Draw(out)
d.text((24,15),'REFERÊNCIA — proporções e arquitetura não medidas',font=font,fill=(235,235,230))
d.text((ref.width+24,15),'BLENDER / CYCLES — geometria editável e reflexo físico',font=font,fill=(235,235,230))
target=root/'renders'/f'{args.name}.png';out.save(target)
Image.blend(ref,render,.5).save(root/'renders'/f'{args.name}-sobreposicao.png')
print('COMPARISON',target)
