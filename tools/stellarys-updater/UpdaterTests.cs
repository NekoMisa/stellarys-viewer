// SPDX-License-Identifier: LGPL-2.1-only
using System;
using System.IO;
using System.Web.Script.Serialization;
class UpdaterTests
{
    static int checks;
    static void Check(bool value) { checks++; if (!value) throw new Exception("Check " + checks + " failed"); }
    static void Reject(Action action) { try { action(); } catch { checks++; return; } throw new Exception("Expected rejection"); }
    static string Metadata(string tag, string digest, string url, bool draft, bool prerelease)
    {
        return new JavaScriptSerializer().Serialize(new { tag_name=tag, draft=draft, prerelease=prerelease, body="notes", assets=new [] {new { name="Stellarys-Viewer-0.2.0-Windows-x64-Setup.exe", state="uploaded", size=3, digest=digest, browser_download_url=url }} });
    }
    static int Main()
    {
        string url=Release.Repository+"/releases/download/v0.2.0/Stellarys-Viewer-0.2.0-Windows-x64-Setup.exe";
        string digest="sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
        Check(Release.Parse(Metadata("v0.2.0",digest,url,false,false)).Version > Release.ParseVersion(Release.Current));
        Check(Release.ParseVersion("0.10.0") > Release.ParseVersion("0.9.0"));
        Check(!(Release.ParseVersion("0.1.0") > Release.ParseVersion(Release.Current)));
        Reject(()=>Release.ParseVersion("0.2.0-beta"));
        Reject(()=>Release.Parse(Metadata("v0.2.0",digest,url,true,false)));
        Reject(()=>Release.Parse(Metadata("v0.2.0",digest,url,false,true)));
        Reject(()=>Release.Parse(Metadata("v0.2.0",null,url,false,false)));
        Reject(()=>Release.Parse(Metadata("v0.2.0",digest,"https://example.com/installer.exe",false,false)));
        Reject(()=>Release.Parse(Metadata("v0.3.0",digest,url,false,false)));
        Check(Release.DownloadHost(new Uri(url)));
        Check(Release.DownloadHost(new Uri("https://release-assets.githubusercontent.com/x")));
        Check(!Release.DownloadHost(new Uri("http://github.com/x")));
        Check(!Release.DownloadHost(new Uri("https://github.com.evil.example/x")));
        Check(!Release.DownloadHost(new Uri("https://github.com:444/x")));
        string file=Path.GetTempFileName();
        try { File.WriteAllText(file,"abc"); Release.Verify(file,digest,3); checks++;
            Reject(()=>Release.Verify(file,digest,4)); File.WriteAllText(file,"abd"); Reject(()=>Release.Verify(file,digest,3)); }
        finally { File.Delete(file); }
        Console.WriteLine(checks+" updater validation checks passed."); return 0;
    }
}
