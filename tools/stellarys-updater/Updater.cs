// Stellarys Viewer updater. SPDX-License-Identifier: LGPL-2.1-only
// Windows .NET Framework 4.8; no credentials or elevated download process.
using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using System.Web.Script.Serialization;
using System.Windows.Forms;

[assembly: System.Reflection.AssemblyTitle("Stellarys Viewer Updater")]
[assembly: System.Reflection.AssemblyVersion("0.2.0.0")]

internal sealed class Release
{
    internal const string Repository = "https://github.com/NekoMisa/stellarys-viewer";
    internal const string Api = "https://api.github.com/repos/NekoMisa/stellarys-viewer/releases/latest";
    internal const string Current = "0.2.0";
    internal const int CurrentBeta = 0; // 0 for a stable build; positive for Windows beta revisions.
    internal Version Version;
    internal int Beta;
    internal string Tag, Notes, Url, Digest, Name;
    internal long Size;
    internal string PageUrl { get { return Repository + "/releases/tag/" + Tag; } }
    internal string DisplayVersion { get { return Version + (Beta == 0 ? "" : " Beta " + Beta); } }
    internal static string CurrentDisplay { get { return Current + (CurrentBeta == 0 ? "" : " Beta " + CurrentBeta); } }
    internal int CompareTo(Release other) { return Compare(Version, Beta, other.Version, other.Beta); }
    internal int CompareInstalled { get { return Compare(Version, Beta, ParseVersion(Current), CurrentBeta); } }
    internal static int Compare(Version left, int leftBeta, Version right, int rightBeta)
    {
        int result = left.CompareTo(right);
        if (result != 0 || leftBeta == rightBeta) return result;
        if (leftBeta == 0) return 1;
        if (rightBeta == 0) return -1;
        return leftBeta.CompareTo(rightBeta);
    }
    internal static bool TryTag(string tag, bool allowExperimental, out Version version, out int beta)
    {
        version = null; beta = 0;
        var match = Regex.Match(tag ?? "", @"^v((?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*))(?:-beta\.([1-9]\d*))?$");
        if (!match.Success || !System.Version.TryParse(match.Groups[1].Value, out version)) return false;
        if (match.Groups[2].Success && (!allowExperimental || !Int32.TryParse(match.Groups[2].Value, out beta))) return false;
        return true;
    }
    internal static Version ParseVersion(string value)
    {
        if (!Regex.IsMatch(value ?? "", @"^\d+\.\d+\.\d+$")) throw new InvalidDataException("Invalid stable version.");
        return new Version(value);
    }
    internal static Release Parse(string json)
    { return Parse(json, false); }
    internal static Release Parse(string json, bool allowExperimental)
    {
        var data = new JavaScriptSerializer { MaxJsonLength = 2097152 }.Deserialize<Dictionary<string, object>>(json);
        return ParseData(data, allowExperimental);
    }
    internal static Release ParseData(Dictionary<string, object> data, bool allowExperimental)
    {
        if ((bool)data["draft"]) throw new InvalidDataException("Draft releases cannot be installed.");
        string tag = (string)data["tag_name"];
        Version version; int beta;
        if (!TryTag(tag, allowExperimental, out version, out beta) || (bool)data["prerelease"] != (beta > 0))
            throw new InvalidDataException("The Windows release tag or update channel is invalid.");
        var r = new Release { Tag = tag, Version = version, Beta = beta, Notes = data.ContainsKey("body") ? data["body"] as string ?? "" : "" };
        r.Name = "Stellarys-Viewer-" + tag.Substring(1) + "-Windows-x64-Setup.exe";
        int matches = 0;
        foreach (Dictionary<string, object> a in (IEnumerable)data["assets"])
        {
            if ((string)a["name"] != r.Name) continue;
            matches++;
            r.Url = (string)a["browser_download_url"];
            r.Digest = a.ContainsKey("digest") ? a["digest"] as string : null;
            r.Size = Convert.ToInt64(a["size"]);
            if ((string)a["state"] != "uploaded" || r.Size < 1 || r.Size > 2147483648L ||
                !Regex.IsMatch(r.Digest ?? "", "^sha256:[a-fA-F0-9]{64}$") ||
                r.Url != Repository + "/releases/download/" + tag + "/" + r.Name)
                throw new InvalidDataException("The release installer has invalid download or SHA-256 metadata.");
        }
        if (matches != 1) throw new InvalidDataException("This release does not have exactly one verified Windows installer.");
        return r;
    }
    internal static bool DownloadHost(Uri uri)
    {
        return uri.Scheme == "https" && uri.IsDefaultPort && uri.UserInfo == "" &&
            (uri.Host == "github.com" || uri.Host == "release-assets.githubusercontent.com" || uri.Host == "objects.githubusercontent.com");
    }
    internal static void Verify(string path, string digest, long size)
    {
        using (var f = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read))
        using (var hash = SHA256.Create())
        {
            if (f.Length != size) throw new InvalidDataException("Installer size does not match the release.");
            string actual = "sha256:" + BitConverter.ToString(hash.ComputeHash(f)).Replace("-", "").ToLowerInvariant();
            if (!String.Equals(actual, digest, StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Installer SHA-256 verification failed. Nothing will be installed.");
        }
    }
}

internal static class ReleaseNotes
{
    // The dialog shows a bounded summary; the trusted release page contains details.
    internal static string[] Summary(string markdown)
    {
        string[] lines = (markdown ?? "").Replace("\r", "").Split('\n');
        var selected = new List<string>();
        bool preferred = false, inCode = false;
        foreach (string line in lines)
        {
            var heading = Regex.Match(line.Trim(), @"^#{1,6}\s+(.+?)\s*#*$");
            if (heading.Success && Regex.IsMatch(Plain(heading.Groups[1].Value),
                @"^(what['’]?s new|changes|changed|highlights|improvements)$", RegexOptions.IgnoreCase))
            { preferred = true; break; }
        }
        bool active = !preferred;
        foreach (string line in lines)
        {
            string text = line.Trim();
            if (text.StartsWith("```", StringComparison.Ordinal)) { inCode = !inCode; continue; }
            if (inCode) continue;
            var heading = Regex.Match(text, @"^#{1,6}\s+(.+?)\s*#*$");
            if (heading.Success)
            {
                if (preferred)
                {
                    bool wanted = Regex.IsMatch(Plain(heading.Groups[1].Value),
                        @"^(what['’]?s new|changes|changed|highlights|improvements)$", RegexOptions.IgnoreCase);
                    if (active && !wanted) break;
                    active = wanted;
                }
                continue;
            }
            if (!active || text.Length == 0 || text.StartsWith("|", StringComparison.Ordinal)) continue;
            var bullet = Regex.Match(text, @"^(?:[-*+]\s+|\d+[.)]\s+|•\s*)(.+)$");
            if (bullet.Success)
            {
                string item = Plain(bullet.Groups[1].Value);
                if (item.Length > 0) selected.Add(item);
            }
            else if (selected.Count > 0 && line.Length > 0 && Char.IsWhiteSpace(line[0]))
                selected[selected.Count - 1] += " " + Plain(text);
            if (selected.Count == 5) break;
        }
        if (selected.Count == 0)
        {
            inCode = false;
            foreach (string line in lines)
            {
                string text = line.Trim();
                if (text.StartsWith("```", StringComparison.Ordinal)) { inCode = !inCode; continue; }
                if (inCode || text.Length == 0 || text.StartsWith("#") || text.StartsWith("|")) continue;
                text = Plain(text);
                if (Regex.IsMatch(text, @"^(Stellarys.*\d+\.\d+\.\d+|Based on |SHA-?256|Source commit)", RegexOptions.IgnoreCase)) continue;
                if (text.Length > 0) selected.Add(text);
                if (selected.Count == 3) break;
            }
        }
        if (selected.Count == 0) selected.Add("See the full release notes for details about this update.");
        for (int i = 0; i < selected.Count; i++) selected[i] = Shorten(selected[i]);
        return selected.ToArray();
    }
    static string Plain(string text)
    {
        text = Regex.Replace(text, @"!?\[([^\]]+)\]\([^)]*\)", "$1");
        text = Regex.Replace(text, @"<[^>]*>", "");
        text = Regex.Replace(text, @"[*_`]+", "");
        text = WebUtility.HtmlDecode(text);
        return Regex.Replace(text, @"[\s\x00-\x1f\x7f]+", " ").Trim();
    }
    static string Shorten(string text)
    {
        if (text.Length <= 180) return text;
        int length = 177;
        int space = text.LastIndexOf(' ', length);
        if (space >= 120) length = space;
        if (Char.IsHighSurrogate(text[length - 1])) length--;
        return text.Substring(0, length).TrimEnd() + "…";
    }
}

internal static class InstallChoice
{
    internal static bool Allowed(Release release, bool repair)
    { return release != null && (release.CompareInstalled > 0 || (repair && release.CompareInstalled == 0)); }
    internal static string Arguments(string home, bool repair)
    { return (repair ? "/REPAIR " : "") + "/D=" + home; } // NSIS requires /D to be last.
}

internal sealed class Updater : Form
{
    readonly Label heading = new Label { Dock = DockStyle.Top, Height = 40, Text = "Stellarys Viewer" };
    readonly Label versions = new Label { Dock = DockStyle.Top, Height = 28 };
    readonly Label status = new Label { Dock = DockStyle.Top, Height = 55 };
    readonly RichTextBox notes = new RichTextBox { ReadOnly = true, DetectUrls = false, BorderStyle = BorderStyle.None,
        BackColor = Color.White, ScrollBars = RichTextBoxScrollBars.Vertical, Dock = DockStyle.Fill };
    readonly LinkLabel fullNotes = new LinkLabel { Text = "Read full release notes on GitHub", Dock = DockStyle.Bottom, Height = 30, Enabled = false };
    readonly Button action = new Button { Text = "Checking…", Enabled = false, Width = 160, Height = 30 };
    readonly CheckBox startup = new CheckBox { Text = "Check for updates when Stellarys starts", AutoSize = true };
    readonly CheckBox experimental = new CheckBox {
        Text = "Include experimental updates (beta)", AutoSize = true, Checked = false, Enabled = false };
    readonly CheckBox installAutomatically = new CheckBox {
        Text = "Install when the download finishes (closes Stellarys)", AutoSize = true, Checked = false, Enabled = false };
    readonly CheckBox repair = new CheckBox {
        Text = "Full reinstall / repair (keeps settings and cache)", AutoSize = true, Checked = false, Enabled = false };
    readonly CancellationTokenSource cancel = new CancellationTokenSource();
    readonly string home = AppDomain.CurrentDomain.BaseDirectory.TrimEnd(Path.DirectorySeparatorChar);
    readonly UpdatePreferences preferences = UpdatePreferences.Default();
    readonly bool quiet;
    Release release;
    string downloaded;
    bool verified;
    bool busy;
    bool checking, restoringPreference;
    internal Updater(bool automatic, Release preview = null)
    {
        quiet = automatic;
        Text = "Stellarys Viewer — Updates"; Size = new Size(740, 600); MinimumSize = new Size(620, 510);
        Font = new Font("Segoe UI", 10); AutoScaleMode = AutoScaleMode.Dpi;
        BackColor = Color.White;
        heading.Font = new Font("Segoe UI", 19, FontStyle.Bold);
        versions.ForeColor = Color.DimGray;
        versions.Text = "Installed: Stellarys " + Release.CurrentDisplay;
        Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath);
        StartPosition = FormStartPosition.CenterScreen;
        var footer = new Panel { Dock = DockStyle.Bottom, Height = 178, Padding = new Padding(18, 8, 18, 12) };
        var buttons = new FlowLayoutPanel { Dock = DockStyle.Top, Height = 37, FlowDirection = FlowDirection.RightToLeft, WrapContents = false };
        var close = new Button { Text = "Close", Width = 90, Height = 30 };
        close.Click += (s,e) => Close();
        startup.Checked = !File.Exists(preferences.StartupDisabledPath);
        startup.CheckedChanged += (s,e) => {
            try { preferences.SaveStartup(startup.Checked); }
            catch (Exception ex) { MessageBox.Show(this, "Could not save update preference: " + ex.Message); }
        };
        experimental.Checked = preferences.IncludeExperimental;
        experimental.CheckedChanged += async (s,e) => {
            if (restoringPreference || busy || checking || downloaded != null) return;
            try { preferences.SaveExperimental(experimental.Checked); }
            catch {
                restoringPreference = true;
                experimental.Checked = !experimental.Checked;
                restoringPreference = false;
                status.Text = "Could not save the experimental update preference. The change was not applied.";
                return;
            }
            await Check();
        };
        buttons.Controls.Add(close); buttons.Controls.Add(action);
        startup.Dock = DockStyle.Bottom;
        installAutomatically.Dock = DockStyle.Bottom;
        repair.Dock = DockStyle.Bottom;
        experimental.Dock = DockStyle.Bottom;
        repair.CheckedChanged += (s,e) => UpdateAction();
        footer.Controls.Add(buttons); footer.Controls.Add(installAutomatically); footer.Controls.Add(repair); footer.Controls.Add(experimental); footer.Controls.Add(startup);
        var installTip = new ToolTip();
        installTip.SetToolTip(installAutomatically, "Save your work before downloading. A verified download requests normal viewer shutdown, then opens Setup. Cancelling shutdown or administrator approval postpones installation.");
        installTip.SetToolTip(repair, "Normal updates keep identical application files. Repair replaces every packaged file and can reinstall the current release. Both download the complete installer and preserve your profile.");
        installTip.SetToolTip(experimental, "Receive Windows beta releases as well as stable updates. Beta builds may have bugs. Turning this off waits for a suitable stable release; it does not downgrade your installed viewer. Choose before downloading.");
        var header = new Panel { Dock = DockStyle.Top, Height = 148, Padding = new Padding(20, 16, 20, 0) };
        header.Controls.Add(status); header.Controls.Add(versions); header.Controls.Add(heading);
        var content = new Panel { Dock = DockStyle.Fill, Padding = new Padding(22, 8, 22, 8) };
        var changesTitle = new Label { Dock = DockStyle.Top, Height = 32, Text = "Release highlights", Font = new Font("Segoe UI", 12, FontStyle.Bold) };
        content.Controls.Add(notes); content.Controls.Add(changesTitle); content.Controls.Add(fullNotes);
        Controls.Add(content); Controls.Add(header); Controls.Add(footer);
        fullNotes.LinkClicked += (s,e) => {
            if (release == null) return;
            try { Process.Start(new ProcessStartInfo(release.PageUrl) { UseShellExecute = true }); }
            catch { MessageBox.Show(this, "Could not open GitHub. You can find the release notes at " + release.PageUrl); }
        };
        action.Click += async (s,e) => { if (release == null) await Check(); else await DownloadAndInstall(); };
        FormClosing += (s,e) => cancel.Cancel();
        Shown += async (s,e) => {
            if (preview != null) {
                release = preview; ShowRelease(); startup.Enabled = false; experimental.Enabled = false;
                status.Text = "Release notes preview. Download and installation are disabled.";
                action.Text = "Download update"; action.Enabled = false;
                return;
            }
            if (quiet) Hide(); await Check();
        };
        if (quiet) { Opacity = 0; ShowInTaskbar = false; }
    }
    void ShowRelease()
    {
        heading.Text = "Stellarys Viewer " + release.DisplayVersion;
        versions.Text = "Installed: " + Release.CurrentDisplay + "    •    Release: " + release.DisplayVersion;
        notes.Clear();
        foreach (string item in ReleaseNotes.Summary(release.Notes))
        {
            notes.SelectionStart = notes.TextLength;
            notes.SelectionIndent = 18; notes.SelectionHangingIndent = 4;
            notes.SelectionBullet = true;
            notes.AppendText(item + "\n");
            notes.SelectionBullet = false; notes.SelectionIndent = 0; notes.SelectionHangingIndent = 0;
            notes.AppendText("\n");
        }
        notes.SelectionStart = 0; notes.SelectionLength = 0;
        notes.ScrollToCaret();
        fullNotes.Enabled = true;
    }
    void Reveal() { Opacity = 1; ShowInTaskbar = true; Show(); Activate(); }
    void UpdateAction()
    {
        if(IsDisposed || busy || checking || release==null)return;
        bool allowed=InstallChoice.Allowed(release,repair.Checked);
        repair.Enabled=release.CompareInstalled>=0;
        action.Enabled=allowed;
        action.Text=downloaded==null?(repair.Checked?"Download repair":"Download update"):(repair.Checked?"Install repair":"Install update");
        installAutomatically.Enabled=downloaded==null&&allowed;
    }
    static HttpClient Client()
    {
        var c = new HttpClient(new HttpClientHandler { AllowAutoRedirect = false });
        c.Timeout = TimeSpan.FromMinutes(15);
        c.DefaultRequestHeaders.UserAgent.ParseAdd("Stellarys-Viewer/" + Release.Current);
        return c;
    }
    async Task Check()
    {
        if (busy || checking || downloaded != null) return;
        if (quiet && File.Exists(preferences.StartupDisabledPath)) { Close(); return; }
        checking = true;
        experimental.Enabled = false; action.Enabled = false; repair.Enabled = false; installAutomatically.Enabled = false;
        release = null; fullNotes.Enabled = false; notes.Clear();
        heading.Text = "Stellarys Viewer " + Release.CurrentDisplay;
        versions.Text = "Installed: " + Release.CurrentDisplay;
        status.Text = experimental.Checked ? "Checking stable and experimental Windows releases…" : "Checking stable Windows releases…";
        try
        {
            using (var c = Client())
            using (var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancel.Token))
            {
                timeout.CancelAfter(TimeSpan.FromSeconds(45));
                release = await ReleaseFeed.Check(c, experimental.Checked, timeout.Token);
            }
            if (IsDisposed || cancel.IsCancellationRequested) return;
            if (release == null) { Finish("No published Windows releases are available for this update channel."); return; }
            if (release.CompareInstalled < 0) {
                release = null;
                Finish("No newer " + (experimental.Checked ? "Windows" : "stable") + " release is available. This build stays installed; automatic downgrades are disabled.");
                return;
            }
            ShowRelease();
            if (release.CompareInstalled == 0) {
                Finish("Stellarys " + Release.CurrentDisplay + " is up to date. Select Full reinstall / repair to repair application files.");
                UpdateAction();return;
            }
            Reveal();
            status.Text = release.Beta > 0 ? "An experimental update is ready. Beta builds may have bugs. Review the highlights before downloading." : "A stable update is ready. Review the highlights below, then choose Download update.";
            UpdateAction();
        }
        catch (OperationCanceledException) { if (!IsDisposed) Finish("Update check cancelled or timed out."); }
        catch (Exception ex) { if (!IsDisposed) Finish("Could not check for updates. " + ex.Message); }
        finally {
            checking = false;
            if (!IsDisposed) { experimental.Enabled = !busy && downloaded == null; UpdateAction(); }
        }
    }
    void Finish(string message) { if (quiet) Close(); else { status.Text = message; action.Text = "Check again"; action.Enabled = true; } }
    async Task DownloadAndInstall()
    {
        if (busy || checking || release == null || !InstallChoice.Allowed(release,repair.Checked)) return;
        // Consent is specific to this Download click; retries with an existing
        // download still use the normal Install confirmation.
        bool installAfterDownload = downloaded == null && installAutomatically.Checked;
        bool fullRepair=repair.Checked;
        busy = true; action.Enabled = false; installAutomatically.Enabled = false;repair.Enabled=false;experimental.Enabled=false;
        try
        {
            if (downloaded == null)
            {
                string dir = Path.Combine(ProfilePaths.Local, "Stellarys_x64", "updates", Guid.NewGuid().ToString("N"));
                Directory.CreateDirectory(dir);
                downloaded = Path.Combine(dir, release.Name);
                using (var c = Client())
                {
                    Uri url = new Uri(release.Url);
                    for (int redirects = 0; ; redirects++)
                    {
                        if (redirects > 5 || !Release.DownloadHost(url)) throw new InvalidDataException("Untrusted download redirect.");
                        using (var response = await c.GetAsync(url, HttpCompletionOption.ResponseHeadersRead, cancel.Token))
                        {
                            if ((int)response.StatusCode >= 300 && (int)response.StatusCode <= 399)
                            { if (response.Headers.Location == null) throw new InvalidDataException("Missing redirect."); url = new Uri(url, response.Headers.Location); continue; }
                            response.EnsureSuccessStatusCode();
                            using (var input = await response.Content.ReadAsStreamAsync())
                            using (var output = new FileStream(downloaded, FileMode.CreateNew, FileAccess.Write, FileShare.None, 65536, true))
                            using (var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancel.Token))
                            {
                                byte[] buffer = new byte[65536]; int n; long total = 0;
                                for (;;) {
                                    timeout.CancelAfter(TimeSpan.FromSeconds(60));
                                    n = await input.ReadAsync(buffer, 0, buffer.Length, timeout.Token);
                                    if (n == 0) break;
                                    total += n;
                                    if (total > release.Size) throw new InvalidDataException("Download exceeds the release size.");
                                    await output.WriteAsync(buffer, 0, n, timeout.Token);
                                    status.Text = "Downloading update: " + (total * 100 / release.Size) + "%";
                                }
                            }
                            break;
                        }
                    }
                }
            }
            status.Text = "Verifying installer…";
            await Task.Run(() => Release.Verify(downloaded, release.Digest, release.Size));
            verified = true;
            if (cancel.IsCancellationRequested) return;
            if (!File.Exists(Path.Combine(home, "stellarys-install.txt")) || File.ReadAllLines(Path.Combine(home, "stellarys-install.txt"))[0] != "StellarysViewer")
                throw new InvalidDataException("Automatic installation requires a marked Stellarys installation. Use the downloaded installer manually for a portable build.");
            if (!installAfterDownload && MessageBox.Show(this, "The download is verified. Install now?\n\n"+(fullRepair?"Full reinstall / repair replaces every packaged application file. Settings and cache are preserved.\n\n":"Normal updates replace changed or missing application files and keep identical files.\n\n")+"Stellarys will close normally without another quit confirmation. Save your work first. Unsaved-edit prompts may still need attention. Setup will then request administrator permission. Cancel leaves the viewer running.", "Ready to update", MessageBoxButtons.OKCancel) != DialogResult.OK)
            { status.Text = "Update postponed. Your viewer has not been closed."; return; }
            var viewers = Process.GetProcessesByName("StellarysViewer");
            try
            {
                foreach (var process in viewers)
                {
                    if (process.HasExited) continue;
                    if (process.SessionId != Process.GetCurrentProcess().SessionId ||
                        !String.Equals(Path.GetDirectoryName(process.MainModule.FileName), home, StringComparison.OrdinalIgnoreCase))
                        throw new InvalidOperationException("Another Stellarys installation or Windows session is running. Close it yourself before updating this installation.");
                }
                foreach (var process in viewers)
                    if (!process.HasExited) ViewerShutdown.Request(process.MainWindowHandle);
                status.Text = "Waiting for Stellarys to close. Saving and logging out…";
                DateTime deadline = DateTime.UtcNow.AddSeconds(90);
                foreach (var process in viewers)
                    while (!process.HasExited)
                    {
                        if (DateTime.UtcNow > deadline) throw new InvalidOperationException("Stellarys is still running; installation was postponed. Close it normally, then retry.");
                        await Task.Delay(250, cancel.Token);
                    }
            }
            finally { foreach (var process in viewers) process.Dispose(); }
            // Hold a read-only sharing lock through installer startup; no writable or
            // delete sharing is allowed after the final verification.
            using (var hold = new FileStream(downloaded, FileMode.Open, FileAccess.Read, FileShare.Read))
            {
                Release.Verify(downloaded, release.Digest, release.Size);
                var start = new ProcessStartInfo(downloaded) { UseShellExecute = true, Verb = "runas", Arguments = InstallChoice.Arguments(home,fullRepair) };
                Process.Start(start);
            }
            Close();
        }
        catch (OperationCanceledException) { if (!IsDisposed) status.Text = "Download cancelled."; DeleteDownload(); }
        catch (System.ComponentModel.Win32Exception ex) { if (!IsDisposed) status.Text = ex.NativeErrorCode == 1223 ? "Administrator approval cancelled. Nothing installed." : ex.Message; }
        catch (Exception ex) { if (!IsDisposed) status.Text = ex.Message; if (!verified || ex is InvalidDataException) DeleteDownload(); }
        finally {
            busy = false;
            if (!IsDisposed) {
                installAutomatically.Checked = false;
                experimental.Enabled = downloaded == null;
                UpdateAction();
            }
        }
    }
    void DeleteDownload() { if (downloaded != null) { try { File.Delete(downloaded); } catch { } downloaded = null; } verified = false; }
    [STAThread]
    static int Main(string[] args)
    {
        ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
        Application.EnableVisualStyles(); Application.SetCompatibleTextRenderingDefault(false);
        if (args.Length == 1 && (args[0] == "--link-settings" || args[0] == "--register-links-machine" ||
            args[0] == "--refresh-links-machine" || args[0] == "--remove-links"))
            return LinkRegistration.Run(args[0]);
        bool fresh;
        using (var mutex = new Mutex(true, "Local\\StellarysUpdater", out fresh))
        {
            if (!fresh) return 0;
            Application.Run(new Updater(Array.IndexOf(args, "--startup") >= 0));
        }
        return 0;
    }
}
