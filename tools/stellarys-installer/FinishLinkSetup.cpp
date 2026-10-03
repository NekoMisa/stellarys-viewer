// SPDX-License-Identifier: LGPL-2.1-only
// Run the link dialog through the interactive Explorer desktop, not the
// administrator account used for Setup. Uses Microsoft's documented Shell APIs:
// https://learn.microsoft.com/windows/win32/shell/samples-execinexplorer
#include <windows.h>
#include <exdisp.h>
#include <shldisp.h>
#include <shlobj.h>
#include <shlguid.h>
#include <servprov.h>
#include <string>
template<class T> struct ComPtr
{
    T* value = nullptr;
    ~ComPtr() { if (value) value->Release(); }
    T** out() { return &value; }
    T* operator->() { return value; }
};

static HRESULT OpenLinkDialog(const std::wstring& path)
{
    ComPtr<IShellWindows> windows;
    HRESULT hr = CoCreateInstance(CLSID_ShellWindows, nullptr, CLSCTX_LOCAL_SERVER,
                                  IID_PPV_ARGS(windows.out()));
    if (FAILED(hr)) return hr;
    VARIANT empty; VariantInit(&empty);
    long handle = 0;
    ComPtr<IDispatch> desktop;
    hr = windows->FindWindowSW(&empty, &empty, SWC_DESKTOP, &handle,
                               SWFO_NEEDDISPATCH, desktop.out());
    if (FAILED(hr) || !desktop.value) return FAILED(hr) ? hr : E_FAIL;
    ComPtr<IServiceProvider> provider;
    hr = desktop->QueryInterface(IID_PPV_ARGS(provider.out()));
    if (FAILED(hr)) return hr;
    ComPtr<IShellBrowser> browser;
    hr = provider->QueryService(SID_STopLevelBrowser, IID_PPV_ARGS(browser.out()));
    if (FAILED(hr)) return hr;
    ComPtr<IShellView> view;
    hr = browser->QueryActiveShellView(view.out());
    if (FAILED(hr)) return hr;
    ComPtr<IDispatch> background;
    hr = view->GetItemObject(SVGIO_BACKGROUND, IID_PPV_ARGS(background.out()));
    if (FAILED(hr)) return hr;
    ComPtr<IShellFolderViewDual> folder;
    hr = background->QueryInterface(IID_PPV_ARGS(folder.out()));
    if (FAILED(hr)) return hr;
    ComPtr<IDispatch> app;
    hr = folder->get_Application(app.out());
    if (FAILED(hr)) return hr;
    ComPtr<IShellDispatch2> shell;
    hr = app->QueryInterface(IID_PPV_ARGS(shell.out()));
    if (FAILED(hr)) return hr;
    BSTR file = SysAllocString(path.c_str());
    VARIANT args; VariantInit(&args); args.vt = VT_BSTR;
    args.bstrVal = SysAllocString(L"--link-settings");
    VARIANT verb; VariantInit(&verb); verb.vt = VT_BSTR;
    verb.bstrVal = SysAllocString(L"open");
    VARIANT show; VariantInit(&show); show.vt = VT_I4; show.lVal = SW_SHOWNORMAL;
    if (!file || !args.bstrVal || !verb.bstrVal) hr = E_OUTOFMEMORY;
    else hr = shell->ShellExecute(file, args, empty, verb, show);
    SysFreeString(file); VariantClear(&args); VariantClear(&verb);
    return hr;
}

int WINAPI wWinMain(HINSTANCE, HINSTANCE, PWSTR, int)
{
    wchar_t module[32768];
    DWORD length = GetModuleFileNameW(nullptr, module, 32768);
    if (!length || length == 32768) return 3;
    std::wstring path(module, length);
    size_t slash = path.find_last_of(L"\\/");
    if (slash == std::wstring::npos) return 3;
    path.resize(slash + 1); path += L"StellarysUpdater.exe";
    DWORD attributes = GetFileAttributesW(path.c_str());
    if (attributes == INVALID_FILE_ATTRIBUTES || (attributes & FILE_ATTRIBUTE_DIRECTORY)) return 3;
    HRESULT hr = CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
    if (FAILED(hr)) return 3;
    hr = OpenLinkDialog(path);
    CoUninitialize();
    // No administrator fallback: Preferences remains available if Explorer fails.
    return SUCCEEDED(hr) ? 0 : 3;
}
