#!/usr/bin/env python3
"""Exercise real desktop parsing/launching and isolated MIME default updates."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time


def main():
    checks = 0
    def check(value):
        nonlocal checks
        checks += 1
        if not value:
            raise AssertionError('Desktop fixture check failed: ' + str(checks))
    with tempfile.TemporaryDirectory(prefix='stellarys-desktop-fixture-') as temporary:
        root = Path(temporary)
        prefix = root / 'Viewer space % $ ` " folder'
        (prefix / 'bin').mkdir(parents=True)
        shutil.copy2(Path(__file__).with_name('install-desktop.py'), prefix / 'install-desktop.py')
        (prefix / 'bin/stellarys-bin').write_text('fixture only')
        (prefix / 'Stellarys.png').write_text('fixture icon')
        stub = prefix / 'stellarys'
        stub.write_text('#!/usr/bin/python3\nimport sys,os,json\nfrom pathlib import Path\n'
                        'Path(os.environ["STELLARYS_FIXTURE_ARGV"]).write_text(json.dumps(sys.argv[1:]))\n')
        stub.chmod(0o755)
        env = os.environ.copy()
        env.update(XDG_DATA_HOME=str(root / 'data'), XDG_CONFIG_HOME=str(root / 'config'),
                   STELLARYS_FIXTURE_ARGV=str(root / 'argv.json'))
        config = root / 'config/mimeapps.list'
        config.parent.mkdir()
        before = '[Default Applications]\nx-scheme-handler/secondlife=fixture-firestorm.desktop;\ntext/plain=fixture-editor.desktop;\n'
        config.write_text(before)
        setup = ['python3', str(prefix / 'install-desktop.py')]
        subprocess.run(setup, env=env, check=True)
        desktop = root / 'data/applications/org.stellarys.Viewer.desktop'
        check(desktop.exists())
        check(config.read_text() == before)
        subprocess.run(['desktop-file-validate', str(desktop)], check=True)
        check('X-Stellarys-Desktop-Entry=true' in desktop.read_text())
        for arguments in ([], ['secondlife://Example%20Region/128/128/20?x=1&y=2']):
            result = root / 'argv.json'
            result.unlink(missing_ok=True)
            subprocess.run(['gio', 'launch', str(desktop), *arguments], env=env, check=True)
            deadline = time.monotonic() + 5
            while not result.exists() and time.monotonic() < deadline:
                time.sleep(0.05)
            check(result.exists())
            check(json.loads(result.read_text()) == arguments)
        subprocess.run(setup, env=env, check=True)
        check(config.read_text() == before)
        subprocess.run(setup + ['--register-links'], env=env, check=True)
        for scheme in ('secondlife', 'hop'):
            actual = subprocess.check_output(['xdg-mime', 'query', 'default', 'x-scheme-handler/' + scheme], env=env, text=True).strip()
            check(actual == 'org.stellarys.Viewer.desktop')
        check('text/plain=fixture-editor.desktop' in config.read_text())
        foreign = '[Desktop Entry]\nType=Application\nName=Unrelated\nExec=/bin/true\n'
        desktop.write_text(foreign)
        rejected = subprocess.run(setup, env=env, capture_output=True)
        check(rejected.returncode != 0)
        check(desktop.read_text() == foreign)
    print(str(checks) + ' desktop fixture checks passed; real user defaults untouched.')


if __name__ == '__main__':
    main()
