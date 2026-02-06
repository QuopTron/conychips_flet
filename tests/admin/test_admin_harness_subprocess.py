import subprocess
import sys
import os
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
HARNESS = os.path.join(ROOT, 'tools', 'test_admin_pages.py')

def test_run_harness_script():
    if not os.path.exists(HARNESS):
        pytest.skip('Harness script tools/test_admin_pages.py not found')

    proc = subprocess.run([sys.executable, HARNESS], capture_output=True, text=True, cwd=ROOT)
    if proc.returncode != 0:
        print('STDOUT:\n', proc.stdout)
        print('STDERR:\n', proc.stderr)
    assert proc.returncode == 0, 'Harness script exited with non-zero code; see stdout/stderr above'
