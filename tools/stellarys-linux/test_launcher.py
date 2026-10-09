#!/usr/bin/env python3
"""Run the actual adapted upstream wrapper against a disposable binary stub."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
from package_linux import make_launcher

repo = Path(__file__).resolve().parents[2]
launcher = make_launcher((repo / 'indra/newview/linux_tools/wrapper.sh').read_text())
assert 'test -x ./etc/register_' not in launcher
checks = 1
with tempfile.TemporaryDirectory(prefix='stellarys-launcher-') as temporary:
    root = Path(temporary)
    prefix = root / 'Viewer space % $ ` " folder'
    (prefix / 'bin').mkdir(parents=True)
    wrapper = prefix / 'stellarys'
    wrapper.write_text(launcher)
    wrapper.chmod(0o755)
    stub = prefix / 'bin/stellarys-bin'
    stub.write_text('#!/usr/bin/python3\nimport sys,os,json\nfrom pathlib import Path\n'
                    'Path(os.environ["STELLARYS_FIXTURE_ARGV"]).write_text(json.dumps(sys.argv[1:]))\n'
                    'sys.exit(23)\n')
    stub.chmod(0o755)
    env = os.environ.copy()
    env['STELLARYS_FIXTURE_ARGV'] = str(root / 'argv.json')
    cases = [([], []), (['secondlife://Example%20Region/1/2/3?x=1&y=2'],
                       ['--url', 'secondlife://Example%20Region/1/2/3?x=1&y=2']),
             (['HOP://Example/1/2/3'], ['--url', 'HOP://Example/1/2/3']),
             (['--skip-gridargs', '--settings', 'a b.xml'], ['--settings', 'a b.xml']),
             (['--url', 'secondlife://Example/1/2/3'], ['--url', 'secondlife://Example/1/2/3'])]
    for args, expected in cases:
        result = subprocess.run([str(wrapper), *args], env=env, capture_output=True)
        assert result.returncode == 23, result.stderr
        assert json.loads((root / 'argv.json').read_text()) == expected
        checks += 2
print(f'{checks} launcher checks passed using a stub; no viewer or link defaults changed.')
