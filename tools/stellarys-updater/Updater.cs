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
[assembly: System.Reflection.AssemblyVersion("0.1.0.0")]

internal sealed class Release
{
    internal const string Repository = "https://github.com/NekoMisa/stellarys-viewer";
    internal const string Api = "https://api.github.com/repos/NekoMisa/stellarys-viewer/releases/latest";
    internal const string Current = "0.1.0";
    internal Version Version;
    internal string Tag, Notes, Url, Digest, Name;
    internal long Size;
    internal static Version ParseVersion(string value)
    {
        if (!Regex.IsMatch(value ?? "", @"^\d+\.\d+\.\d+$")) throw new InvalidDataException("Invalid stable version.");
        return new Version(value);
    }
    internal static Release Parse(string json)
    {
        var data = new JavaScriptSerializer { MaxJsonLength = 2097152 }.Deserialize<Dictionary<string, object>>(json);
        if ((bool)data["draft"] || (bool)data["prerelease"]) throw new InvalidDataException("Not a stable release.");
        string tag = (string)data["tag_name"];
        if (!tag.StartsWith("v", StringComparison.Ordinal)) throw new InvalidDataException("Expected vMAJOR.MINOR.PATCH release tag.");
        var r = new Release { Tag = tag, Version = ParseVersion(tag.Substring(1)), Notes = data.ContainsKey("body") ? data["body"] as string ?? "" : "" };
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

internal sealed class Updater : Form
{
    readonly Label status = new Label { Dock = DockStyle.Top, Height = 52, Padding = new Padding(8) };
    readonly TextBox notes = new TextBox { Multiline = true, ReadOnly = true, ScrollBars = ScrollBars.Vertical, Dock = DockStyle.Fill };
    readonly Button action = new Button { Text = "Checking…", Enabled = false, Width = 180 };
    readonly CheckBox startup = new CheckBox { Text = "Check for updates when Stellarys starts", AutoSize = true };
    readonly CancellationTokenSource cancel = new CancellationTokenSource();
    readonly string home = AppDomain.CurrentDomain.BaseDirectory.TrimEnd(Path.DirectorySeparatorChar);
    readonly string preferences = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "Stellarys_x64", "updater-disable-startup");
    readonly bool quiet;
    Release release;
    string downloaded;
    bool verified;
    bool busy;
    internal Updater(bool automatic)
    {
        quiet = automatic;
        Text = "Stellarys Viewer — Updates"; Size = new Size(640, 440); MinimumSize = new Size(540, 360);
        StartPosition = FormStartPosition.CenterScreen;
        var buttons = new FlowLayoutPanel { Dock = DockStyle.Bottom, Height = 75, Padding = new Padding(8), FlowDirection = FlowDirection.LeftToRight };
        var close = new Button { Text = "Close", Width = 90 };
        close.Click += (s,e) => Close();
        startup.Checked = !File.Exists(preferences);
        startup.CheckedChanged += (s,e) => {
            try { Directory.CreateDirectory(Path.GetDirectoryName(preferences)); if (startup.Checked) File.Delete(preferences); else File.WriteAllText(preferences, "disabled"); }
            catch (Exception ex) { MessageBox.Show(this, "Could not save update preference: " + ex.Message); }
        };
        buttons.Controls.Add(action); buttons.Controls.Add(close); buttons.Controls.Add(startup);
        Controls.Add(notes); Controls.Add(status); Controls.Add(buttons);
        action.Click += async (s,e) => await DownloadAndInstall();
        FormClosing += (s,e) => cancel.Cancel();
        Shown += async (s,e) => { if (quiet) Hide(); await Check(); };
        if (quiet) { Opacity = 0; ShowInTaskbar = false; }
    }
    void Reveal() { Opacity = 1; ShowInTaskbar = true; Show(); Activate(); }
    static HttpClient Client()
    {
        var c = new HttpClient(new HttpClientHandler { AllowAutoRedirect = false });
        c.Timeout = TimeSpan.FromMinutes(15);
        c.DefaultRequestHeaders.UserAgent.ParseAdd("Stellarys-Viewer/" + Release.Current);
        return c;
    }
    async Task Check()
    {
        if (quiet && File.Exists(preferences)) { Close(); return; }
        status.Text = "Checking GitHub Releases…";
        try
        {
            using (var c = Client())
            using (var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancel.Token))
            {
                timeout.CancelAfter(TimeSpan.FromSeconds(30));
                using (var response = await c.GetAsync(Release.Api, HttpCompletionOption.ResponseHeadersRead, timeout.Token))
                {
                    if (response.StatusCode == HttpStatusCode.NotFound) { Finish("No public Stellarys releases are available yet."); return; }
                    response.EnsureSuccessStatusCode();
                    using (var stream = await response.Content.ReadAsStreamAsync())
                    using (var bytes = new MemoryStream())
                    {
                        byte[] buffer = new byte[16384]; int n;
                        while ((n = await stream.ReadAsync(buffer, 0, buffer.Length, timeout.Token)) != 0)
                        { if (bytes.Length + n > 2097152) throw new InvalidDataException("Release metadata is too large."); bytes.Write(buffer, 0, n); }
                        release = Release.Parse(System.Text.Encoding.UTF8.GetString(bytes.ToArray()));
                    }
                }
            }
            if (release.Version <= Release.ParseVersion(Release.Current)) { Finish("Stellarys " + Release.Current + " is up to date."); return; }
            Reveal();
            status.Text = "Stellarys " + release.Version + " is available (installed: " + Release.Current + "). Download and install it?";
            notes.Text = release.Notes;
            action.Text = "Download update"; action.Enabled = true;
        }
        catch (OperationCanceledException) { if (!IsDisposed) Finish("Update check cancelled or timed out."); }
        catch (Exception ex) { if (!IsDisposed) Finish("Could not check for updates. " + ex.Message); }
    }
    void Finish(string message) { if (quiet) Close(); else { status.Text = message; action.Text = "No update ready"; } }
    async Task DownloadAndInstall()
    {
        if (busy || release == null) return;
        busy = true; action.Enabled = false;
        try
        {
            if (downloaded == null)
            {
                string dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Stellarys_x64", "updates", Guid.NewGuid().ToString("N"));
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
            if (MessageBox.Show(this, "The download is verified. Install now?\n\nStellarys will be asked to close normally. Save your work first and respond to any viewer shutdown prompts. Setup will then request administrator permission. Cancel leaves the viewer running.", "Ready to update", MessageBoxButtons.OKCancel) != DialogResult.OK)
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
                    if (!process.HasExited && !process.CloseMainWindow())
                        throw new InvalidOperationException("Stellarys could not be asked to close. Close it normally, then retry Install update.");
                status.Text = "Waiting for Stellarys to close. Please respond to any viewer shutdown prompts…";
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
                var start = new ProcessStartInfo(downloaded) { UseShellExecute = true, Verb = "runas", Arguments = "/D=" + home };
                Process.Start(start);
            }
            Close();
        }
        catch (OperationCanceledException) { if (!IsDisposed) status.Text = "Download cancelled."; DeleteDownload(); }
        catch (System.ComponentModel.Win32Exception ex) { if (!IsDisposed) status.Text = ex.NativeErrorCode == 1223 ? "Administrator approval cancelled. Nothing installed." : ex.Message; }
        catch (Exception ex) { if (!IsDisposed) status.Text = ex.Message; if (!verified || ex is InvalidDataException) DeleteDownload(); }
        finally { busy = false; if (!IsDisposed) { action.Enabled = true; action.Text = downloaded == null ? "Retry download" : "Install update"; } }
    }
    void DeleteDownload() { if (downloaded != null) { try { File.Delete(downloaded); } catch { } downloaded = null; } verified = false; }
    [STAThread]
    static int Main(string[] args)
    {
        ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
        Application.EnableVisualStyles(); Application.SetCompatibleTextRenderingDefault(false);
        bool fresh;
        using (var mutex = new Mutex(true, "Local\\StellarysUpdater", out fresh))
        {
            if (!fresh) return 0;
            Application.Run(new Updater(Array.IndexOf(args, "--startup") >= 0));
        }
        return 0;
    }
}
