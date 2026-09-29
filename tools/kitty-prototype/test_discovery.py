"""Compile the actual viewer discovery function against controlled avatar fixtures."""
from pathlib import Path
import importlib.util, subprocess, sys
here = Path(__file__).resolve().parent
src = Path(r'C:\FK-Poser-Test\source\indra\newview\fsfloaterposer.cpp')
text = src.read_text(encoding='utf-8')
start = text.index('uuid_vec_t FSFloaterPoser::getNearbyAvatarsAndAnimeshes() const')
end = text.index('bool FSFloaterPoser::avatarIsNearbyMe(', start)
function = text[start:end]
prefix = r'''
#include <vector>
#include <iostream>
using uuid_vec_t = std::vector<int>;
struct LLCharacter {
    int id;
    explicit LLCharacter(int i): id(i) {}
    virtual ~LLCharacter() = default;
    int getID() const { return id; }
    static std::vector<LLCharacter*> sInstances;
};
std::vector<LLCharacter*> LLCharacter::sInstances;
struct LLVOAvatar : LLCharacter {
    bool self=false, control=false, nearby=true, alive=true, sameRegion=true;
    explicit LLVOAvatar(int i): LLCharacter(i) {}
    bool isSelf() const { return self; }
    bool isControlAvatar() const { return control; }
};
struct LLMuteList {
    static LLMuteList* getInstance() { static LLMuteList list; return &list; }
    bool isMuted(int id) const { return id == 4; }
};
struct FSFloaterPoser {
    uuid_vec_t getNearbyAvatarsAndAnimeshes() const;
    bool avatarIsNearbyMe(LLVOAvatar* av) const { return av && av->nearby; }
    bool couldAnimateAvatar(LLVOAvatar* av) const { return av && av->alive && av->sameRegion; }
};
'''
suffix = r'''
int main() {
    LLVOAvatar self(1), other(2), animesh(3), muted(4), distant(5), dead(6), region(7);
    LLCharacter nonAvatar(8);
    self.self=true; animesh.control=true; distant.nearby=false;
    dead.alive=false; region.sameRegion=false;
    LLCharacter::sInstances={&self,&other,&animesh,&muted,&distant,&dead,&region,&nonAvatar};
    auto result=FSFloaterPoser{}.getNearbyAvatarsAndAnimeshes();
    if (result != uuid_vec_t{1,2,3}) {
        std::cerr << "FAIL: expected self, other avatar, animesh; got";
        for(int id:result) std::cerr << " " << id;
        std::cerr << "\n"; return 1;
    }
    LLCharacter::sInstances.clear();
    if (!FSFloaterPoser{}.getNearbyAvatarsAndAnimeshes().empty()) return 2;
    std::cout << "PASS: actual discovery function includes nearby other avatar and self/animesh; excludes muted, distant, dead, other-region and non-avatar; empty list handled.\n";
}
'''
testdir = here / 'tests'
testdir.mkdir(exist_ok=True)
testsrc = testdir / 'discovery-tests.cpp'
testsrc.write_text(prefix + function + suffix, encoding='utf-8')
helper = here.parents[1] / 'work/package/Black-Dragon-AMD-Port/build_windows.py'
spec = importlib.util.spec_from_file_location('helper', helper)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
_, install, version, _, env = mod.visual_studio_environment()
compiler = install / 'VC/Tools/MSVC' / version / 'bin/Hostx64/x64/cl.exe'
exe = testdir / 'discovery-tests.exe'
subprocess.run([str(compiler), '/nologo', '/std:c++17', '/EHsc', str(testsrc),
                '/Fe:' + str(exe), '/Fo:' + str(testdir / 'discovery-tests.obj')],
               cwd=testdir, env=env, check=True)
sys.exit(subprocess.run([str(exe)], cwd=testdir).returncode)
