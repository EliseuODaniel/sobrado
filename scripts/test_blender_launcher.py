"""Verifica o encaminhamento do launcher sem abrir Blender ou alterar o host."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BlenderLauncherTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='casa-launcher-test-')
        self.addCleanup(self.temp.cleanup)
        executable = Path(self.temp.name) / 'blender-fake'
        executable.write_text('''#!/usr/bin/env python3
import json, os, sys
print('RECEIPT='+json.dumps({'args':sys.argv[1:],
    'preload':os.environ.get('LD_PRELOAD'),
    'library':os.environ.get('LD_LIBRARY_PATH')}))
raise SystemExit(int(os.environ.get('CASA_TEST_EXIT', '0')))
''')
        executable.chmod(0o755)
        if os.name == 'nt':
            script = executable.with_suffix('.py')
            executable.rename(script)
            executable = executable.with_suffix('.cmd')
            executable.write_text(
                '@echo off\n"' + sys.executable + '" "' + str(script) + '" %*\n',
                encoding='utf-8',
            )
        self.env = dict(os.environ, BLENDER_EXECUTABLE=str(executable))

    def run_launcher(self, *args):
        run = subprocess.run([sys.executable, 'scripts/run_blender.py', *args],
            cwd=ROOT, env=self.env, capture_output=True, text=True, timeout=10)
        receipt = next(line for line in run.stdout.splitlines() if line.startswith('RECEIPT='))
        return run.returncode, json.loads(receipt.split('=', 1)[1])

    def test_default_preserves_environment_and_arguments(self):
        code, receipt = self.run_launcher('--background')
        self.assertEqual(code, 0)
        self.assertEqual(receipt['args'], ['--background'])
        self.assertEqual(receipt['preload'], self.env.get('LD_PRELOAD'))
        self.assertEqual(receipt['library'], self.env.get('LD_LIBRARY_PATH'))

    @unittest.skipUnless(Path('/usr/lib/wsl/lib/libcuda.so.1').is_file(), 'Driver WSL ausente')
    def test_wsl_driver_applies_only_to_child_and_preserves_script_arguments(self):
        parent_preload = os.environ.get('LD_PRELOAD')
        code, receipt = self.run_launcher('--wsl-gpu', '--background', '--python', 'script.py', '--', '--cpu')
        self.assertEqual(code, 0)
        self.assertEqual(receipt['preload'], '/usr/lib/wsl/lib/libcuda.so.1')
        self.assertTrue(receipt['library'].startswith('/usr/lib/wsl/lib'))
        self.assertEqual(receipt['args'], ['--python-exit-code', '1', '--background', '--python', 'script.py', '--', '--cpu'])
        self.assertEqual(os.environ.get('LD_PRELOAD'), parent_preload)

    def test_forwards_failure_status(self):
        self.env['CASA_TEST_EXIT'] = '7'
        code, _ = self.run_launcher('--background')
        self.assertEqual(code, 7)


if __name__ == '__main__':
    unittest.main()
