from pathlib import Path
import importlib.util, os, subprocess, sys, json, datetime

here = Path(__file__).resolve().parent
workspace = here.parents[1]
root = Path(os.environ.get('FK_PROTOTYPE_ROOT', r'C:\FK-Poser-Test'))
src = root / 'source'
build = root / 'build-vs18-v143'
tools = Path(os.environ.get('FK_TOOLS_ROOT', r'C:\FS-AMD-Test\python-tools'))
variables = Path(os.environ.get('FK_BUILD_VARIABLES', r'C:\FS-AMD-Test\variables\variables'))
helper_path = here / 'toolchain_helper.py'
if not helper_path.exists():
    helper_path = workspace / 'work/package/Black-Dragon-AMD-Port/build_windows.py'
spec = importlib.util.spec_from_file_location('toolchain_helper', helper_path)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
major, install, tool_version, _, env = helper.visual_studio_environment()
env['PATH'] = str(tools / 'Scripts') + os.pathsep + env['PATH']
python = tools / 'Scripts/python.exe'
cmake = tools / 'Scripts/cmake.exe'
env.update(AUTOBUILD_ADDRSIZE='64', AUTOBUILD_CONFIGURATION='ReleaseFS_open',
    AUTOBUILD_VSVER=str(major * 10), AUTOBUILD_BUILD_ID='80712',
    AUTOBUILD_WIN_VSTOOLSET='v143', AUTOBUILD_VARIABLES_FILE=str(variables),
    AUTOBUILD_CONFIG_FILE=str(src / 'autobuild.xml'),
    AUTOBUILD_INSTALLABLE_CACHE=str(root / 'dependency-cache'),
    AUTOBUILD=str(tools / 'Scripts/autobuild.exe'))
env['_CL_'] = env.get('_CL_', '') + ' /MP4'
env['LL_BUILD'] = helper.load_build_variables(variables, env) + ' /EHsc'

if '--test-consent' in sys.argv:
    out = here / 'tests'
    out.mkdir(exist_ok=True)
    compiler = install / 'VC/Tools/MSVC' / tool_version / 'bin/Hostx64/x64/cl.exe'
    subprocess.run([str(compiler), '/nologo', '/std:c++17', '/EHsc',
        '/Fe:' + str(out / 'consent-tests.exe'), '/Fo:' + str(out / 'consent-tests.obj'),
        str(here / 'consent_tests.cpp')], env=env, cwd=out, check=True)
    subprocess.run([str(out / 'consent-tests.exe')], check=True, cwd=out)
    sys.exit(0)

args = [str(cmake), '-S', str(src / 'indra'), '-B', str(build),
    '-G', 'Visual Studio 18 2026', '-A', 'x64', '-T', f'v143,version={tool_version}',
    f'-DCMAKE_GENERATOR_INSTANCE={install}', '-DCMAKE_BUILD_TYPE=Release',
    '-DADDRESS_SIZE=64', '-DUNATTENDED=ON', '-DINSTALL_PROPRIETARY=OFF',
    '-DUSE_KDU=OFF', '-DHAVOK=OFF', '-DHAVOK_TPV=OFF', '-DOPENSIM=OFF',
    '-DUSE_FMODSTUDIO=ON', '-DUSE_OPENAL=OFF', '-DUSE_AVX2_OPTIMIZATION=ON',
    '-DNVAPI=ON', '-DUSE_TRACY=OFF', '-DBUGSPLAT_DB=', '-DPACKAGE=OFF', '-DLL_TESTS=OFF',
    '-DVIEWER_CHANNEL=Stellarys Viewer',
    f'-DPYTHON_EXECUTABLE={python}', f'-DPython3_EXECUTABLE={python}',
    f'-DAUTOBUILD_EXECUTABLE={env["AUTOBUILD"]}']
if '--build-only' not in sys.argv:
    subprocess.run(args, env=env, cwd=src, check=True)
if '--configure-only' not in sys.argv:
    subprocess.run([str(cmake), '--build', str(build), '--config', 'Release',
                   '--parallel', '2'], env=env, cwd=src, check=True)
print('Build helper completed', datetime.datetime.now().isoformat())
