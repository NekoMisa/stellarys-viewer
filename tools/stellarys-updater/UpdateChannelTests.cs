// SPDX-License-Identifier: LGPL-2.1-only
using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
using System.Web.Script.Serialization;

internal static class UpdateChannelTests
{
    static int checks;
    static readonly JavaScriptSerializer Json = new JavaScriptSerializer();
    const string Digest = "sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
    static void Check(bool value) { checks++; if (!value) throw new Exception("Channel check " + checks + " failed"); }
    static void Reject(Action action) { try { action(); } catch { checks++; return; } throw new Exception("Expected rejection"); }
    static Dictionary<string,object> Data(string tag, bool beta, bool draft = false)
    {
        string name = "Stellarys-Viewer-" + tag.Substring(1) + "-Windows-x64-Setup.exe";
        return new Dictionary<string,object> {
            {"tag_name",tag}, {"draft",draft}, {"prerelease",beta}, {"body","## Changes\n- Fixture only."},
            {"assets",new object[] {new Dictionary<string,object> {
                {"name",name},{"state","uploaded"},{"size",3},{"digest",Digest},
                {"browser_download_url",Release.Repository+"/releases/download/"+tag+"/"+name}
            }}}
        };
    }
    static Release Parse(Dictionary<string,object> data, bool include) { return Release.Parse(Json.Serialize(data),include); }
    sealed class Transport : HttpMessageHandler
    {
        internal readonly List<string> Requests = new List<string>();
        internal readonly Dictionary<string,string> Responses = new Dictionary<string,string>();
        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request,CancellationToken token)
        {
            string url=request.RequestUri.AbsoluteUri; Requests.Add(url);
            string body;
            return Task.FromResult(Responses.TryGetValue(url,out body)
                ? new HttpResponseMessage(HttpStatusCode.OK) {Content=new StringContent(body)}
                : new HttpResponseMessage(HttpStatusCode.NotFound));
        }
    }
    static int Main()
    {
        Version baseVersion=new Version(1,0,0);
        Check(Release.Compare(baseVersion,1,baseVersion,2)<0);
        Check(Release.Compare(baseVersion,99,baseVersion,0)<0);
        Check(Release.Compare(baseVersion,0,baseVersion,1)>0);
        Check(Release.Compare(baseVersion,0,baseVersion,0)==0);
        Check(Release.Compare(new Version(2,0,0),1,baseVersion,0)>0);
        Check(Release.Compare(new Version(0,9,0),0,baseVersion,1)<0);
        var stable=Parse(Data("v1.0.0",false),false);
        var beta1=Parse(Data("v1.0.0-beta.1",true),true);
        var beta2=Parse(Data("v1.0.0-beta.2",true),true);
        var future=Parse(Data("v2.0.0-beta.1",true),true);
        Check(beta1.Beta==1 && beta1.DisplayVersion=="1.0.0 Beta 1");
        Check(beta1.Name=="Stellarys-Viewer-1.0.0-beta.1-Windows-x64-Setup.exe");
        Check(beta2.CompareTo(beta1)>0 && stable.CompareTo(beta2)>0);
        Reject(()=>Parse(Data("v1.0.0-beta.1",true),false));
        Reject(()=>Parse(Data("v1.0.0-beta.1",false),true));
        Reject(()=>Parse(Data("v1.0.0",true),true));
        Reject(()=>Parse(Data("v1.0.0-beta.1",true,true),true));
        Reject(()=>Parse(Data("v1.0.0-beta.0",true),true));
        Reject(()=>Parse(Data("v1.0.0-beta.01",true),true));
        Reject(()=>Parse(Data("v1.0.0-rc.1",true),true));
        Reject(()=>Parse(Data("v1.0.0-beta.2147483648",true),true));
        Reject(()=>Parse(Data("v2147483648.0.0-beta.1",true),true));
        var bad=Data("v1.0.0-beta.1",true);
        ((Dictionary<string,object>)((object[])bad["assets"])[0])["digest"]=null;
        Reject(()=>Parse(bad,true));
        bad=Data("v1.0.0-beta.1",true);
        ((Dictionary<string,object>)((object[])bad["assets"])[0])["browser_download_url"]="https://example.com/update.exe";
        Reject(()=>Parse(bad,true));
        bad=Data("v1.0.0-beta.1",true);
        bad["assets"]=new object[] { ((object[])bad["assets"])[0], ((object[])bad["assets"])[0] };
        Reject(()=>Parse(bad,true));
        int count;
        var linux=new Dictionary<string,object>{{"tag_name","linux-v99.0.0-portable-preview1"},{"draft",false}};
        string page=Json.Serialize(new object[] {Data("v1.0.0-beta.2",true),linux,Data("v1.0.0",false),Data("v1.0.0-beta.1",true)});
        Check(ReleaseFeed.SelectPage(page,false,null,out count).Tag=="v1.0.0" && count==4);
        Check(ReleaseFeed.SelectPage(page,true,null,out count).Tag=="v1.0.0");
        page=Json.Serialize(new object[] {Data("v2.0.0-beta.1",true),linux,Data("v1.0.0",false)});
        Check(ReleaseFeed.SelectPage(page,true,null,out count).Tag=="v2.0.0-beta.1");
        Check(ReleaseFeed.SelectPage(page,false,null,out count).Tag=="v1.0.0");
        Check(ReleaseFeed.SelectPage(Json.Serialize(new object[]{Data("v2.0.0-beta.1",true,true)}),true,stable,out count)==stable);
        Check(ReleaseFeed.SelectPage(Json.Serialize(new object[]{Data("v0.0.1",false)}),true,stable,out count)==stable);
        Reject(()=>ReleaseFeed.SelectPage("{}",true,null,out count));
        var excessive=new object[101]; for(int n=0;n<excessive.Length;n++)excessive[n]=linux;
        Reject(()=>ReleaseFeed.SelectPage(Json.Serialize(excessive),true,null,out count));
        var invalidCandidate=Data("v2.0.0-beta.3",true);
        ((Dictionary<string,object>)((object[])invalidCandidate["assets"])[0])["digest"]=null;
        Reject(()=>ReleaseFeed.SelectPage(Json.Serialize(new object[]{invalidCandidate}),true,stable,out count));
        var installed=new Release {Version=Release.ParseVersion(Release.Current),Beta=Release.CurrentBeta};
        Check(!InstallChoice.Allowed(installed,false) && InstallChoice.Allowed(installed,true));
        Check(InstallChoice.Allowed(new Release {Version=installed.Version,Beta=0},false)==(Release.CurrentBeta>0));
        Check(!InstallChoice.Allowed(new Release {Version=new Version(0,0,1)},true));
        using(var transport=new Transport()) using(var client=new HttpClient(transport))
        {
            transport.Responses[Release.Api]=Json.Serialize(Data("v1.0.0",false));
            transport.Responses[ReleaseFeed.ListApi+"?per_page=100&page=1"]=page;
            Check(ReleaseFeed.Check(client,false,CancellationToken.None).GetAwaiter().GetResult().Tag=="v1.0.0");
            Check(transport.Requests.Count==1 && transport.Requests[0]==Release.Api);
            transport.Requests.Clear();
            Check(ReleaseFeed.Check(client,true,CancellationToken.None).GetAwaiter().GetResult().Tag==future.Tag);
            Check(transport.Requests.Count==2);
            var full=new object[100]; for(int n=0;n<full.Length;n++)full[n]=linux;
            transport.Responses[ReleaseFeed.ListApi+"?per_page=100&page=1"]=Json.Serialize(full);
            transport.Responses[ReleaseFeed.ListApi+"?per_page=100&page=2"]=Json.Serialize(new object[]{Data("v2.0.0-beta.1",true)});
            transport.Requests.Clear();
            Check(ReleaseFeed.Check(client,true,CancellationToken.None).GetAwaiter().GetResult().Tag==future.Tag);
            Check(transport.Requests.Count==3 && transport.Requests[2].EndsWith("page=2"));
            for(int n=1;n<=10;n++)transport.Responses[ReleaseFeed.ListApi+"?per_page=100&page="+n]=Json.Serialize(full);
            transport.Requests.Clear();
            Reject(()=>ReleaseFeed.Check(client,true,CancellationToken.None).GetAwaiter().GetResult());
            Check(transport.Requests.Count==11);
            transport.Responses[Release.Api]=new string('x',2097153);
            Reject(()=>ReleaseFeed.Check(client,false,CancellationToken.None).GetAwaiter().GetResult());
        }
        string root=Path.Combine(Path.GetTempPath(),"Stellarys-channel-tests-"+Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        string roaming=Environment.GetEnvironmentVariable("APPDATA"),local=Environment.GetEnvironmentVariable("LOCALAPPDATA");
        try
        {
            var prefs=new UpdatePreferences(Path.Combine(root,"profile"));
            Check(!prefs.IncludeExperimental); prefs.SaveExperimental(false);
            prefs.SaveExperimental(true); Check(new UpdatePreferences(Path.Combine(root,"profile")).IncludeExperimental);
            prefs.SaveStartup(false); prefs.SaveExperimental(false);
            Check(!prefs.IncludeExperimental && File.Exists(prefs.StartupDisabledPath));
            prefs.SaveExperimental(true); prefs.SaveStartup(true);
            Check(prefs.IncludeExperimental && !File.Exists(prefs.StartupDisabledPath));
            File.WriteAllText(prefs.ExperimentalPath,"not enabled"); Check(!prefs.IncludeExperimental);
            File.WriteAllText(prefs.ExperimentalPath,new string('x',100)); Check(!prefs.IncludeExperimental);
            Directory.CreateDirectory(Path.Combine(root,"roaming"));Directory.CreateDirectory(Path.Combine(root,"local"));
            Environment.SetEnvironmentVariable("APPDATA",Path.Combine(root,"roaming"));
            Environment.SetEnvironmentVariable("LOCALAPPDATA",Path.Combine(root,"local"));
            Check(ProfilePaths.Roaming==Path.Combine(root,"roaming") && ProfilePaths.Local==Path.Combine(root,"local"));
            var isolated=UpdatePreferences.Default(); isolated.SaveExperimental(true);
            Check(isolated.ExperimentalPath.StartsWith(Path.Combine(root,"roaming"),StringComparison.OrdinalIgnoreCase));
            Check(File.Exists(Path.Combine(root,"roaming","Stellarys_x64","updater-include-experimental")));
            string download=Path.Combine(root,"fixture.exe");File.WriteAllText(download,"abc");
            Release.Verify(download,beta1.Digest,beta1.Size);checks++;
        }
        finally
        {
            Environment.SetEnvironmentVariable("APPDATA",roaming);Environment.SetEnvironmentVariable("LOCALAPPDATA",local);
            if(!Path.GetFullPath(root).StartsWith(Path.GetFullPath(Path.GetTempPath()),StringComparison.OrdinalIgnoreCase)) throw new Exception("Unsafe fixture cleanup");
            Directory.Delete(root,true);
        }
        Console.WriteLine(checks+" experimental-channel/version/feed/profile checks passed; real profiles and associations untouched.");
        return 0;
    }
}
