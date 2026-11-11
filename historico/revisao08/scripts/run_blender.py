"""Launcher local: converte caminhos WSL/Windows e não instala configurações globais.

python3 scripts/run_blender.py --background --factory-startup --python-exit-code 1 \
    --python scripts/build_house.py -- --project-root . --device cpu
"""
from pathlib import Path
import os
import shutil
import subprocess
import sys

root=Path(__file__).resolve().parents[1]
windows=root/'.tools/blender-5.2.4-windows-x64/blender.exe'
linux=root/'.tools/blender-5.2.4-linux-x64/blender'
# A versão Windows portátil não iniciou neste host (dependência lado a lado).
# Use o Linux validado por padrão; uma instalação Windows funcional pode ser indicada.
exe=os.environ.get('BLENDER_EXECUTABLE') or (str(linux) if linux.is_file() else shutil.which('blender'))
if not exe:raise SystemExit('Blender não localizado. Defina BLENDER_EXECUTABLE para a instalação 5.2 LTS.')
args=sys.argv[1:]
if '--python' in args and '--python-exit-code' not in args:
    args=['--python-exit-code','1',*args]
is_windows=str(exe).lower().endswith('.exe') and shutil.which('wslpath')
path_flags={'--python','--project-root','--output','--blend','--render-output','-o','-b'}
converted=[]
for i,arg in enumerate(args):
    is_path=(i>0 and args[i-1] in path_flags and not arg.startswith('-')) or arg.endswith('.blend')
    if is_windows and is_path and not arg.startswith('\\\\') and not (len(arg)>1 and arg[1]==':'):
        path=Path(arg).resolve()
        arg=subprocess.check_output(['wslpath','-w',str(path)],text=True).strip()
    converted.append(arg)
print('BLENDER_EXECUTABLE',exe,flush=True)
raise SystemExit(subprocess.run([exe,*converted],cwd=root).returncode)
