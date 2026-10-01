// Stellarys complete local shot presets. SPDX-License-Identifier: LGPL-2.1-only
#ifndef LL_FLOATER_SHOT_PRESETS_H
#define LL_FLOATER_SHOT_PRESETS_H
#include "llfloater.h"
class LLComboBox;
class LLLineEditor;
class LLSpinCtrl;
class LLFloaterShotPresets : public LLFloater
{
public:
    explicit LLFloaterShotPresets(const LLSD& key);
    bool postBuild() override;
    void onOpen(const LLSD& key) override;
private:
    void load();
    bool write(const LLSD& presets);
    void populate(const std::string& selected = "");
    void selectionChanged();
    void save();
    void restore();
    void remove();
    void message(const std::string& text);
    LLSD capture();
    bool apply(const LLSD& shot);
    LLSD mPresets = LLSD::emptyMap();
    bool mWritable = true;
    LLComboBox* mList = nullptr;
    LLLineEditor* mName = nullptr;
    LLSpinCtrl* mWidth = nullptr;
    LLSpinCtrl* mHeight = nullptr;
};
#endif
