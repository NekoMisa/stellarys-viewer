/**
 * @file diffuseV.glsl
 *
 * $LicenseInfo:firstyear=2007&license=viewerlgpl$
 * Second Life Viewer Source Code
 * Copyright (C) 2007, Linden Research, Inc.
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation;
 * version 2.1 of the License only.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * Linden Research, Inc., 945 Battery Street, San Francisco, CA  94111  USA
 * $/LicenseInfo$
 */

#ifdef RIGGED_PRECISE_MATH
invariant gl_Position;
precise gl_Position;
#endif

uniform mat3 normal_matrix;
uniform mat4 texture_matrix0;
uniform mat4 modelview_projection_matrix;

in vec3 position;
in vec4 diffuse_color;
in vec3 normal;
in vec2 texcoord0;

out vec3 vary_normal;

out vec4 vertex_color;
out vec2 vary_texcoord0;
out vec3 vary_position;

void passTextureIndex();

uniform mat4 modelview_matrix;

#ifdef HAS_SKIN
mat3x4 getSkinBlend();
vec3 skinNormal(mat3x4 b, vec3 pos, vec3 dir, mat4 m);
vec4 skinTransformH(mat3x4 b, vec3 pos, mat4 m);
uniform mat4 projection_matrix;

#endif

void main()
{
#ifdef HAS_SKIN
    mat3x4 skin = getSkinBlend();
    vec4 pos = skinTransformH(skin, position.xyz, modelview_matrix);
    vary_position = pos.xyz;
    gl_Position = projection_matrix * pos;
    vary_normal = normalize(skinNormal(skin, position.xyz, normal.xyz, modelview_matrix));
#else
    vary_position = (modelview_matrix * vec4(position.xyz, 1.0)).xyz;
    gl_Position = modelview_projection_matrix * vec4(position.xyz, 1.0);
    vary_normal = normalize(normal_matrix * normal);
#endif

    vary_texcoord0 = (texture_matrix0 * vec4(texcoord0,0,1)).xy;

    passTextureIndex();

    vertex_color = diffuse_color;
}
