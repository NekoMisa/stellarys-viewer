#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-only
"""Run the production mirror sampling function against poisoned unused GPU mips."""
from pathlib import Path
import argparse
import importlib.util
import os
import subprocess


def fragment(text):
    start = text.index('void tapHeroProbe(inout vec3 glossenv')
    end = text.index('\n#else', start)
    return '''#version 400 core
uniform samplerCubeArray heroProbes;
uniform int heroMipCount;
uniform float testGlossiness;
const vec4 clipPlane = vec4(0,0,0,1);
const mat3 env_mat = mat3(1);
const int heroShape = 0;
const mat4 heroBox = mat4(1);
const vec4 heroSphere = vec4(0,0,0,1);
void boxIntersect(vec3 p, vec3 n, mat4 b, out float d, float scale) { d = 1.0; }
float sphereWeight(vec3 p, vec3 n, vec3 c, float r, vec4 v, out float dw) { dw=0.0; return 1.0; }
''' + text[start:end] + '''
out vec4 result;
void main() {
    vec3 color = vec3(0.1,0.2,0.3);
    tapHeroProbe(color, vec3(0,0,-1), vec3(0,0,1), testGlossiness);
    result = vec4(color,1.0);
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-dir', type=Path, required=True)
    parser.add_argument('--reference', type=Path, help='Optional original shader to demonstrate the regression')
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    out = args.work_dir.resolve()
    if os.name != 'nt' or out.is_relative_to(repo):
        parser.error('Run on Windows with a separate output folder.')
    out.mkdir(parents=True, exist_ok=True)
    current = out / 'test-current.frag'
    current.write_text(fragment((repo / 'indra/newview/app_settings/shaders/class3/deferred/reflectionProbeF.glsl').read_text(encoding='utf-8')), encoding='utf-8')
    shaders = [str(current)]
    if args.reference:
        reference = out / 'test-reference.frag'
        reference.write_text(fragment(args.reference.read_text(encoding='utf-8')), encoding='utf-8')
        shaders.insert(0, str(reference))
    spec = importlib.util.spec_from_file_location('toolchain', repo / 'tools/kitty-prototype/toolchain_helper.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    _, install, version, _, env = helper.visual_studio_environment()
    env.update(TEMP=str(out), TMP=str(out))
    compiler = install / 'VC/Tools/MSVC' / version / 'bin/Hostx64/x64/cl.exe'
    exe = out / 'mirror_mip_check.exe'
    subprocess.run([str(compiler), '/nologo', '/std:c++17', '/EHsc', '/W4', '/WX',
                    '/Fe:' + str(exe), '/Fo:' + str(out / 'mirror_mip_check.obj'),
                    str(Path(__file__).with_name('mirror_mip_check.cpp')),
                    '/link', 'opengl32.lib', 'user32.lib', 'gdi32.lib'], env=env, cwd=out, check=True)
    subprocess.run([str(exe), *shaders], env=env, cwd=out, check=True)


if __name__ == '__main__':
    main()
