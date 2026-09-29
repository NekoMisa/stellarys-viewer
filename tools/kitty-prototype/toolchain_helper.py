"""Experimental Black Dragon AMD port: isolated Windows source build.

Run with Python 3.11+ on Windows. Requires Git and VS 2022/2026 with v143.
This helper has not been executed on Windows; see README.md.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

BASE = "b2ca434b39bcd93aff0e23414999dddd73527e05"
REPO = "https://github.com/NiranV/Black-Dragon-Viewer.git"
HERE = Path(__file__).resolve().parent


def run(argv, **kwargs):
    print("\n> " + subprocess.list2cmdline([str(a) for a in argv]), flush=True)
    return subprocess.run([str(a) for a in argv], check=True, **kwargs)


def capture(argv, **kwargs):
    return subprocess.check_output([str(a) for a in argv], text=True, **kwargs).strip()


def load_build_variables(path, env):
    values = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r'(\w+)="(.*)"', line)
        if not match:
            raise RuntimeError("Unrecognized build-variable line: " + line)
        name, value = match.groups()
        def expand(m):
            key = m.group(1) or m.group(2)
            if key not in values and key not in env:
                raise RuntimeError("Missing build variable " + key)
            return values.get(key, env.get(key))
        values[name] = re.sub(r'\$\{(\w+)\}|\$(\w+)', expand, value)
    return values["LL_BUILD_WINDOWS_RELEASE"]


def visual_studio_environment():
    vswhere = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Microsoft Visual Studio/Installer/vswhere.exe"
    if not vswhere.is_file():
        raise RuntimeError("Visual Studio Installer was not found. Install VS with Desktop development with C++ and MSVC v143.")
    entries = json.loads(capture([vswhere, "-products", "*", "-prerelease", "-format", "json", "-utf8"]))
    candidates = []
    for entry in entries:
        major = int(entry["installationVersion"].split(".")[0])
        if major not in (17, 18):
            continue
        install = Path(entry["installationPath"])
        for tool in (install / "VC/Tools/MSVC").glob("14.*"):
            version = tuple(int(n) for n in tool.name.split("."))
            if 30 <= version[1] < 50 and (tool / "bin/Hostx64/x64/cl.exe").is_file():
                candidates.append((major, version, install, tool.name, entry["installationVersion"]))
    if not candidates:
        raise RuntimeError("MSVC v143 x64 tools were not found. Add 'MSVC v143 - VS 2022 C++ x64/x86 build tools' in Visual Studio Installer.")
    major, _, install, version, installation_version = max(candidates)
    vcvars = install / "VC/Auxiliary/Build/vcvarsall.bat"
    # Paths returned by Microsoft's local installer are quoted for cmd.exe.
    command = f'call "{vcvars}" x64 -vcvars_ver={version} >nul && set'
    if not vcvars.is_file():
        vcvars = install / "Common7/Tools/VsDevCmd.bat"
        if not vcvars.is_file():
            raise RuntimeError("Visual Studio developer environment script is missing")
        command = f'call "{vcvars}" -no_logo -arch=x64 -host_arch=x64 -vcvars_ver={version} >nul && set'
    # cmd.exe does not use the C-runtime quote escaping applied to list argv.
    comspec = os.environ.get("COMSPEC", "cmd.exe")
    output = subprocess.check_output(f'"{comspec}" /d /s /c "{command}"', text=True).strip()
    env = os.environ.copy()
    for line in output.splitlines():
        key, sep, value = line.partition("=")
        if sep and key:
            # Avoid duplicate PATH/Path keys when passing the Windows environment.
            for existing in list(env):
                if existing.upper() == key.upper():
                    del env[existing]
            env[key.upper()] = value
    return major, install, version, installation_version, env


def assemble_viewer(source, build, destination):
    """Use the upstream file manifest, but omit creation of an NSIS installer."""
    path = source / "indra/newview/viewer_manifest.py"
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("bd_viewer_manifest", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    def portable_finish(self):
        self.package_file = self.final_exe()
    module.Windows_x86_64_Manifest.package_finish = portable_finish
    destination.mkdir(parents=True, exist_ok=True)
    sys.argv = [str(path), "--actions=copy package", "--platform=windows", "--arch=x86_64",
                "--configuration=Release", "--buildtype=Release", "--channel=Black Dragon Black Kitty Fix 0.1.0 Preview",
                "--grid=agni", "--bugsplat=", "--discord=OFF", "--openal=ON", "--tracy=OFF", "--fmodstudio=OFF", "--portable=ON",
                f"--source={path.parent}", f"--artwork={path.parent}",
                f"--build={build / 'newview'}", f"--dest={destination}",
                f"--versionfile={build / 'newview/viewer_version.txt'}"]
    previous_cwd = Path.cwd()
    try:
        # The upstream manifest writes ../build_data.json relative to cwd.
        os.chdir(build / "newview")
        module.main(extra=[dict(name=name, description=name, default=default)
                           for name, default in (("bugsplat", ""), ("discord", "OFF"),
                                                 ("openal", "ON"), ("tracy", "OFF"),
                                                 ("fmodstudio", "OFF"), ("portable", "OFF"))])
    finally:
        os.chdir(previous_cwd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, default=Path(r"C:\BD-AMD-Test"))
    parser.add_argument("--jobs", type=int, default=2, help="Concurrent MSBuild projects (default: 2)")
    parser.add_argument("--configure-only", action="store_true")
    parser.add_argument("--build-only", action="store_true", help="Compile without updating the portable viewer folder")
    args = parser.parse_args()
    if os.name != "nt":
        parser.error("This helper must run on Windows, using Windows Python (not WSL).")
    if sys.version_info < (3, 11):
        parser.error("Python 3.11 or newer is required.")
    if args.jobs < 1:
        parser.error("--jobs must be at least 1.")
    if not shutil.which("git"):
        parser.error("Install Git for Windows and open a new terminal first.")
    work = args.work_dir.resolve()
    work.mkdir(parents=True, exist_ok=True)
    venv = work / "python-tools"
    python = venv / "Scripts/python.exe"
    if Path(sys.prefix).resolve() != venv:
        if not python.exists():
            run([sys.executable, "-m", "venv", venv])
        run([python, "-m", "pip", "install", "autobuild==3.10.2", "cmake>=4.2,<5", "llsd"])
        run([python, HERE / "build_windows.py", *sys.argv[1:]])
        return

    major, install, tool_version, installation_version, env = visual_studio_environment()
    env["PATH"] = str(venv / "Scripts") + os.pathsep + env.get("PATH", "")
    env.update(AUTOBUILD_ADDRSIZE="64", AUTOBUILD_CONFIGURATION="ReleaseOS",
               AUTOBUILD_VSVER=str(major * 10), AUTOBUILD_BUILD_ID="57700")
    env["AUTOBUILD_WIN_VSTOOLSET"] = "v143"
    # The project enables /MP with no limit; cap per-project compiler processes
    # so two MSBuild projects do not exhaust a 32 GB machine.
    env["_CL_"] = env.get("_CL_", "") + " /MP4"
    env["AUTOBUILD"] = str(venv / "Scripts/autobuild.exe")
    env["AUTOBUILD_INSTALLABLE_CACHE"] = str(work / "dependency-cache")
    source = work / "source"
    if not source.exists():
        source.mkdir()
        run(["git", "init", source], env=env)
        run(["git", "-C", source, "config", "core.autocrlf", "false"], env=env)
        run(["git", "-C", source, "remote", "add", "origin", REPO], env=env)
        run(["git", "-C", source, "fetch", "--depth=1", "origin", BASE], env=env)
        run(["git", "-C", source, "checkout", "--detach", "FETCH_HEAD"], env=env)
    if capture(["git", "-C", source, "rev-parse", "HEAD"], env=env) != BASE:
        raise RuntimeError("Existing source is not the expected revision. Choose a new --work-dir.")
    patch = HERE / "black-dragon-amd.patch"
    reverse = subprocess.run(["git", "-C", str(source), "apply", "--reverse", "--check", str(patch)],
                             env=env, capture_output=True)
    if reverse.returncode != 0:
        run(["git", "-C", source, "apply", "--check", patch], env=env)
        run(["git", "-C", source, "apply", patch], env=env)
    else:
        print("AMD patch is already present.")
    env["AUTOBUILD_VARIABLES_FILE"] = str(source / "variables/variables")
    env["AUTOBUILD_CONFIG_FILE"] = str(source / "autobuild.xml")
    env["LL_BUILD"] = load_build_variables(source / "variables/variables", env) + " /EHsc"
    build = work / f"build-vs{major}-v143"
    cmake = venv / "Scripts/cmake.exe"
    generator = "Visual Studio 18 2026" if major == 18 else "Visual Studio 17 2022"
    run([cmake, "-S", source / "indra", "-B", build, "-G", generator, "-A", "x64",
         "-T", f"v143,version={tool_version}", f"-DCMAKE_GENERATOR_INSTANCE={install}",
         "-DCMAKE_BUILD_TYPE=Release", "-DADDRESS_SIZE=64", "-DUNATTENDED=ON",
         "-DINSTALL_PROPRIETARY=OFF", "-DUSE_KDU=OFF", "-DHAVOK=OFF", "-DHAVOK_TPV=OFF",
         "-DUSE_FMODSTUDIO=OFF", "-DUSE_OPENAL=ON", "-DOPENAL=ON", "-DNVAPI=OFF",
         "-DUSE_DISCORD=OFF", "-DUSE_TRACY=OFF", "-DBUGSPLAT_DB=", "-DPACKAGE=OFF",
         "-DLL_TESTS=OFF", "-DVIEWER_CHANNEL=Black Dragon Black Kitty Fix 0.1.0 Preview",
         f"-DPYTHON_EXECUTABLE={python}", f"-DPython3_EXECUTABLE={python}",
         f"-DAUTOBUILD_EXECUTABLE={env['AUTOBUILD']}"], env=env, cwd=source)
    if args.configure_only:
        print("Configured solution:", build / "BlackDragon.sln")
        return
    run([cmake, "--build", build, "--config", "Release", "--parallel", args.jobs], env=env, cwd=source)
    if args.build_only:
        print("Build completed; portable viewer folder was not updated.")
        return
    os.environ.update(env)
    output = work / "viewer"
    assemble_viewer(source, build, output)
    print("\nBuild and file assembly completed:", output)
    print("This is an experimental build. Test your affected mesh, shadows and motion blur.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print("\nBUILD STOPPED:", error, file=sys.stderr)
        print("Keep the complete log and ask ChatGPT to investigate. The installed viewer was not modified.", file=sys.stderr)
        sys.exit(1)
