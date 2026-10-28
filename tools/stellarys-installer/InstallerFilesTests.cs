// SPDX-License-Identifier: LGPL-2.1-only
using System;
using System.IO;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text;
using System.Web.Script.Serialization;
using System.Runtime.InteropServices;
class InstallerFilesTests
{
    [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)]
    static extern bool CreateHardLink(string link,string existing,IntPtr reserved);
    static int checks;
    static void Check(bool ok){checks++;if(!ok)throw new Exception("File planning check "+checks+" failed.");}
    static void Reject(Action a){try{a();}catch{checks++;return;}throw new Exception("Expected refusal.");}
    static string Hash(string text){using(var s=SHA256.Create())return BitConverter.ToString(s.ComputeHash(Encoding.UTF8.GetBytes(text))).Replace("-","").ToLowerInvariant();}
    static Dictionary<string,object> Entry(string path,string contents)
    {return new Dictionary<string,object>{{"path",path},{"bytes",Encoding.UTF8.GetByteCount(contents)},{"sha256",Hash(contents)}};}
    static int Main(string[] args)
    {
        if(args.Length!=1||Directory.Exists(args[0]))throw new Exception("Supply a new disposable fixture directory.");
        string root=Path.GetFullPath(args[0]);Directory.CreateDirectory(root);
        string app=Path.Combine(root,"app"),manifest=Path.Combine(root,"files.json");Directory.CreateDirectory(app);
        string addon=Path.Combine(app,"opengl32.dll");
        File.WriteAllText(addon,"Third-party wrapper fixture");
        var files=new[]{Entry("same.txt","same"),Entry("changed.txt","new!"),Entry("missing.txt","add")};
        File.WriteAllText(manifest,new JavaScriptSerializer().Serialize(files));
        var entries=InstallerFiles.Load(manifest);
        File.WriteAllText(Path.Combine(app,"same.txt"),"same",new UTF8Encoding(false));
        File.WriteAllText(Path.Combine(app,"changed.txt"),"old!",new UTF8Encoding(false));
        DateTime old=new DateTime(2001,2,3,4,5,6,DateTimeKind.Utc);File.SetLastWriteTimeUtc(Path.Combine(app,"same.txt"),old);
        byte[] plan=InstallerFiles.Plan(app,entries,false);
        Check(Encoding.ASCII.GetString(plan)=="100");
        Check(File.GetLastWriteTimeUtc(Path.Combine(app,"same.txt"))==old);
        Check(File.ReadAllText(Path.Combine(app,"changed.txt"))=="old!"&&!File.Exists(Path.Combine(app,"missing.txt")));
        Check(Encoding.ASCII.GetString(InstallerFiles.Plan(app,entries,true))=="000");
        Check(Encoding.ASCII.GetString(InstallerFiles.Plan(Path.Combine(root,"new"),entries,false))=="000");
        Reject(()=>InstallerFiles.Verify(app,entries));
        foreach(var f in files)File.WriteAllText(Path.Combine(app,(string)f["path"]),f["path"].Equals("same.txt")?"same":f["path"].Equals("changed.txt")?"new!":"add",new UTF8Encoding(false));
        InstallerFiles.Verify(app,entries);Check(true);
        Check(Encoding.ASCII.GetString(InstallerFiles.Plan(app,entries,false))=="111");
        Check(File.ReadAllText(addon)=="Third-party wrapper fixture");
        Check(Encoding.ASCII.GetString(InstallerFiles.Plan(app,entries,true))=="000");
        Check(File.ReadAllText(addon)=="Third-party wrapper fixture");
        using(var locked=new FileStream(Path.Combine(app,"same.txt"),FileMode.Open,FileAccess.ReadWrite,FileShare.None))
        {Reject(()=>InstallerFiles.Plan(app,entries,false));Reject(()=>InstallerFiles.Plan(app,entries,true));}
        foreach(string path in new[]{"../escape","C:\\outside","\\\\server\\share","file:stream","a\\..\\b","a\\.\\b","a\\\\b","a ","a.","NUL.txt","COM1","user_settings\\settings.xml","cache\\x","logs\\x","browser_profile\\x"})
        {
            File.WriteAllText(manifest,new JavaScriptSerializer().Serialize(new[]{Entry(path,"x")}));
            Reject(()=>InstallerFiles.Load(manifest));
        }
        File.WriteAllText(manifest,new JavaScriptSerializer().Serialize(new[]{Entry("same.txt","same"),Entry("SAME.TXT","same")}));Reject(()=>InstallerFiles.Load(manifest));
        var bad=Entry("x","x");bad["bytes"]=-1;File.WriteAllText(manifest,new JavaScriptSerializer().Serialize(new[]{bad}));Reject(()=>InstallerFiles.Load(manifest));
        bad=Entry("x","x");bad["sha256"]="invalid";File.WriteAllText(manifest,new JavaScriptSerializer().Serialize(new[]{bad}));Reject(()=>InstallerFiles.Load(manifest));
        bad=Entry("x","x");bad["bytes"]=1.5;File.WriteAllText(manifest,new JavaScriptSerializer().Serialize(new[]{bad}));Reject(()=>InstallerFiles.Load(manifest));
        Reject(()=>InstallerFiles.Root("C:\\"));Reject(()=>InstallerFiles.Root("relative"));Reject(()=>InstallerFiles.Root("\\\\server\\share"));
        Check(CreateHardLink(Path.Combine(root,"hard-linked-copy"),Path.Combine(app,"same.txt"),IntPtr.Zero));
        Reject(()=>InstallerFiles.Plan(app,entries,false));Reject(()=>InstallerFiles.Plan(app,entries,true));Reject(()=>InstallerFiles.Verify(app,entries));
        Console.WriteLine(checks+" installer file planning/security checks passed.");return 0;
    }
}
