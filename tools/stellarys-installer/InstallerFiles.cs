// SPDX-License-Identifier: LGPL-2.1-only
// Embedded setup helper: compares application files, never reads viewer profiles.
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;
using System.Threading.Tasks;
using Microsoft.Win32.SafeHandles;

internal static class InstallerFiles
{
    internal sealed class Entry { internal string Path, Hash; internal long Size; }
    [StructLayout(LayoutKind.Sequential)]
    struct FileInformation
    {
        internal uint Attributes;
        internal System.Runtime.InteropServices.ComTypes.FILETIME Creation, Access, Write;
        internal uint Volume, SizeHigh, SizeLow, Links, IndexHigh, IndexLow;
    }
    [DllImport("kernel32.dll", SetLastError=true)]
    static extern bool GetFileInformationByHandle(SafeFileHandle handle, out FileInformation information);

    internal static List<Entry> Load(string manifest)
    {
        if (new FileInfo(manifest).Length > 32 * 1024 * 1024) throw new InvalidDataException("Application manifest is too large.");
        var data = new JavaScriptSerializer { MaxJsonLength=32*1024*1024 }.Deserialize<List<Dictionary<string,object>>>(File.ReadAllText(manifest));
        if (data == null || data.Count < 1 || data.Count > 100000) throw new InvalidDataException("Invalid application manifest.");
        var names = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        var result = new List<Entry>();
        foreach (var item in data)
        {
            object path, size, hash;
            if (item == null || !item.TryGetValue("path",out path) || !(path is string) ||
                !item.TryGetValue("bytes",out size) || !(size is int || size is long) ||
                !item.TryGetValue("sha256",out hash) || !(hash is string)) throw new InvalidDataException("Invalid application manifest entry.");
            string relative = ((string)path).Replace('/', '\\');
            if (relative.Length == 0 || relative.Length > 240 || Path.IsPathRooted(relative)) throw new InvalidDataException("Invalid application path.");
            foreach (string part in relative.Split('\\'))
            {
                if (part.Length == 0 || part=="." || part==".." || part.EndsWith(" ") || part.EndsWith(".") ||
                    part.IndexOfAny(Path.GetInvalidFileNameChars()) >= 0 ||
                    Regex.IsMatch(part,@"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)",RegexOptions.IgnoreCase) ||
                    Regex.IsMatch(part,@"^(user_settings|logs|cache|browser_profile|\.git)$",RegexOptions.IgnoreCase))
                    throw new InvalidDataException("Application path is not permitted.");
            }
            long length=Convert.ToInt64(size);
            if (length < 0 || length > 2147483648L || !Regex.IsMatch((string)hash,@"\A[a-fA-F0-9]{64}\z") || !names.Add(relative))
                throw new InvalidDataException("Invalid or duplicate application manifest entry.");
            result.Add(new Entry { Path=relative, Size=length, Hash=(string)hash });
        }
        return result;
    }
    internal static string Root(string path)
    {
        if (!Regex.IsMatch(path??"",@"\A[A-Za-z]:[\\/]")) throw new InvalidDataException("Choose a local absolute application folder.");
        string root=Path.GetFullPath(path).TrimEnd('\\');
        if(root.Length<=3)throw new InvalidDataException("A drive root is not an application folder.");
        CheckParents(root,new HashSet<string>(StringComparer.OrdinalIgnoreCase));
        return root;
    }
    static void CheckParents(string path,HashSet<string> checkedDirectories)
    {
        for(string p=path;!String.IsNullOrEmpty(p)&&checkedDirectories.Add(p);p=Path.GetDirectoryName(p))
        {
            if(File.Exists(p))throw new IOException("An application directory is a file.");
            if(Directory.Exists(p) && (File.GetAttributes(p)&FileAttributes.ReparsePoint)!=0)
                throw new IOException("Application directories must not contain links or junctions.");
        }
    }
    static bool Matches(string root,Entry entry,HashSet<string> checkedDirectories,bool compare)
    {
        string path=Path.GetFullPath(Path.Combine(root,entry.Path));
        if(!path.StartsWith(root+"\\",StringComparison.OrdinalIgnoreCase))throw new InvalidDataException("Application path escaped its folder.");
        CheckParents(Path.GetDirectoryName(path),checkedDirectories);
        if(Directory.Exists(path))throw new IOException("An application file is a directory.");
        // GetAttributes also catches a dangling reparse point; File.Exists would hide it.
        try { if((File.GetAttributes(path)&FileAttributes.ReparsePoint)!=0)throw new IOException("Application files must not be links."); }
        catch(FileNotFoundException){return false;} catch(DirectoryNotFoundException){return false;}
        using(var file=new FileStream(path,FileMode.Open,FileAccess.Read,FileShare.Read,65536,FileOptions.SequentialScan))
        {
            FileInformation info;
            if(!GetFileInformationByHandle(file.SafeFileHandle,out info))throw new IOException("Application file identity could not be checked.");
            if(info.Links!=1)throw new IOException("Application files must not have additional hard links.");
            if(!compare || file.Length!=entry.Size)return false;
            using(var sha=SHA256.Create())
                return String.Equals(BitConverter.ToString(sha.ComputeHash(file)).Replace("-",""),entry.Hash,StringComparison.OrdinalIgnoreCase);
        }
    }
    internal static byte[] Plan(string destination,List<Entry> entries,bool repair)
    {
        string root=Root(destination);
        var plan=new byte[entries.Count];
        int workers=Math.Min(4,entries.Count);
        Parallel.For(0,workers,worker=>{
            var dirs=new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            for(int i=worker;i<entries.Count;i+=workers)plan[i]=(byte)(Matches(root,entries[i],dirs,!repair)?'1':'0');
        });
        return plan;
    }
    internal static void Verify(string destination,List<Entry> entries)
    {
        string root=Root(destination);
        int workers=Math.Min(4,entries.Count);
        Parallel.For(0,workers,worker=>{
            var dirs=new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            for(int i=worker;i<entries.Count;i+=workers)
                if(!Matches(root,entries[i],dirs,true))throw new InvalidDataException("Application verification failed. Run Setup again with Full reinstall / repair.");
        });
    }
    static int Main(string[] args)
    {
        try
        {
            if(args.Length<3)throw new ArgumentException("Invalid installer helper arguments.");
            var entries=Load(args[2]);
            if(args[0]=="plan" && args.Length==5 && (args[4]=="0"||args[4]=="1"))
            {
                byte[] plan=Plan(args[1],entries,args[4]=="1");
                File.WriteAllBytes(args[3],plan);
                int unchanged=0;foreach(byte b in plan)if(b=='1')unchanged++;
                Console.WriteLine("Application files: "+unchanged+" unchanged, "+(plan.Length-unchanged)+" to install.");
            }
            else if(args[0]=="verify" && args.Length==3)
            {Verify(args[1],entries);Console.WriteLine("All "+entries.Count+" packaged application files verified.");}
            else throw new ArgumentException("Invalid installer helper arguments.");
            return 0;
        }
        catch(Exception ex){var aggregate=ex as AggregateException;Console.WriteLine(aggregate==null?ex.Message:aggregate.Flatten().InnerExceptions[0].Message);return 3;}
    }
}
