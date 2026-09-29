/**
 * @file normaldebugV.glsl
 *
 * $LicenseInfo:firstyear=2023&license=viewerlgpl$
 * Second Life Viewer Source Code
 * Copyright (C) 2023, Linden Research, Inc.
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

in vec3 position;
in vec3 normal;
out vec4 normal_g;
#ifdef HAS_ATTRIBUTE_TANGENT
in vec4 tangent;
out vec4 tangent_g;
#endif

uniform float debug_normal_draw_length;

#ifdef HAS_SKIN
mat3x4 getSkinBlend();
vec3 skinNormal(mat3x4 b, vec3 pos, vec3 dir, mat4 m);
vec4 skinTransformH(mat3x4 b, vec3 pos, mat4 m);
#else
uniform mat3 normal_matrix;
#endif
uniform mat4 projection_matrix;
uniform mat4 modelview_matrix;

// The direction is already in view space.  Avoid reconstructing it by
// subtracting two large transformed points, which loses precision at altitude.
vec4 get_screen_normal(vec4 view_pos, vec3 view_dir)
{
    vec4 world_norm = view_pos;
    world_norm.xyz += debug_normal_draw_length * normalize(view_dir);
    return projection_matrix * world_norm;
}

void main()
{
#ifdef HAS_SKIN
    mat3x4 skin = getSkinBlend();
    vec4 world_pos = skinTransformH(skin, position.xyz, modelview_matrix);
    vec3 view_normal = skinNormal(skin, position.xyz, normal.xyz, modelview_matrix);
#ifdef HAS_ATTRIBUTE_TANGENT
    vec3 view_tangent = skinNormal(skin, position.xyz, tangent.xyz, modelview_matrix);
#endif
#else
    vec4 world_pos = modelview_matrix * vec4(position.xyz, 1.0);
    vec3 view_normal = mat3(modelview_matrix) * normal.xyz;
#ifdef HAS_ATTRIBUTE_TANGENT
    vec3 view_tangent = mat3(modelview_matrix) * tangent.xyz;
#endif
#endif

    gl_Position = projection_matrix * world_pos;
    normal_g = get_screen_normal(world_pos, view_normal);
#ifdef HAS_ATTRIBUTE_TANGENT
    tangent_g = get_screen_normal(world_pos, view_tangent);
#endif
}
