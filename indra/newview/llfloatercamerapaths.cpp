// SPDX-License-Identifier: LGPL-2.1-only
#include "llviewerprecompiledheaders.h"
#include "llfloatercamerapaths.h"
#include "llagent.h"
#include "llagentcamera.h"
#include "llagentpilot.h"
#include "llbutton.h"
#include "llcheckboxctrl.h"
#include "llcombobox.h"
#include "lldir.h"
#include "llfile.h"
#include "llfloaterreg.h"
#include "lllineeditor.h"
#include "llnotificationsutil.h"
#include "llscrolllistctrl.h"
#include "llsdserialize.h"
#include "llsdutil_math.h"
#include "llsliderctrl.h"
#include "llspinctrl.h"
#include "llstartup.h"
#include "lltextbox.h"
#include "llviewercamera.h"
#include "llviewercontrol.h"
#include "llviewerjoystick.h"
#include "llviewerobject.h"
#include "llviewernetwork.h"
#include "llviewerregion.h"
#include "rlvactions.h"
#include <fstream>

namespace
{
using namespace StellarysCameraPath;
constexpr S32 MAX_BYTES = 2 * 1024 * 1024, MAX_PATHS = 20;
std::string   filename()
{ return gDirUtilp->getExpandedFilename(LL_PATH_USER_SETTINGS, "stellarys_camera_paths.xml"); }
bool readBytes(std::string& bytes)
{
    bytes.clear();
    if (!LLFile::isfile(filename()))
        return true;
    llifstream input(filename(), std::ios::binary);
    if (!input.good())
        return false;
    input.seekg(0, std::ios::end);
    const auto size = input.tellg();
    input.seekg(0);
    if (size <= 0 || size > MAX_BYTES)
        return false;
    bytes.resize(static_cast<std::size_t>(size));
    input.read(&bytes[0], static_cast<std::streamsize>(size));
    return input.good();
}
bool vec(const LLSD& value, Vec& out)
{
    if (!value.isArray() || value.size() != 3)
        return false;
    for (S32 i = 0; i < 3; ++i)
    {
        if (!value[i].isReal() && !value[i].isInteger())
            return false;
        out[i] = value[i].asReal();
    }
    return true;
}
bool decode(const LLSD& path, std::vector<Frame>& frames)
{
    frames.clear();
    if (!path.isMap() || !path["grid"].isString() || path["grid"].asString().empty() || path["grid"].asString().size() > 256 ||
        !path["region"].isUUID() || path["region"].asUUID().isNull() || !path["frames"].isArray() || path["frames"].size() < 1 ||
        path["frames"].size() > static_cast<S32>(MAX_FRAMES))
        return false;
    if (path.has("motion") && (!path["motion"].isString() || (path["motion"].asString() != "curve" && path["motion"].asString() != "ease" &&
                                                              path["motion"].asString() != "linear")))
        return false;
    if (path.has("repeat") &&
        (!path["repeat"].isString() ||
         (path["repeat"].asString() != "none" && path["repeat"].asString() != "closed" && path["repeat"].asString() != "reverse")))
        return false;
    if (path.has("delay") && (!path["delay"].isReal() || !StellarysShot::inRange(path["delay"].asReal(), 0, 60)))
        return false;
    for (auto it = path["frames"].beginArray(); it != path["frames"].endArray(); ++it)
    {
        const auto& data = *it;
        Frame       f;
        if (!vec(data["position"], f.position) || !vec(data["focus"], f.focus) || !data["roll"].isReal() || !data["fov"].isReal() ||
            !data["seconds"].isReal())
            return false;
        f.roll    = data["roll"].asReal();
        f.fov     = data["fov"].asReal();
        f.seconds = data["seconds"].asReal();
        if (data.has("cut"))
        {
            if (!data["cut"].isBoolean())
                return false;
            f.cut = data["cut"].asBoolean();
        }
        frames.push_back(f);
    }
    return valid(frames);
}
Motion motion(const LLFloaterCameraPaths* floater)
{
    const std::string value = floater->getChild<LLComboBox>("motion")->getValue().asString();
    return value == "linear" ? Motion::Linear : value == "ease" ? Motion::Ease : Motion::Curve;
}
Repeat repeat(const LLFloaterCameraPaths* floater)
{
    const std::string value = floater->getChild<LLComboBox>("repeat")->getValue().asString();
    return value == "closed" ? Repeat::Closed : value == "reverse" ? Repeat::Reverse : Repeat::Once;
}
bool keysMovingCamera()
{
    return gAgentCamera.getOrbitUpKey() || gAgentCamera.getOrbitDownKey() || gAgentCamera.getOrbitLeftKey() ||
           gAgentCamera.getOrbitRightKey() || gAgentCamera.getOrbitInKey() || gAgentCamera.getOrbitOutKey() || gAgentCamera.getPanUpKey() ||
           gAgentCamera.getPanDownKey() || gAgentCamera.getPanLeftKey() || gAgentCamera.getPanRightKey() || gAgentCamera.getPanInKey() ||
           gAgentCamera.getPanOutKey() || gAgentCamera.getRollLeftKey() || gAgentCamera.getRollRightKey();
}
} // namespace

