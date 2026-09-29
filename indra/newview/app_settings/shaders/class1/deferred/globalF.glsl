/**
 * @file class1/deferred/globalF.glsl
 *
 * $LicenseInfo:firstyear=2024&license=viewerlgpl$
 * Second Life Viewer Source Code
 * Copyright (C) 2024, Linden Research, Inc.
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


 // Global helper functions included in every fragment shader
 // DO NOT declare sampler uniforms here as OS X doesn't compile
 // them out

uniform float mirror_flag;
uniform vec4 clipPlane;
uniform float clipSign;

void mirrorClip(vec3 pos)
{
    if (mirror_flag > 0)
    {
        if ((dot(pos.xyz, clipPlane.xyz) + clipPlane.w) < 0.0)
        {
                discard;
        }
    }
}

vec4 encodeNormal(vec3 n, float env, float gbuffer_flag)
{
    // The equivalent polar form avoids cancellation in 1 + z near the south pole.
    float z = clamp(n.z, -1.0, 1.0);
    vec2 encoded;
    if (z < 0.0)
    {
        float xy2 = dot(n.xy, n.xy);
        vec2 direction = xy2 > 0.0 ? n.xy * inversesqrt(xy2) : vec2(1.0, 0.0);
        encoded = direction * sqrt((1.0 - z) * 0.125);
    }
    else
    {
        encoded = n.xy / sqrt(8.0 * z + 8.0);
    }
    return vec4(encoded + 0.5, env, gbuffer_flag);
}

vec4 decodeNormal(vec4 norm)
{
    vec2 fenc = norm.xy*4-2;
    // UNORM quantization can put an encoded south-pole normal outside the disk.
    float f = min(dot(fenc,fenc), 4.0);
    float g = sqrt(max(1-f/4, 0.0));
    vec4 n;
    n.xy = fenc*g;
    n.z = 1-f/2;
    n.w = norm.w;
    return n;
}

// Widen a specular lobe by the normal variation lost when a normal map is filtered to a pixel.
// Without this, the averaged normal still uses the authored sharp lobe and highlights can
// collapse into isolated bright pixels as the camera moves across a rigged avatar.
float filterSpecularRoughness(float perceptualRoughness, vec3 n)
{
    const float SPEC_AA_VARIANCE  = 0.15;
    const float SPEC_AA_THRESHOLD = 0.25;

    vec3 du = dFdx(n);
    vec3 dv = dFdy(n);
    float variance = SPEC_AA_VARIANCE * (dot(du, du) + dot(dv, dv));
    float kernel = min(2.0 * variance, SPEC_AA_THRESHOLD);

    float alpha = perceptualRoughness * perceptualRoughness;
    return sqrt(sqrt(clamp(alpha * alpha + kernel, 0.0, 1.0)));
}
