// Stellarys complete local shot presets. SPDX-License-Identifier: LGPL-2.1-only
#include "llviewerprecompiledheaders.h"
#include "llfloatershotpresets.h"
#include "stellarysshotvalidation.h"
#include "llagent.h"
#include "llagentcamera.h"
#include "llbutton.h"
#include "llcombobox.h"
#include "lldir.h"
#include "llenvironment.h"
#include "llfile.h"
#include "llfloaterreg.h"
#include "llfloatersnapshot.h"
#include "lllineeditor.h"
#include "llnotificationsutil.h"
#include "llsdserialize.h"
#include "llsdutil_math.h"
#include "llsettingsvo.h"
#include "llsidetraypanelcontainer.h"
#include "llspinctrl.h"
#include "lltextbox.h"
#include "llviewercamera.h"
#include "llviewercontrol.h"
#include "llviewerjoystick.h"
#include "llviewernetwork.h"
#include "llviewerregion.h"
#include "llviewerwindow.h"
#include "pipeline.h"
#include "rlvactions.h"
#include <fstream>

namespace
{
constexpr S32 MAX_FILE_BYTES = 1024 * 1024;
constexpr S32 MAX_PRESETS = 50;
std::string path()
{ return gDirUtilp->getExpandedFilename(LL_PATH_USER_SETTINGS, "stellarys_shot_presets.xml"); }
bool vector(const LLSD& value, std::array<double,3>& result)
{
    if (!value.isArray() || value.size()!=3) return false;
    for (S32 i=0;i<3;++i)
    {
        if (!value[i].isReal() && !value[i].isInteger()) return false;
        result[i]=value[i].asReal();
    }
    return true;
}
bool valid(const LLSD& shot)
{
    std::array<double,3> position, focus, depth_focus;
    if (!shot.isMap() || !shot["schema"].isInteger() || shot["schema"].asInteger()!=1 ||
        !shot["region"].isUUID() || shot["region"].asUUID().isNull() ||
        !shot["grid"].isString() || shot["grid"].asString().empty() || shot["grid"].asString().size()>256 ||
        !vector(shot["position"],position) || !vector(shot["focus"],focus) ||
        !shot["roll"].isReal() || !StellarysShot::validCamera(position,focus,shot["roll"].asReal()) ||
        !vector(shot["depth_focus"],depth_focus) || !StellarysShot::validPosition(depth_focus) ||
        !shot["width"].isInteger() || !shot["height"].isInteger() ||
        !StellarysShot::validDimensions(shot["width"].asInteger(),shot["height"].asInteger()) ||
        !shot["sky"].isMap() || !shot["water"].isMap() || !shot["sky_advanced"].isBoolean()) return false;
    const LLSD& lens=shot["lens"];
    if (!lens.isMap() || lens.size()!=StellarysShot::lensRanges.size()+StellarysShot::flags.size()+1) return false;
    for (const auto& rule : StellarysShot::lensRanges)
        if (!lens[rule.name].isReal() || !StellarysShot::inRange(lens[rule.name].asReal(),rule.minimum,rule.maximum)) return false;
    for (const auto* flag : StellarysShot::flags) if (!lens[flag].isBoolean()) return false;
    if (!lens["RenderTonemapType"].isInteger() || !StellarysShot::inRange(lens["RenderTonemapType"].asInteger(),0,10)) return false;
    return true;
}
}