LLFloaterCameraPaths::LLFloaterCameraPaths(const LLSD& key) : LLFloater(key)
{
}
LLFloaterCameraPaths::~LLFloaterCameraPaths()
{
    if (mPreview)
        gAgentCamera.setCinematicFOV(-1.f);
}
bool LLFloaterCameraPaths::postBuild()
{
    mPaths    = getChild<LLComboBox>("paths");
    mName     = getChild<LLLineEditor>("path_name");
    mList     = getChild<LLScrollListCtrl>("frames");
    mSeconds  = getChild<LLSpinCtrl>("seconds");
    mDelay    = getChild<LLSpinCtrl>("delay");
    mTimeline = getChild<LLSliderCtrl>("timeline");
    mPaths->setCommitCallback(
        [this](LLUICtrl*, const LLSD&)
        {
            if (!mUpdating)
                requestSelect(mPaths->getValue().asString());
        });
    mList->setCommitCallback(
        [this](LLUICtrl*, const LLSD&)
        {
            if (!mUpdating)
                frameSelected();
        });
    auto button = [this](const char* name, auto action)
    {
        getChild<LLButton>(name)->setCommitCallback([action](LLUICtrl*, const LLSD&) { action(); });
    };
    button("new_path", [this] { requestSelect(""); });
    button("reload", [this] { requestSelect("", true); });
    button("save_path", [this] { savePath(); });
    button("delete_path", [this] { deletePath(); });
    button("add", [this] { captureFrame(false); });
    button("replace", [this] { captureFrame(true); });
    button("remove", [this] { removeFrame(); });
    button("up", [this] { moveFrame(-1); });
    button("down", [this] { moveFrame(1); });
    button("view_frame", [this] { viewFrame(); });
    button("play", [this] { play(); });
    button("stop",
           [this]
           {
               stop(true);
               message("Preview stopped.");
           });
    mSeconds->setCommitCallback(
        [this](LLUICtrl*, const LLSD&)
        {
            const S32 i = mList->getFirstSelectedIndex();
            if (mUpdating || mPreview || i < 0)
                return;
            auto frames       = mFrames;
            frames[i].seconds = mSeconds->getValue().asReal();
            if (!valid(frames))
            {
                message("Use 0.1-600 seconds per leg, at most one hour for the whole loop.");
                return;
            }
            mFrames = std::move(frames);
            mDirty  = true;
            refreshFrames(i);
        });
    getChild<LLComboBox>("transition")
        ->setCommitCallback(
            [this](LLUICtrl* ctrl, const LLSD&)
            {
                const S32 i = mList->getFirstSelectedIndex();
                if (mUpdating || mPreview || i < 0)
                    return;
                auto frames   = mFrames;
                frames[i].cut = ctrl->getValue().asString() == "cut";
                if (!valid(frames))
                {
                    message("Shorten the path to at most one hour before adding more movement.");
                    refreshFrames(i);
                    return;
                }
                mFrames = std::move(frames);
                mDirty  = true;
                refreshFrames(i);
            });
    mTimeline->setCommitCallback(
        [this](LLUICtrl*, const LLSD&)
        {
            if (!mUpdating)
                seek(total() * mTimeline->getValueF32() / 100.);
        });
    mName->setKeystrokeCallback([](LLLineEditor*, void* p) { static_cast<LLFloaterCameraPaths*>(p)->refreshControls(); }, this);
    getChild<LLComboBox>("delay_choice")
        ->setCommitCallback(
            [this](LLUICtrl* ctrl, const LLSD&)
            {
                const auto choice = ctrl->getValue().asString();
                if (choice != "custom")
                    mDelay->setValue(std::stod(choice));
                mDirty = !mFrames.empty();
                refreshControls();
            });
    for (const char* name : { "repeat", "motion", "delay" })
        getChild<LLUICtrl>(name)->setCommitCallback(
            [this](LLUICtrl*, const LLSD&)
            {
                mDirty = !mFrames.empty();
                refreshControls();
            });
    return true;
}
void LLFloaterCameraPaths::onOpen(const LLSD&)
{
    if (!mLoaded)
    {
        load();
        selectPath("");
    }
    populate();
    refreshFrames();
}
void LLFloaterCameraPaths::onClose(bool quitting)
{ stop(!quitting); }
void LLFloaterCameraPaths::message(const std::string& text)
{ getChild<LLTextBox>("status")->setText(text); }
void LLFloaterCameraPaths::load()
{
    mLoaded   = true;
    mWritable = true;
    mSaved    = LLSD::emptyMap();
    if (!readBytes(mLoadedBytes))
    {
        mWritable = false;
        message("Saved paths could not be read. The file is unchanged.");
        return;
    }
    if (mLoadedBytes.empty())
        return;
    std::istringstream input(mLoadedBytes);
    LLSD               data;
    std::vector<Frame> frames;
    bool               ok = LLSDSerialize::fromXML(data, input) > 0 && data["schema"].isInteger() && data["schema"].asInteger() == 1 &&
                            data["paths"].isMap() && data["paths"].size() <= MAX_PATHS;
    if (ok)
        for (auto it = data["paths"].beginMap(); it != data["paths"].endMap(); ++it)
            if (!StellarysShot::validName(it->first) || !decode(it->second, frames))
            {
                ok = false;
                break;
            }
    if (!ok)
    {
        mWritable = false;
        message("Saved paths use an invalid or newer format. The file is unchanged.");
        return;
    }
    mSaved = data["paths"];
}
bool LLFloaterCameraPaths::write(const LLSD& paths)
{
    if (!mWritable)
        return false;
    std::string current;
    if (!readBytes(current) || current != mLoadedBytes)
    {
        message("Saved paths changed in another viewer. Use Reload before saving; your draft is still here.");
        return false;
    }
    LLSD data;
    data["schema"] = 1;
    data["paths"]  = paths;
    std::ostringstream buffer;
    LLSDSerialize::toPrettyXML(data, buffer);
    const auto bytes = buffer.str();
    if (bytes.size() > MAX_BYTES)
    {
        message("Saved paths are full. Delete an unused path first.");
        return false;
    }
    LLUUID id;
    id.generate();
    const auto temp = filename() + "." + id.asString() + ".tmp";
    llofstream output(temp, std::ios::binary | std::ios::trunc);
    output.write(bytes.data(), bytes.size());
    output.flush();
    const bool ok = output.good();
    output.close();
    if (!ok || !readBytes(current) || current != mLoadedBytes || LLFile::rename(temp, filename()) != 0)
    {
        LLFile::remove(temp);
        message("Could not save paths. Your previous file and draft are unchanged.");
        return false;
    }
    mLoadedBytes = bytes;
    mSaved       = paths;
    return true;
}
void LLFloaterCameraPaths::selectPath(const std::string& name)
{
    stop(true);
    mSelected = name;
    mFrames.clear();
    mGrid.clear();
    mRegion.setNull();
    mDirty = false;
    if (mSaved.has(name))
    {
        decode(mSaved[name], mFrames);
        mGrid   = mSaved[name]["grid"].asString();
        mRegion = mSaved[name]["region"].asUUID();
    }
    const LLSD& saved = mSaved;
    const LLSD& data  = saved[name];
    getChild<LLComboBox>("motion")->setValue(data.has("motion") ? data["motion"].asString() : "curve");
    getChild<LLComboBox>("repeat")->setValue(data.has("repeat") ? data["repeat"].asString() : "none");
    const double delay = data.has("delay") ? data["delay"].asReal() : 5.;
    mDelay->setValue(delay);
    getChild<LLComboBox>("delay_choice")->setValue(delay == 0 ? "0" : delay == 5 ? "5" : delay == 10 ? "10" : "custom");
    mName->setText(name);
    populate();
    refreshFrames(mFrames.empty() ? -1 : 0);
    if (mWritable)
        message(mFrames.empty() ? "Position your camera, then Add keyframe. Add at least two to play."
                                : "Path loaded. Camera movement stays in its original region.");
}
void LLFloaterCameraPaths::requestSelect(const std::string& name, bool reload)
{
    if (mPreview)
    {
        populate();
        return;
    }
    if (!mDirty)
    {
        if (reload)
            load();
        selectPath(name);
        return;
    }
    populate();
    auto handle = getHandle();
    LLNotificationsUtil::add("StellarysDiscardCameraPath", LLSD(), LLSD(),
                             [handle, name, reload](const LLSD& n, const LLSD& r)
                             {
                                 auto* self = dynamic_cast<LLFloaterCameraPaths*>(handle.get());
                                 if (self && LLNotificationsUtil::getSelectedOption(n, r) == 0)
                                 {
                                     if (reload)
                                         self->load();
                                     self->selectPath(name);
                                 }
                                 return false;
                             });
}
void LLFloaterCameraPaths::populate()
{
    mUpdating = true;
    mPaths->removeall();
    mPaths->add("New / unsaved path", LLSD(""));
    for (auto it = mSaved.beginMap(); it != mSaved.endMap(); ++it)
        mPaths->add(it->first, LLSD(it->first));
    mPaths->setValue(mSelected);
    mUpdating = false;
    refreshControls();
}
double LLFloaterCameraPaths::total() const
{ return repeatDuration(mFrames, repeat(this)); }
void LLFloaterCameraPaths::refreshFrames(S32 selection)
{
    mUpdating = true;
    mList->deleteAllItems();
    for (std::size_t i = 0; i < mFrames.size(); ++i)
    {
        LLSD row;
        row["value"]                = static_cast<S32>(i);
        row["columns"][0]["column"] = "frame";
        row["columns"][0]["value"]  = "Keyframe " + std::to_string(i + 1);
        row["columns"][1]["column"] = "seconds";
        row["columns"][1]["value"]  = mFrames[i].cut ? "Cut (instant)" : llformat("%.1f s", mFrames[i].seconds);
        mList->addElement(row);
    }
    if (selection >= 0 && !mFrames.empty())
        mList->selectNthItem(llmin(selection, static_cast<S32>(mFrames.size() - 1)));
    mUpdating = false;
    frameSelected();
}
void LLFloaterCameraPaths::frameSelected()
{
    const S32 i = mList->getFirstSelectedIndex();
    if (i >= 0)
    {
        mSeconds->setValue(mFrames[i].seconds);
        getChild<LLComboBox>("transition")->setValue(mFrames[i].cut ? "cut" : "move");
    }
    refreshControls();
}
void LLFloaterCameraPaths::refreshControls()
{
    const S32  i        = mList->getFirstSelectedIndex();
    const bool selected = i >= 0;
    for (const char* name : { "paths", "path_name", "new_path", "reload", "motion", "repeat", "delay_choice" })
        getChildView(name)->setEnabled(!mPreview);
    getChildView("delay")->setEnabled(!mPreview && getChild<LLComboBox>("delay_choice")->getValue().asString() == "custom");
    getChildView("seconds")->setEnabled(!mPreview && selected && !mFrames[i].cut);
    getChildView("transition")->setEnabled(!mPreview && selected);
    getChildView("add")->setEnabled(!mPreview && mFrames.size() < MAX_FRAMES);
    getChildView("replace")->setEnabled(!mPreview && selected);
    getChildView("remove")->setEnabled(!mPreview && selected);
    getChildView("up")->setEnabled(!mPreview && i > 0);
    getChildView("down")->setEnabled(!mPreview && selected && i + 1 < static_cast<S32>(mFrames.size()));
    getChildView("save_path")->setEnabled(!mPreview && mWritable && !mFrames.empty());
    getChild<LLButton>("save_path")->setLabel(mSaved.has(mName->getText()) ? "Replace path" : "Save path");
    getChildView("delete_path")->setEnabled(!mPreview && mWritable && mSaved.has(mSelected));
    getChildView("play")->setEnabled(mFrames.size() > 1 && total() > 0);
    getChildView("view_frame")->setEnabled(selected);
    getChildView("timeline")->setEnabled(mFrames.size() > 1 && total() > 0);
    getChildView("stop")->setEnabled(mPreview);
    using State        = Clock::State;
    const bool running = mClock.state == State::Playing || mClock.state == State::Countdown;
    getChild<LLButton>("play")->setLabel(running ? "Pause" : mStarted && mClock.state == State::Paused ? "Resume" : "Play");
    getChild<LLTextBox>("summary")->setText(
        llformat("%d keyframes  |  %.1f seconds%s", static_cast<S32>(mFrames.size()), total(), mDirty ? "  |  Unsaved changes" : ""));
}
bool LLFloaterCameraPaths::capture(Frame& f)
{
    if (LLStartUp::getStartupState() != STATE_STARTED || !gAgent.getRegion() || !gAgentCamera.cameraThirdPerson() ||
        LLViewerJoystick::getInstance()->getOverrideCamera())
    {
        message("Log in, use third-person camera and turn off Flycam before adding a keyframe.");
        return false;
    }
    const auto p = gAgentCamera.getCameraPositionGlobal(), look = gAgentCamera.getFocusGlobal();
    for (unsigned i = 0; i < 3; ++i)
    {
        f.position[i] = p.mdV[i];
        f.focus[i]    = look.mdV[i];
    }
    f.roll = std::remainder(static_cast<double>(gAgentCamera.getCameraRoll()), 2 * PI);
    f.fov  = LLViewerCamera::getInstance()->getView();
    if (!valid(f))
    {
        message("This camera position or lens value cannot be saved.");
        return false;
    }
    return true;
}
void LLFloaterCameraPaths::captureFrame(bool replace)
{
    if (mPreview)
        return;
    Frame     f;
    const S32 i = mList->getFirstSelectedIndex();
    if (replace && i < 0)
        return;
    if (!replace && mFrames.size() >= MAX_FRAMES)
        return;
    if (!capture(f))
        return;
    const auto grid   = LLGridManager::getInstance()->getGrid();
    const auto region = gAgent.getRegion()->getRegionID();
    if (!mFrames.empty() && !StellarysShot::samePlace(mGrid, mRegion.asString(), grid, region.asString()))
    {
        message("Return to this path's original region, or start a New path.");
        return;
    }
    auto updated = mFrames;
    if (replace)
    {
        f.seconds  = updated[i].seconds;
        f.cut      = updated[i].cut;
        updated[i] = f;
    }
    else
        updated.push_back(f);
    if (!valid(updated))
    {
        message("The path is too long. Shorten its travel times first.");
        return;
    }
    mFrames = std::move(updated);
    mGrid   = grid;
    mRegion = region;
    mDirty  = true;
    refreshFrames(replace ? i : static_cast<S32>(mFrames.size() - 1));
    message(replace ? "Keyframe replaced with your current camera view." : "Keyframe added. Move the camera and add the next one.");
}
void LLFloaterCameraPaths::moveFrame(S32 offset)
{
    const auto i = mList->getFirstSelectedIndex();
    if (mPreview || i < 0 || i + offset < 0 || i + offset >= static_cast<S32>(mFrames.size()))
        return;
    std::swap(mFrames[i], mFrames[i + offset]);
    mDirty = true;
    refreshFrames(i + offset);
}
void LLFloaterCameraPaths::removeFrame()
{
    const auto i = mList->getFirstSelectedIndex();
    if (mPreview || i < 0)
        return;
    mFrames.erase(mFrames.begin() + i);
    mDirty = true;
    refreshFrames(i);
}
LLSD LLFloaterCameraPaths::encodeDraft() const
{
    LLSD data;
    data["grid"]   = mGrid;
    data["region"] = mRegion;
    data["frames"] = LLSD::emptyArray();
    data["motion"] = getChild<LLComboBox>("motion")->getValue();
    data["repeat"] = getChild<LLComboBox>("repeat")->getValue();
    data["delay"]  = mDelay->getValue().asReal();
    for (const auto& f : mFrames)
    {
        LLSD item;
        for (S32 i = 0; i < 3; ++i)
        {
            item["position"][i] = f.position[i];
            item["focus"][i]    = f.focus[i];
        }
        item["roll"]    = f.roll;
        item["fov"]     = f.fov;
        item["seconds"] = f.seconds;
        item["cut"]     = f.cut;
        data["frames"].append(item);
    }
    return data;
}
void LLFloaterCameraPaths::savePath()
{
    if (mPreview || !valid(mFrames))
        return;
    std::string name = mName->getText();
    LLStringUtil::trim(name);
    if (!StellarysShot::validName(name))
    {
        message("Enter a short path name without line breaks.");
        return;
    }
    if (!mSaved.has(name) && mSaved.size() >= MAX_PATHS)
    {
        message("You can save up to 20 paths. Delete an unused one first.");
        return;
    }
    LLSD saved  = mSaved;
    saved[name] = encodeDraft();
    if (write(saved))
    {
        mSelected = name;
        mName->setText(name);
        mDirty = false;
        populate();
        message("Path saved locally. It stays with your settings between updates.");
    }
}
void LLFloaterCameraPaths::deletePath()
{
    if (mPreview || !mSaved.has(mSelected))
        return;
    const auto name   = mSelected;
    auto       handle = getHandle();
    LLSD       args;
    args["NAME"] = name;
    LLNotificationsUtil::add("StellarysDeleteCameraPath", args, LLSD(),
                             [handle, name](const LLSD& n, const LLSD& r)
                             {
                                 auto* self = dynamic_cast<LLFloaterCameraPaths*>(handle.get());
                                 if (self && LLNotificationsUtil::getSelectedOption(n, r) == 0)
                                 {
                                     LLSD saved = self->mSaved;
                                     saved.erase(name);
                                     if (self->write(saved))
                                         self->selectPath("");
                                 }
                                 return false;
                             });
}
bool LLFloaterCameraPaths::allowed(std::string& reason) const
{
    if (LLStartUp::getStartupState() != STATE_STARTED || !gAgent.getRegion() ||
        !StellarysShot::samePlace(mGrid, mRegion.asString(), LLGridManager::getInstance()->getGrid(),
                                  gAgent.getRegion()->getRegionID().asString()))
        reason = "Return to the path's original region and grid to preview it.";
    else if (!gAgentCamera.cameraThirdPerson() || LLViewerJoystick::getInstance()->getOverrideCamera() ||
             gSavedSettings.getBOOL("UseFreezeFrame") || gAgentPilot.isPlaying())
        reason = "Use third-person camera with Flycam, autopilot playback and snapshot Freeze Frame off.";
    else if (!RlvActions::canChangeCameraPreset(LLUUID::null) || !RlvActions::canChangeCameraFOV(LLUUID::null) ||
             RlvActions::isCameraDistanceClamped())
        reason = "An active viewer restriction prevents camera-path playback.";
    else
        return true;
    return false;
}
bool LLFloaterCameraPaths::beginPreview()
{
    std::string reason;
    if (!allowed(reason))
    {
        message(reason);
        return false;
    }
    if (!mPreview)
    {
        if (!capture(mReturnView))
            return false;
        mReturnFocusAvatar = gAgentCamera.getFocusOnAvatar();
        auto object        = gAgentCamera.getFocusObject();
        mReturnFocusObject = object ? object->getID() : LLUUID::null;
        gAgentCamera.getPhotographicZoom(mReturnZoom, mReturnCurrentZoom);
        mPreview = true;
    }
    return true;
}
bool LLFloaterCameraPaths::apply(double time)
{
    Frame f;
    if (mFramePreview >= 0 && mFramePreview < static_cast<S32>(mFrames.size()))
        f = mFrames[mFramePreview];
    else if (mFrames.size() == 1)
        f = mFrames.front();
    else if (!sampleRepeated(mFrames, time, repeat(this), motion(this), f))
        return false;
    if (!valid(f))
        return false;
    auto* camera = LLViewerCamera::getInstance();
    if (f.fov < camera->getMinView() || f.fov > camera->getMaxView())
        return false;
    gAgentCamera.restorePhotographicView(LLVector3d(f.position.data()), LLVector3d(f.focus.data()), static_cast<F32>(f.roll));
    gAgentCamera.setCinematicFOV(static_cast<F32>(f.fov));
    return true;
}
void LLFloaterCameraPaths::play()
{
    using State = Clock::State;
    if (mClock.state == State::Playing || mClock.state == State::Countdown)
    {
        mClock.pause();
        message("Paused. Resume continues the same preview; Stop / return restores your view.");
        refreshControls();
        return;
    }
    if (!beginPreview())
        return;
    mFramePreview = -1;
    if (mStarted && mClock.state == State::Paused)
        mClock.resume();
    else
    {
        // Validate the complete trajectory before taking control, including curves and the loop seam.
        const auto length = total();
        Frame      f;
        auto*      camera = LLViewerCamera::getInstance();
        for (S32 i = 0; i <= 1000; ++i)
            if (!sampleRepeated(mFrames, length * i / 1000., repeat(this), motion(this), f) || f.fov < camera->getMinView() ||
                f.fov > camera->getMaxView())
            {
                stop(true);
                message("This path crosses an invalid camera position. Adjust its keyframes or use Straight motion.");
                return;
            }
        if (!mClock.start(length, mDelay->getValue().asReal(), repeat(this) != Repeat::Once))
        {
            stop(true);
            message("Use a 0-60 second countdown and at least two valid keyframes.");
            return;
        }
        mStarted = true;
    }
    mLastTick = std::chrono::steady_clock::now();
    refreshControls();
}
void LLFloaterCameraPaths::viewFrame()
{
    const S32 i = mList->getFirstSelectedIndex();
    if (i < 0 || !beginPreview())
        return;
    mFramePreview = i;
    mClock.stop();
    mClock.total = total();
    mClock.state = Clock::State::Paused;
    mStarted     = false;
    for (S32 k = 0; k < i; ++k)
        mClock.elapsed += legDuration(mFrames[k]);
    mLastTick = std::chrono::steady_clock::now();
    if (!apply(mClock.elapsed))
    {
        stop(true);
        message("This keyframe cannot be previewed.");
        return;
    }
    message("Viewing the selected keyframe. Play starts the path; Stop / return restores your view.");
    refreshControls();
}
void LLFloaterCameraPaths::seek(double time)
{
    if (!beginPreview())
        return;
    mFramePreview    = -1;
    mClock.total     = total();
    mClock.elapsed   = std::clamp(time, 0., mClock.total);
    mClock.remaining = 0;
    mClock.state     = Clock::State::Paused;
    mStarted         = false;
    mLastTick        = std::chrono::steady_clock::now();
    if (!apply(mClock.elapsed))
    {
        stop(true);
        message("This point cannot be previewed. Adjust the path or motion style.");
        return;
    }
    message("Previewing this point. Play starts from the beginning; Stop / return restores your view.");
    refreshControls();
}
void LLFloaterCameraPaths::stop(bool restore)
{
    if (!mPreview)
    {
        mClock.stop();
        return;
    }
    std::string reason;
    const bool  canRestore = restore && allowed(reason);
    gAgentCamera.setCinematicFOV(-1.f);
    if (canRestore)
    {
        const LLVector3d position(mReturnView.position.data()), focus(mReturnView.focus.data());
        gAgentCamera.restorePhotographicView(position, focus, static_cast<F32>(mReturnView.roll));
        if (mReturnFocusAvatar)
            gAgentCamera.setFocusOnAvatar(true, false, false);
        else if (mReturnFocusObject.notNull())
        {
            gAgentCamera.setCameraPosAndFocusGlobal(position, focus, mReturnFocusObject);
            gAgentCamera.stopCameraAnimation();
        }
        gAgentCamera.restorePhotographicZoom(mReturnZoom, mReturnCurrentZoom);
    }
    mPreview      = false;
    mStarted      = false;
    mFramePreview = -1;
    mClock.stop();
    mUpdating = true;
    mTimeline->setValue(0.f);
    mUpdating = false;
    refreshControls();
}
void LLFloaterCameraPaths::tick()
{
    if (!mPreview)
        return;
    std::string reason;
    if (!allowed(reason))
    {
        stop(false);
        message("Playback stopped: " + reason);
        return;
    }
    if (keysMovingCamera())
    {
        stop(true);
        message("Camera input stopped the preview.");
        return;
    }
    using State      = Clock::State;
    const auto   now = std::chrono::steady_clock::now();
    const double dt  = std::chrono::duration<double>(now - mLastTick).count();
    mLastTick        = now;
    if ((mClock.state == State::Playing || mClock.state == State::Countdown) && dt > 1.)
    {
        mClock.pause();
        message("Paused after a long frame delay. Resume when the viewer is ready.");
        refreshControls();
        return;
    }
    mClock.advance(dt);
    if (mClock.remaining > 0)
    {
        message(llformat(mClock.state == State::Paused ? "Countdown paused: %d seconds left. Resume or Stop / return."
                                                       : "Starting in %d seconds...  Stop or Esc cancels.",
                         static_cast<S32>(std::ceil(mClock.remaining))));
        return;
    }
    if (!apply(mClock.elapsed))
    {
        stop(true);
        message("Preview stopped at an invalid camera point.");
        return;
    }
    mUpdating = true;
    mTimeline->setValue(static_cast<F32>(100 * mClock.elapsed / llmax(.1, mClock.total)));
    mUpdating = false;
    if (mClock.state == State::Playing)
        message(llformat("Playing  %.1f / %.1f seconds  |  Esc stops", mClock.elapsed, mClock.total));
    else if (mClock.state == State::Finished)
    {
        message("Finished. Stop / return restores your previous view; Play runs it again.");
        refreshControls();
    }
}
void LLFloaterCameraPaths::updatePlayback()
{
    if (auto* self = LLFloaterReg::findTypedInstance<LLFloaterCameraPaths>("stellarys_camera_paths"))
        self->tick();
}
bool LLFloaterCameraPaths::stopPlayback(bool restore)
{
    auto* self = LLFloaterReg::findTypedInstance<LLFloaterCameraPaths>("stellarys_camera_paths");
    if (!self || !self->mPreview)
        return false;
    self->stop(restore);
    self->message("Preview cancelled.");
    return true;
}
