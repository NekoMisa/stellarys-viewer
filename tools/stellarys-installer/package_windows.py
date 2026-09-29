from pathlib import Path
import subprocess, shutil, hashlib, json, zipfile, os, sys, importlib.util
repo=Path(__file__).resolve().parents[2]
w=Path(os.environ.get('STELLARYS_WORK', str(repo.parent)))
build=Path(os.environ.get('STELLARYS_BUILD', r'C:\FK-Poser-Test\build-vs18-v143'))
version=json.loads((repo/'stellarys-source.json').read_text())['stellarys_version']
out=w.parent/('outputs/Stellarys-Viewer-'+version); out.mkdir(parents=True,exist_ok=True)
payload=w/('stellarys-payload-'+version); payload.mkdir(exist_ok=True)
source=repo/'indra/newview'
icon=source/'icons/stellarys/firestorm_icon.ico'
sys.path.insert(0,str(source))
spec=importlib.util.spec_from_file_location('viewer_manifest',source/'viewer_manifest.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def portable_finish(self):
 self.package_file=self.final_exe()
module.Windows_x86_64_Manifest.package_finish=portable_finish
module.Windows_x86_64_Manifest.final_exe=lambda self: 'StellarysViewer.exe'
os.chdir(build/'newview')
sys.argv=[str(source/'viewer_manifest.py'),'--actions=copy package','--platform=windows','--arch=x86_64','--configuration=Release','--buildtype=Release','--channel=Stellarys Viewer','--viewer_flavor=hvk','--grid=agni','--bugsplat=','--discord=OFF','--fmodstudio=ON','--openal=OFF','--tracy=OFF','--velopack=OFF','--avx2=ON',f'--source={source}',f'--artwork={source}',f'--build={build/"newview"}',f'--dest={payload}',f'--versionfile={build/"newview/viewer_version.txt"}']
module.main(extra=[dict(name=n,description=n,default=d) for n,d in [('bugsplat',''),('discord','OFF'),('fmodstudio','OFF'),('openal','ON'),('tracy','OFF'),('velopack','OFF'),('avx2','ON')]])
for name in ('Firestorm-FireKittyPoser.exe','fire-kitty-poser-version.json','README-Fire-Kitty-Poser.txt'):
 (payload/name).unlink(missing_ok=True)
shutil.copy2((build/'newview/Release/firestorm-bin.exe'),payload/'StellarysViewer.exe')
subprocess.run([r'C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe','/nologo','/target:winexe','/win32icon:'+str(icon),'/out:'+str(payload/'StellarysUpdater.exe'),'/r:System.Windows.Forms.dll','/r:System.Drawing.dll','/r:System.Net.Http.dll','/r:System.Web.Extensions.dll',str(repo/'tools/stellarys-updater/Updater.cs')],check=True)
shutil.copy2(icon,payload/'Stellarys.ico')
shutil.copy2(repo/'LICENSE',payload/'LICENSE.txt')
shutil.copytree((build/'packages/LICENSES'),payload/'ThirdPartyLicenses',dirs_exist_ok=True)
shutil.copy2(repo/'tools/stellarys-installer/README-Stellarys.txt',payload/'README-Stellarys.txt')
shutil.copy2(repo/'tools/stellarys-installer/README-Stellarys.txt',out/'README.txt')
(payload/'stellarys-install.txt').write_text('StellarysViewer\nVersion='+version+'\nBase=7.2.4.80712\n',encoding='utf-8')
(payload/'stellarys-version.json').write_text(json.dumps({'name':'Stellarys Viewer','version':version,'base_version':'7.2.4.80712','profile':'Stellarys_x64','updater':'GitHub Releases; opt-in download and install'},indent=2),encoding='utf-8')
manifest=[];install=[];uninstall=[];dirs=set()
def q(s):return '"'+str(s).replace('$','$$').replace('"','$\\"')+'"'
for p in sorted(payload.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(payload)
 assert not any(x.lower() in ('.git','logs','user_settings','private-backups','browser_profile','cache') for x in rel.parts),rel
 assert p.suffix.lower() not in ('.log','.dmp','.pdb','.pfx','.p12','.key'),rel
 assert p.name.lower() not in ('password.dat','bin_conf.dat','stored_logins.xml','agni_agents.xml'),rel
 folder=str(rel.parent)
 install+=['SetOutPath "$INSTDIR'+('\\'+folder if folder!='.' else '')+'"','File '+q(p)]
 uninstall+=['Delete "$INSTDIR\\'+str(rel).replace('$','$$')+'"']
 dirs.update(str(x) for x in rel.parents if str(x)!='.')
 manifest.append({'path':str(rel),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
uninstall+=['RMDir "$INSTDIR\\'+d+'"' for d in sorted(dirs,key=lambda d:(d.count('\\'),d),reverse=True)]
(out/'install-files.nsh').write_text('\n'.join(install),encoding='utf-8-sig')
(out/'uninstall-files.nsh').write_text('\n'.join(uninstall),encoding='utf-8-sig')
(out/'PAYLOAD-MANIFEST.json').write_text(json.dumps(manifest,indent=2))
exe=out/('Stellarys-Viewer-'+version+'-Windows-x64-Setup.exe')
with (out/'installer-build.log').open('w') as log:
 subprocess.run([str(w/'installer/nsis-3.12/makensis.exe'),'/V3',f'/DPAYLOAD={payload}',f'/DOUTPUT={exe}',f'/DINSTALL_FILES={out/"install-files.nsh"}',f'/DUNINSTALL_FILES={out/"uninstall-files.nsh"}',f'/DGUARD={repo/"tools/stellarys-installer/InstallerGuard.ps1"}',f'/DREMOVE_DATA={repo/"tools/stellarys-updater/RemoveUserData.ps1"}',str(repo/'tools/stellarys-installer/Stellarys.nsi')],stdout=log,stderr=subprocess.STDOUT,check=True)
print('Stellarys installer compiled; clean payload files:',len(manifest),flush=True)
