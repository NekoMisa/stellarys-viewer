// SPDX-License-Identifier: LGPL-2.1-only
#ifndef LL_FLOATER_CAMERA_PATHS_H
#define LL_FLOATER_CAMERA_PATHS_H
#include "llfloater.h"
#include "stellaryscamerapath.h"
#include <chrono>
class LLComboBox;
class LLLineEditor;
class LLScrollListCtrl;
class LLSpinCtrl;
class LLSliderCtrl;
class LLFloaterCameraPaths : public LLFloater
{
public:
    explicit LLFloaterCameraPaths(const LLSD& key);
    ~LLFloaterCameraPaths() override;
    bool        postBuild() override;
    void        onOpen(const LLSD& key) override;
    void        onClose(bool app_quitting) override;
    static void updatePlayback();
    static bool stopPlayback(bool restore = true);

private:
    using Frame = StellarysCameraPath::Frame;
    void                                  message(const std::string& text);
    void                                  load();
    bool                                  write(const LLSD& paths);
    void                                  selectPath(const std::string& name);
    void                                  requestSelect(const std::string& name, bool reload = false);
    void                                  populate();
    void                                  refreshFrames(S32 selection = -1);
    void                                  refreshControls();
    void                                  frameSelected();
    void                                  captureFrame(bool replace);
    bool                                  capture(Frame& frame);
    void                                  moveFrame(S32 offset);
    void                                  removeFrame();
    void                                  savePath();
    void                                  deletePath();
    void                                  play();
    void                                  viewFrame();
    void                                  seek(double time);
    void                                  tick();
    bool                                  beginPreview();
    bool                                  allowed(std::string& reason) const;
    bool                                  apply(double time);
    void                                  stop(bool restore);
    double                                total() const;
    LLSD                                  encodeDraft() const;
    LLSD                                  mSaved = LLSD::emptyMap();
    std::vector<Frame>                    mFrames;
    std::string                           mGrid, mSelected, mLoadedBytes;
    LLUUID                                mRegion;
    bool                                  mLoaded = false, mWritable = true, mDirty = false, mUpdating = false;
    bool                                  mPreview = false, mStarted = false;
    S32                                   mFramePreview = -1;
    Frame                                 mReturnView;
    LLUUID                                mReturnFocusObject;
    bool                                  mReturnFocusAvatar = false;
    F32                                   mReturnZoom = 0, mReturnCurrentZoom = 0;
    StellarysCameraPath::Clock            mClock;
    std::chrono::steady_clock::time_point mLastTick;
    LLComboBox*                           mPaths    = nullptr;
    LLLineEditor*                         mName     = nullptr;
    LLScrollListCtrl*                     mList     = nullptr;
    LLSpinCtrl*                           mSeconds  = nullptr;
    LLSpinCtrl*                           mDelay    = nullptr;
    LLSliderCtrl*                         mTimeline = nullptr;
};
#endif