LLFloaterShotPresets::LLFloaterShotPresets(const LLSD& key) : LLFloater(key) {}
bool LLFloaterShotPresets::postBuild()
{
    mList=getChild<LLComboBox>("shots");
    mName=getChild<LLLineEditor>("shot_name");
    mWidth=getChild<LLSpinCtrl>("shot_width");
    mHeight=getChild<LLSpinCtrl>("shot_height");
    mList->setCommitCallback([this](LLUICtrl*,const LLSD&) { selectionChanged(); });
    mName->setKeystrokeCallback([](LLLineEditor*,void* data) {
        auto* self=static_cast<LLFloaterShotPresets*>(data);
        self->getChild<LLButton>("save")->setLabel(self->mPresets.has(self->mName->getText()) ? "Replace shot" : "Save shot");
    },this);
    getChild<LLButton>("save")->setCommitCallback([this](LLUICtrl*,const LLSD&) { save(); });
    getChild<LLButton>("restore")->setCommitCallback([this](LLUICtrl*,const LLSD&) { restore(); });
    getChild<LLButton>("delete")->setCommitCallback([this](LLUICtrl*,const LLSD&) { remove(); });
    getChild<LLButton>("snapshot")->setCommitCallback([](LLUICtrl*,const LLSD&) { LLFloaterReg::showInstance("snapshot"); });
    return true;
}
void LLFloaterShotPresets::onOpen(const LLSD&)
{
    load(); populate();
    S32 width=gSavedSettings.getS32("LastSnapshotToDiskWidth");
    S32 height=gSavedSettings.getS32("LastSnapshotToDiskHeight");
    if (auto* snapshot=LLFloaterSnapshot::findInstance())
    {
        if (auto* panel=snapshot->findChild<LLPanelSnapshot>("panel_snapshot_local"))
        { width=panel->getTypedPreviewWidth(); height=panel->getTypedPreviewHeight(); }
    }
    if (!StellarysShot::validDimensions(width,height))
    { width=llclamp(gViewerWindow->getWindowWidthRaw(),32,6016); height=llclamp(gViewerWindow->getWindowHeightRaw(),32,6016); }
    mWidth->setValue(width); mHeight->setValue(height);
}
void LLFloaterShotPresets::message(const std::string& text)
{ getChild<LLTextBox>("status")->setText(text); }
void LLFloaterShotPresets::load()
{
    mWritable=true; mPresets=LLSD::emptyMap();
    if (!LLFile::isfile(path())) return;
    llifstream input(path(),std::ios::binary);
    input.seekg(0,std::ios::end); auto size=input.tellg(); input.seekg(0);
    LLSD data;
    bool ok=size>0 && size<=MAX_FILE_BYTES && LLSDSerialize::fromXML(data,input)>0 &&
        data["schema"].isInteger() && data["schema"].asInteger()==1 && data["presets"].isMap() && data["presets"].size()<=MAX_PRESETS;
    if (ok) for (auto it=data["presets"].beginMap();it!=data["presets"].endMap();++it)
        if (!StellarysShot::validName(it->first) || !valid(it->second)) { ok=false; break; }
    if (!ok) { mWritable=false; message("The saved shot file could not be read. It has been left unchanged."); return; }
    mPresets=data["presets"];
    message("Choose a saved shot, or name your current setup and save it.");
}
bool LLFloaterShotPresets::write(const LLSD& presets)
{
    if (!mWritable) return false;
    LLSD data; data["schema"]=1; data["presets"]=presets;
    std::ostringstream buffer; LLSDSerialize::toPrettyXML(data,buffer);
    const std::string bytes=buffer.str();
    if (bytes.size()>MAX_FILE_BYTES) { message("The shot collection is full. Delete an unused shot first."); return false; }
    const std::string temporary=path()+".tmp";
    llofstream output(temporary,std::ios::binary|std::ios::trunc);
    output.write(bytes.data(),bytes.size()); output.flush(); bool ok=output.good(); output.close();
    if (!ok || LLFile::rename(temporary,path())!=0)
    { LLFile::remove(temporary); message("Could not save the shot file. Your previous shots are unchanged."); return false; }
    mPresets=presets; return true;
}
void LLFloaterShotPresets::populate(const std::string& selected)
{
    mList->removeall();
    for (auto it=mPresets.beginMap();it!=mPresets.endMap();++it) mList->add(it->first,LLSD(it->first));
    mList->setValue(selected);
    const bool have=mPresets.has(selected);
    getChildView("restore")->setEnabled(have); getChildView("delete")->setEnabled(have);
    getChildView("save")->setEnabled(mWritable);
    getChild<LLButton>("save")->setLabel(mPresets.has(mName->getText()) ? "Replace shot" : "Save shot");
}
void LLFloaterShotPresets::selectionChanged()
{
    const std::string name=mList->getValue().asString();
    mName->setText(name); populate(name);
}
LLSD LLFloaterShotPresets::capture()
{
    if (!gAgent.getRegion() || !gAgentCamera.cameraThirdPerson() || LLViewerJoystick::getInstance()->getOverrideCamera())
    { message("Use the normal third-person camera and turn off Flycam before saving a shot."); return LLSD(); }
    auto& environment=LLEnvironment::instance();
    auto sky=environment.getCurrentSky(); auto water=environment.getCurrentWater();
    if (!sky || !water) { message("Lighting is not ready yet. Try again in a moment."); return LLSD(); }
    LLSD shot; shot["schema"]=1;
    shot["grid"]=LLGridManager::getInstance()->getGrid(); shot["region"]=gAgent.getRegion()->getRegionID();
    shot["position"]=ll_sd_from_vector3d(gAgentCamera.getCameraPositionGlobal());
    shot["focus"]=ll_sd_from_vector3d(gAgentCamera.getFocusGlobal());
    shot["roll"]=std::remainder(static_cast<double>(gAgentCamera.getCameraRoll()),6.283185307179586);
    shot["depth_focus"]=ll_sd_from_vector3d(gAgent.getPosGlobalFromAgent(LLPipeline::sLastFocusPoint));
    shot["width"]=mWidth->getValue().asInteger(); shot["height"]=mHeight->getValue().asInteger();
    for (const auto& rule:StellarysShot::lensRanges) shot["lens"][rule.name]=static_cast<F64>(gSavedSettings.getF32(rule.name));
    // Object-focus zoom can narrow the rendered FOV without changing CameraAngle.
    shot["lens"]["CameraAngle"]=static_cast<F64>(LLViewerCamera::getInstance()->getView());
    for (const auto* flag:StellarysShot::flags) shot["lens"][flag]=gSavedSettings.getBOOL(flag);
    shot["lens"]["RenderTonemapType"]=gSavedSettings.getS32("RenderTonemapType");
    shot["sky"]=sky->getSettings(); shot["water"]=water->getSettings();
    auto* viewer_sky=dynamic_cast<LLSettingsVOSky*>(sky.get());
    shot["sky_advanced"]=viewer_sky && viewer_sky->isAdvanced();
    if (!valid(shot)) { message("This setup contains an unsupported lens value or image size. Nothing was saved."); return LLSD(); }
    return shot;
}
void LLFloaterShotPresets::save()
{
    std::string name=mName->getText(); LLStringUtil::trim(name);
    if (!StellarysShot::validName(name)) { message("Enter a short name without line breaks."); return; }
    if (!mPresets.has(name) && mPresets.size()>=MAX_PRESETS) { message("You can save up to 50 shots. Delete an unused shot first."); return; }
    LLSD shot=capture(); if (shot.isUndefined()) return;
    LLSD updated=mPresets; updated[name]=shot;
    if (write(updated)) { mName->setText(name); populate(name); message("Shot saved locally. Camera position restores in its original region only."); }
}
bool LLFloaterShotPresets::apply(const LLSD& shot)
{
    if (!valid(shot)) { message("This shot could not be restored. Your current setup is unchanged."); return false; }
    if (!gAgent.getRegion() || !StellarysShot::samePlace(shot["grid"].asString(),shot["region"].asUUID().asString(),
        LLGridManager::getInstance()->getGrid(),gAgent.getRegion()->getRegionID().asString()))
    { message("Return to the original region and grid before restoring this shot."); return false; }
    if (LLViewerJoystick::getInstance()->getOverrideCamera() || !gAgentCamera.cameraThirdPerson() || gSavedSettings.getBOOL("UseFreezeFrame"))
    { message("Turn off Flycam or snapshot Freeze Frame and use third-person view before restoring."); return false; }
    if (!RlvActions::canChangeCameraPreset(LLUUID::null) || !RlvActions::canChangeCameraFOV(LLUUID::null) ||
        RlvActions::isCameraDistanceClamped() || !RlvActions::canChangeEnvironment())
    { message("An active viewer restriction prevents restoring this shot."); return false; }
    // Validate both environments before changing any camera, lighting or settings.
    auto sky=std::make_shared<LLSettingsVOSky>(shot["sky"],shot["sky_advanced"].asBoolean());
    auto water=std::make_shared<LLSettingsVOWater>(shot["water"]);
    if (!sky->validate() || !water->validate()) { message("This shot contains invalid lighting. Your setup is unchanged."); return false; }
    auto* snapshot=LLFloaterSnapshot::getInstance();
    if (!snapshot || snapshot->isWaitingState()) { message("Wait for the current snapshot to finish, then try again."); return false; }
    auto* panel=snapshot->findChild<LLPanelSnapshot>("panel_snapshot_local");
    auto* container=snapshot->findChild<LLSideTrayPanelContainer>("panel_container");
    if (!panel || !container) { message("Open the snapshot window once, then try again."); return false; }
    for (const auto& rule:StellarysShot::lensRanges) gSavedSettings.setF32(rule.name,static_cast<F32>(shot["lens"][rule.name].asReal()));
    for (const auto* flag:StellarysShot::flags) gSavedSettings.setBOOL(flag,shot["lens"][flag].asBoolean());
    gSavedSettings.setS32("RenderTonemapType",shot["lens"]["RenderTonemapType"].asInteger());
    gAgentCamera.restorePhotographicView(ll_vector3d_from_sd(shot["position"]),ll_vector3d_from_sd(shot["focus"]),static_cast<F32>(shot["roll"].asReal()));
    LLPipeline::sLastFocusPoint=gAgent.getPosAgentFromGlobal(ll_vector3d_from_sd(shot["depth_focus"]));
    auto& environment=LLEnvironment::instance();
    environment.setEnvironment(LLEnvironment::ENV_LOCAL,sky,water);
    environment.setSelectedEnvironment(LLEnvironment::ENV_LOCAL,LLEnvironment::TRANSITION_INSTANT);
    environment.updateEnvironment(LLEnvironment::TRANSITION_INSTANT,true);
    S32 width=shot["width"].asInteger(),height=shot["height"].asInteger();
    gSavedSettings.setS32("LastSnapshotToDiskWidth",width); gSavedSettings.setS32("LastSnapshotToDiskHeight",height);
    gSavedSettings.setS32("LastSnapshotToDiskResolution",7);
    gSavedSettings.setString("FSLastSnapshotPanel","panel_snapshot_local");
    container->openPanel("panel_snapshot_local");
    panel->getChild<LLUICtrl>("local_keep_aspect_check")->setValue(false);
    snapshot->notify(LLSD().with("keep-aspect-change",false));
    panel->getImageSizeComboBox()->setValue("[i-1,i-1]");
    panel->getWidthSpinner()->setValue(width); panel->getHeightSpinner()->setValue(height);
    LLSD size; size["w"]=width; size["h"]=height;
    snapshot->notify(LLSD().with("custom-res-change",size));
    mWidth->setValue(width); mHeight->setValue(height);
    message("Shot restored. Lighting is local; Snapshot is set to save to disk.");
    return true;
}
void LLFloaterShotPresets::restore()
{ const auto name=mList->getValue().asString(); if (mPresets.has(name)) apply(mPresets[name]); }
void LLFloaterShotPresets::remove()
{
    const auto name=mList->getValue().asString(); if (!mPresets.has(name)) return;
    LLSD args; args["NAME"]=name;
    auto handle=getHandle();
    LLNotificationsUtil::add("StellarysDeleteShotPreset",args,LLSD(),[handle,name](const LLSD& notification,const LLSD& response) {
        auto* self=dynamic_cast<LLFloaterShotPresets*>(handle.get());
        if (self && LLNotificationsUtil::getSelectedOption(notification,response)==0)
        { LLSD updated=self->mPresets; updated.erase(name); if (self->write(updated)) { self->populate(); self->message("Shot deleted. Your current camera and lighting are unchanged."); } }
        return false;
    });
}
