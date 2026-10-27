// SPDX-License-Identifier: LGPL-2.1-only
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
using System.Web.Script.Serialization;

internal static class ProfilePaths
{
    static string ExistingRoot(string variable, Environment.SpecialFolder fallback)
    {
        string value = Environment.GetEnvironmentVariable(variable);
        try
        {
            // Match the native viewer's process-local profile redirection.
            if (!String.IsNullOrWhiteSpace(value) && Path.IsPathRooted(value) && Directory.Exists(value))
                return Path.GetFullPath(value);
        }
        catch (ArgumentException) { }
        catch (NotSupportedException) { }
        return Environment.GetFolderPath(fallback);
    }
    internal static string Roaming { get { return ExistingRoot("APPDATA", Environment.SpecialFolder.ApplicationData); } }
    internal static string Local { get { return ExistingRoot("LOCALAPPDATA", Environment.SpecialFolder.LocalApplicationData); } }
}

internal sealed class UpdatePreferences
{
    readonly string root;
    internal UpdatePreferences(string profileRoot) { root = Path.GetFullPath(profileRoot); }
    internal static UpdatePreferences Default()
    { return new UpdatePreferences(Path.Combine(ProfilePaths.Roaming, "Stellarys_x64")); }
    internal string StartupDisabledPath { get { return Path.Combine(root, "updater-disable-startup"); } }
    internal string ExperimentalPath { get { return Path.Combine(root, "updater-include-experimental"); } }
    internal bool IncludeExperimental
    {
        get
        {
            try
            {
                var file = new FileInfo(ExperimentalPath);
                return file.Exists && file.Length <= 32 && File.ReadAllText(file.FullName).Trim() == "enabled";
            }
            catch (IOException) { return false; }
            catch (UnauthorizedAccessException) { return false; }
        }
    }
    internal void SaveExperimental(bool enabled)
    {
        if (!enabled) { if (File.Exists(ExperimentalPath)) File.Delete(ExperimentalPath); return; }
        Directory.CreateDirectory(root);
        string temporary = ExperimentalPath + "." + Guid.NewGuid().ToString("N") + ".tmp";
        try
        {
            File.WriteAllText(temporary, "enabled\n");
            if (File.Exists(ExperimentalPath)) File.Replace(temporary, ExperimentalPath, null);
            else File.Move(temporary, ExperimentalPath);
        }
        finally { if (File.Exists(temporary)) File.Delete(temporary); }
    }
    internal void SaveStartup(bool enabled)
    {
        Directory.CreateDirectory(root);
        if (enabled) File.Delete(StartupDisabledPath);
        else File.WriteAllText(StartupDisabledPath, "disabled");
    }
}

internal static class ReleaseFeed
{
    internal const string ListApi = "https://api.github.com/repos/NekoMisa/stellarys-viewer/releases";
    const int PerPage = 100;
    const int MaxPages = 10;
    internal static Release SelectPage(string json, bool includeExperimental, Release selected, out int count)
    {
        var entries = new JavaScriptSerializer { MaxJsonLength = 8388608 }.DeserializeObject(json) as object[];
        if (entries == null) throw new InvalidDataException("Invalid release list.");
        count = entries.Length;
        if (count > PerPage) throw new InvalidDataException("Unexpected release page size.");
        foreach (object entry in entries)
        {
            var data = entry as Dictionary<string, object>;
            if (data == null) throw new InvalidDataException("Invalid release entry.");
            object draft;
            if (data.TryGetValue("draft", out draft) && draft is bool && (bool)draft) continue;
            object tagValue;
            Version version; int beta;
            if (!data.TryGetValue("tag_name", out tagValue) ||
                !Release.TryTag(tagValue as string, includeExperimental, out version, out beta)) continue;
            // Old or irrelevant releases cannot trigger a downgrade or prevent a
            // current update because an obsolete asset is no longer available.
            if (Release.Compare(version, beta, Release.ParseVersion(Release.Current), Release.CurrentBeta) < 0) continue;
            Release candidate = Release.ParseData(data, includeExperimental);
            if (selected == null || candidate.CompareTo(selected) > 0) selected = candidate;
        }
        return selected;
    }
    static async Task<string> Read(HttpClient client, string url, int limit, CancellationToken token)
    {
        using (var response = await client.GetAsync(url, HttpCompletionOption.ResponseHeadersRead, token))
        {
            if (response.StatusCode == HttpStatusCode.NotFound) return null;
            response.EnsureSuccessStatusCode();
            using (var stream = await response.Content.ReadAsStreamAsync())
            using (var bytes = new MemoryStream())
            {
                byte[] buffer = new byte[16384]; int n;
                while ((n = await stream.ReadAsync(buffer, 0, buffer.Length, token)) != 0)
                {
                    if (bytes.Length + n > limit) throw new InvalidDataException("Release metadata is too large.");
                    bytes.Write(buffer, 0, n);
                }
                return System.Text.Encoding.UTF8.GetString(bytes.ToArray());
            }
        }
    }
    internal static async Task<Release> Check(HttpClient client, bool includeExperimental, CancellationToken token)
    {
        string stable = await Read(client, Release.Api, 2097152, token);
        Release selected = stable == null ? null : Release.Parse(stable);
        if (!includeExperimental) return selected;
        for (int page = 1; page <= MaxPages; page++)
        {
            string json = await Read(client, ListApi + "?per_page=" + PerPage + "&page=" + page, 8388608, token);
            if (json == null) return selected;
            int count;
            selected = SelectPage(json, true, selected, out count);
            if (count < PerPage) return selected;
        }
        throw new InvalidDataException("There are too many release pages to check safely. Please use the GitHub releases page.");
    }
}
