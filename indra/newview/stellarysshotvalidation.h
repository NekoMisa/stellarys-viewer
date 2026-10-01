// SPDX-License-Identifier: LGPL-2.1-only
#ifndef STELLARYS_SHOT_VALIDATION_H
#define STELLARYS_SHOT_VALIDATION_H
#include <array>
#include <cmath>
#include <string>
namespace StellarysShot
{
inline bool validName(const std::string& name)
{
    if (name.empty() || name.size() > 80) return false;
    for (unsigned char c : name) if (c < 32 || c == 127) return false;
    return true;
}
inline bool inRange(double value, double minimum, double maximum)
{ return std::isfinite(value) && value >= minimum && value <= maximum; }
inline bool validPosition(const std::array<double, 3>& position)
{
    return inRange(position[0], 0, 4294967295.) &&
           inRange(position[1], 0, 4294967295.) &&
           inRange(position[2], -1000000., 1000000.);
}
inline bool validCamera(const std::array<double, 3>& position, const std::array<double, 3>& focus, double roll)
{
    if (!validPosition(position) || !validPosition(focus) || !inRange(roll, -3.142, 3.142)) return false;
    double distance = 0;
    for (unsigned i = 0; i < 3; ++i) distance += (position[i]-focus[i])*(position[i]-focus[i]);
    return inRange(distance, 0.000001, 65536.*65536.);
}
inline bool validDimensions(int width, int height)
{ return width >= 32 && width <= 6016 && height >= 32 && height <= 6016; }
inline bool samePlace(const std::string& grid, const std::string& region,
                      const std::string& current_grid, const std::string& current_region)
{ return !grid.empty() && !region.empty() && grid == current_grid && region == current_region; }
struct SettingRange { const char* name; double minimum; double maximum; };
inline constexpr std::array<SettingRange, 10> lensRanges = {{
    {"CameraAngle", 0.01, 3.1}, {"CameraFieldOfView", 0.1, 180.},
    {"CameraFNumber", 0.01, 128.}, {"CameraFocalLength", 0.01, 1000.},
    {"CameraFocusTransitionTime", 0., 120.}, {"CameraMaxCoF", 0., 1000.},
    {"CameraDoFResScale", 0.25, 1.}, {"RenderExposure", 0., 20.},
    {"RenderTonemapMix", 0., 1.}, {"RenderGlowStrength", 0., 10.}
}};
inline constexpr std::array<const char*, 6> flags = {{
    "RenderDepthOfField", "FSFocusPointLocked", "FSFocusPointFollowsPointer",
    "RenderGlow", "RenderGlowHDR", "RenderDisableVintageMode"
}};
}
#endif
