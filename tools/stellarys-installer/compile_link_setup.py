"""Compile the small Explorer handoff helper using the viewer's MSVC toolchain."""
from pathlib import Path
import importlib.util
import subprocess


def compile_helper(destination):
    repo = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location(
        'stellarys_toolchain', repo / 'tools/kitty-prototype/toolchain_helper.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    _, install, version, _, env = helper.visual_studio_environment()
    compiler = install / 'VC/Tools/MSVC' / version / 'bin/Hostx64/x64/cl.exe'
    destination = Path(destination).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    obj = destination.with_suffix('.obj')
    try:
        subprocess.run([
            str(compiler), '/nologo', '/std:c++17', '/O2', '/MT', '/W4', '/WX',
            '/EHsc', '/DUNICODE', '/D_UNICODE', '/Fo:' + str(obj),
            '/Fe:' + str(destination), str(Path(__file__).with_name('FinishLinkSetup.cpp')),
            '/link', 'ole32.lib', 'oleaut32.lib', 'uuid.lib', 'user32.lib',
            '/SUBSYSTEM:WINDOWS', '/MANIFEST:EMBED',
            "/MANIFESTUAC:level='asInvoker' uiAccess='false'",
        ], env=env, cwd=destination.parent, check=True)
    finally:
        obj.unlink(missing_ok=True)


if __name__ == '__main__':
    import sys
    compile_helper(sys.argv[1])
