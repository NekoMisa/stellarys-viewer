from pathlib import Path
import importlib.util, os, sys, json, shutil

here = Path(__file__).resolve().parent
root = Path(os.environ.get('FK_PROTOTYPE_ROOT', r'C:\FK-Poser-Test'))
build = root / 'build-vs18-v143'
source = root / 'source/indra/newview'
revision = os.environ.get('FK_RELEASE_REVISION', '')
assert revision in ('', 'r2')
destination = root / ('release/FireKittyPoser-Prototype-0.1' + ('-' + revision if revision else ''))
sys.path.insert(0, str(source))
spec = importlib.util.spec_from_file_location('fs_manifest', source / 'viewer_manifest.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
def portable_finish(self):
    self.package_file = self.final_exe()
module.Windows_x86_64_Manifest.package_finish = portable_finish
module.Windows_x86_64_Manifest.final_exe = lambda self: 'Firestorm-FireKittyPoser.exe'
os.chdir(build / 'newview')
sys.argv = [str(source / 'viewer_manifest.py'), '--actions=copy package',
    '--platform=windows', '--arch=x86_64', '--configuration=Release', '--buildtype=Release',
    '--channel=Firestorm Fire Kitty Poser Prototype 0.1', '--viewer_flavor=hvk',
    '--grid=agni', '--bugsplat=', '--discord=OFF', '--fmodstudio=ON', '--openal=OFF',
    '--tracy=OFF', '--velopack=OFF', '--avx2=ON', f'--source={source}',
    f'--artwork={source}', f'--build={build / "newview"}', f'--dest={destination}',
    f'--versionfile={build / "newview/viewer_version.txt"}']
module.main(extra=[dict(name=n, description=n, default=d) for n, d in
    [('bugsplat',''), ('discord','OFF'), ('fmodstudio','OFF'), ('openal','ON'),
     ('tracy','OFF'), ('velopack','OFF'), ('avx2','ON')]])
(destination / 'fire-kitty-poser-version.json').write_text(json.dumps({
    'base_version': '7.2.4.80712', 'fix_version': '0.1.0', 'poser_prototype_version': '0.1', 'revision': revision or 'r1',
    'base_commit': '10bd3c9f930c76e1427ddd4ecece6cdf36b4406d',
    'amd_commit': '0c132c2eb3d15afc56d7fe42589dc8f2eb778197',
    'profile': 'FirestormFireKittyPoser_x64', 'status': 'experimental local poser; manual updates only'
}, indent=2))
shutil.copy2(here / ('TESTING-r2.txt' if revision else 'TESTING.txt'), destination / 'README-Fire-Kitty-Poser.txt')
print('Portable prototype packaged:', destination)
