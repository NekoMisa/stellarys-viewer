#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-only
"""Build Stellarys in a separate Windows work directory using MSVC v143."""
from pathlib import Path
import argparse
import importlib.util
import json
import os
import subprocess


def main():
    repo = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-dir', type=Path, required=True)
    parser.add_argument('--tools', type=Path, required=True, help='Existing Python/autobuild/CMake virtual environment')
    parser.add_argument('--build-variables', type=Path, required=True)
    parser.add_argument('--channel-variant', help='Defaults to Windows Beta N for experimental builds')
    parser.add_argument('--certificate-bundle', type=Path, help='Optional trusted PEM CA bundle for build downloads; verification remains enabled')
    parser.add_argument('--jobs', type=int, default=2)
    parser.add_argument('--compiler-jobs', type=int, default=2)
    parser.add_argument('--configure-only', action='store_true')
    parser.add_argument('--build-only', action='store_true')
    args = parser.parse_args()
    if os.name != 'nt' or args.jobs < 1 or args.compiler_jobs < 1:
        parser.error('Windows and positive job counts are required.')
    work = args.work_dir.resolve()
    if work.is_relative_to(repo) or repo.is_relative_to(work / 'build-windows'):
        parser.error('Use a separate build work directory.')
    work.mkdir(parents=True, exist_ok=True)
    (work / 'tmp').mkdir(exist_ok=True)
    tools = args.tools.resolve() / 'Scripts'
    for name in ('python.exe', 'autobuild.exe', 'cmake.exe'):
        if not (tools / name).is_file():
            parser.error('Missing build tool: ' + name)
    metadata = json.loads((repo / 'stellarys-source.json').read_text())
    beta = metadata.get('windows_beta', 0)
    if args.channel_variant is None:
        args.channel_variant = 'Windows Beta ' + str(beta) if beta else ''
    revision = metadata['upstream_version'].split('.')[-1]
    helper_path = repo / 'tools/kitty-prototype/toolchain_helper.py'
    spec = importlib.util.spec_from_file_location('stellarys_toolchain', helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    major, install, version, _, env = helper.visual_studio_environment()
    variables = args.build_variables.resolve()
    env.update(PATH=str(tools) + os.pathsep + env['PATH'],
               TEMP=str(work / 'tmp'), TMP=str(work / 'tmp'),
               AUTOBUILD_ADDRSIZE='64', AUTOBUILD_CONFIGURATION='ReleaseFS_open',
               AUTOBUILD_VSVER=str(major * 10), AUTOBUILD_BUILD_ID=revision,
               AUTOBUILD_WIN_VSTOOLSET='v143', AUTOBUILD_VARIABLES_FILE=str(variables),
               AUTOBUILD_CONFIG_FILE=str(repo / 'autobuild.xml'),
               AUTOBUILD_INSTALLABLE_CACHE=str(work / 'dependency-cache'),
               AUTOBUILD=str(tools / 'autobuild.exe'))
    if args.certificate_bundle:
        bundle = args.certificate_bundle.resolve(strict=True)
        env['SSL_CERT_FILE'] = str(bundle)
    env['_CL_'] = env.get('_CL_', '') + ' /MP' + str(args.compiler_jobs)
    env['LL_BUILD'] = helper.load_build_variables(variables, env) + ' /EHsc'
    build = work / 'build-windows'
    configure = [str(tools / 'cmake.exe'), '-S', str(repo / 'indra'), '-B', str(build),
                 '-G', 'Visual Studio 18 2026' if major == 18 else 'Visual Studio 17 2022',
                 '-A', 'x64', '-T', 'v143,version=' + version,
                 '-DCMAKE_GENERATOR_INSTANCE=' + str(install), '-DCMAKE_BUILD_TYPE=Release',
                 '-DADDRESS_SIZE=64', '-DUNATTENDED=ON', '-DINSTALL_PROPRIETARY=OFF',
                 '-DUSE_KDU=OFF', '-DHAVOK=OFF', '-DHAVOK_TPV=OFF', '-DOPENSIM=OFF',
                 '-DUSE_FMODSTUDIO=ON', '-DUSE_OPENAL=OFF', '-DUSE_AVX2_OPTIMIZATION=ON',
                 '-DNVAPI=ON', '-DUSE_TRACY=OFF', '-DUSE_VELOPACK=OFF', '-DBUGSPLAT_DB=',
                 '-DPACKAGE=OFF', '-DLL_TESTS=OFF', '-DCMAKE_INSTALL_PREFIX=' + str(work / 'unused-install'),
                 '-DSTELLARYS_CHANNEL_VARIANT=' + args.channel_variant,
                 '-DPYTHON_EXECUTABLE=' + str(tools / 'python.exe'),
                 '-DPython3_EXECUTABLE=' + str(tools / 'python.exe'),
                 '-DAUTOBUILD_EXECUTABLE=' + env['AUTOBUILD']]
    if not args.build_only:
        subprocess.run(configure, env=env, cwd=repo, check=True)
    if not args.configure_only:
        subprocess.run([str(tools / 'cmake.exe'), '--build', str(build), '--config', 'Release',
                        '--parallel', str(args.jobs)], env=env, cwd=repo, check=True)


if __name__ == '__main__':
    main()
