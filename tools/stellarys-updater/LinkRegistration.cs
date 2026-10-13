// Stellarys Windows link integration. SPDX-License-Identifier: LGPL-2.1-only
using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using System.Windows.Forms;
using Microsoft.Win32;

internal static class LinkRegistration
{
    // Windows requires ApplicationName to match RegisteredApplications.
    // Keep AppKey and the protocol ProgIDs stable so existing choices survive.
    internal const string AppName = "Stellarys";
    internal const string DisplayName = AppName;
    internal const string LegacyAppName = "Stellarys Viewer";
    internal const string AppKey = @"Software\StellarysViewer\LinkHandler";
    internal static readonly string[] Schemes = { "secondlife", "hop" };
    internal static string ProgId(string scheme) { return "StellarysViewer." + scheme; }
    internal static string Command(string exe) { return "\"" + Path.GetFullPath(exe) + "\" --url \"%1\""; }
    internal static string Viewer { get { return Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "StellarysViewer.exe"); } }

    static void Set(RegistryKey root, string path, string name, object value, RegistryValueKind kind)
    {
        using (RegistryKey key = root.CreateSubKey(path)) key.SetValue(name, value, kind);
    }
    static string Read(RegistryKey root, string path, string name)
    {
        using (RegistryKey key = root.OpenSubKey(path)) return key == null ? null : key.GetValue(name) as string;
    }
    internal static bool Owns(RegistryKey root, string exe)
    {
        return String.Equals(Read(root, AppKey, "Executable"), Path.GetFullPath(exe), StringComparison.OrdinalIgnoreCase);
    }
    static void RemoveApplicationName(RegistryKey root, string name)
    {
        using (RegistryKey key = root.OpenSubKey(@"Software\RegisteredApplications", true))
            if (key != null && String.Equals(key.GetValue(name) as string, AppKey + @"\Capabilities", StringComparison.OrdinalIgnoreCase))
                key.DeleteValue(name, false);
    }
    // Passing a disposable RegistryKey lets tests exercise real registry behavior
    // without touching Windows associations. Production uses only HKCU/HKLM.
    internal static void Register(RegistryKey root, string exe)
    {
        exe = Path.GetFullPath(exe);
        if (!File.Exists(exe) || !String.Equals(Path.GetFileName(exe), "StellarysViewer.exe", StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException("The Stellarys application could not be found beside this helper.");
        if (exe.IndexOf('"') >= 0) throw new InvalidDataException("Invalid application path.");
        Set(root, AppKey, "Executable", exe, RegistryValueKind.String);
        string capabilities = AppKey + @"\Capabilities";
        Set(root, capabilities, "ApplicationName", DisplayName, RegistryValueKind.String);
        Set(root, capabilities, "ApplicationDescription", "Open Second Life and hop location links with Stellarys Viewer.", RegistryValueKind.String);
        Set(root, capabilities, "ApplicationIcon", "\"" + exe + "\",0", RegistryValueKind.String);
        foreach (string scheme in Schemes)
        {
            string id = ProgId(scheme), key = @"Software\Classes\" + id;
            Set(root, key, "", "Stellarys " + scheme + " location", RegistryValueKind.String);
            Set(root, key, "URL Protocol", "", RegistryValueKind.String);
            Set(root, key + @"\DefaultIcon", "", "\"" + exe + "\",0", RegistryValueKind.String);
            Set(root, key + @"\shell\open", "FriendlyAppName", DisplayName, RegistryValueKind.String);
            Set(root, key + @"\Application", "ApplicationName", DisplayName, RegistryValueKind.String);
            Set(root, key + @"\Application", "ApplicationIcon", "\"" + exe + "\",0", RegistryValueKind.String);
            Set(root, key + @"\shell\open\command", "", Command(exe), RegistryValueKind.String);
            Set(root, capabilities + @"\URLAssociations", scheme, id, RegistryValueKind.String);
            // Windows Settings enumerates only known URL protocols. Declare the
            // scheme without writing its default value or an open command.
            using (RegistryKey protocol = root.CreateSubKey(@"Software\Classes\" + scheme))
                if (protocol.GetValue("URL Protocol") == null)
                    protocol.SetValue("URL Protocol", "", RegistryValueKind.String);
            Set(root, @"Software\Classes\" + scheme + @"\OpenWithProgids", id, new byte[0], RegistryValueKind.None);
        }
        Set(root, @"Software\RegisteredApplications", AppName, capabilities, RegistryValueKind.String);
        // Remove only our old alias, after the replacement is fully written.
        RemoveApplicationName(root, LegacyAppName);
        // No protocol default, UserChoice or other viewer key is changed.
    }
    internal static void Remove(RegistryKey root, string exe)
    {
        if (!Owns(root, exe)) return; // Another installation owns registration.
        foreach (string scheme in Schemes)
        {
            string id = ProgId(scheme), key = @"Software\Classes\" + id;
            if (!String.Equals(Read(root, key + @"\shell\open\command", ""), Command(exe), StringComparison.OrdinalIgnoreCase))
                return; // Preserve a changed registration rather than guessing.
        }
        foreach (string scheme in Schemes)
        {
            string id = ProgId(scheme);
            root.DeleteSubKeyTree(@"Software\Classes\" + id, false);
            using (RegistryKey key = root.OpenSubKey(@"Software\Classes\" + scheme + @"\OpenWithProgids", true))
                if (key != null) key.DeleteValue(id, false);
        }
        RemoveApplicationName(root, AppName);
        RemoveApplicationName(root, LegacyAppName);
        root.DeleteSubKeyTree(AppKey, false);
    }

    [DllImport("shell32.dll")]
    static extern void SHChangeNotify(uint eventId, uint flags, IntPtr item1, IntPtr item2);
    [DllImport("shlwapi.dll", CharSet = CharSet.Unicode)]
    static extern int AssocQueryString(uint flags, uint str, string assoc, string extra, StringBuilder output, ref uint length);
    internal static void Notify() { SHChangeNotify(0x08000000, 0, IntPtr.Zero, IntPtr.Zero); }
    internal static string CurrentHandler(string scheme)
    {
        var text = new StringBuilder(32768); uint length = (uint)text.Capacity;
        // ASSOCF_IS_PROTOCOL, ASSOCSTR_EXECUTABLE: query Windows' effective choice.
        int hr = AssocQueryString(0x1000, 2, scheme, "open", text, ref length);
        if (hr != 0 || text.Length == 0) return "No app selected";
        string exe = text.ToString();
        if (String.Equals(exe, Viewer, StringComparison.OrdinalIgnoreCase)) return "Stellarys (this installation)";
        string name = Path.GetFileNameWithoutExtension(exe);
        if (String.Equals(name, "StellarysViewer", StringComparison.OrdinalIgnoreCase)) return "Stellarys (another installation)";
        if (name.IndexOf("firestorm", StringComparison.OrdinalIgnoreCase) >= 0) return "Firestorm";
        if (name.IndexOf("blackdragon", StringComparison.OrdinalIgnoreCase) >= 0 || name.IndexOf("black-dragon", StringComparison.OrdinalIgnoreCase) >= 0) return "Black Dragon";
        return name;
    }
    internal static string DefaultsUri()
    {
        return "ms-settings:defaultapps?registeredAppUser=" + Uri.EscapeDataString(AppName);
    }
    internal static void OpenDefaults()
    {
        Process.Start(new ProcessStartInfo(DefaultsUri()) { UseShellExecute = true });
    }
    internal static int Run(string mode)
    {
        if (mode == "--link-settings") { Application.Run(new LinkSettingsForm()); return 0; }
        try
        {
            if (mode == "--register-links-machine" || mode == "--refresh-links-machine")
            {
                using (RegistryKey root = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64))
                    if (mode == "--register-links-machine" || Owns(root, Viewer)) Register(root, Viewer);
            }
            else if (mode == "--remove-links")
            {
                using (RegistryKey root = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)) Remove(root, Viewer);
                using (RegistryKey root = RegistryKey.OpenBaseKey(RegistryHive.CurrentUser, RegistryView.Registry64)) Remove(root, Viewer);
            }
            else return 2;
            Notify(); return 0;
        }
        catch { return 3; } // Installer reports failure; no personal data in logs.
    }
}

internal sealed class LinkSettingsForm : Form
{
    readonly Label secondLife, hop, message;
    internal LinkSettingsForm()
    {
        Text = "Stellarys Viewer — Link settings";
        Font = new Font("Segoe UI", 10); BackColor = Color.White;
        ClientSize = new Size(440, 250); FormBorderStyle = FormBorderStyle.FixedDialog;
        MaximizeBox = false; MinimizeBox = false; StartPosition = FormStartPosition.CenterScreen;
        Controls.Add(new Label { Text = "Second Life links", Font = new Font(Font.FontFamily, 16, FontStyle.Bold), Left = 18, Top = 14, Width = 400, Height = 32 });
        Controls.Add(new Label { Text = "Choose which viewer opens your map links.", Left = 18, Top = 51, Width = 404, Height = 24 });
        var handlers = new Panel { Left = 18, Top = 84, Width = 404, Height = 72, BackColor = Color.FromArgb(245, 244, 248) };
        handlers.Controls.Add(new Label { Text = "Second Life", Left = 12, Top = 10, Width = 110, Height = 23, ForeColor = Color.FromArgb(90, 86, 99) });
        handlers.Controls.Add(new Label { Text = "Hop", Left = 12, Top = 41, Width = 110, Height = 23, ForeColor = Color.FromArgb(90, 86, 99) });
        secondLife = new Label { Left = 132, Top = 10, Width = 260, Height = 23, AutoEllipsis = true };
        hop = new Label { Left = 132, Top = 41, Width = 260, Height = 23, AutoEllipsis = true };
        handlers.Controls.Add(secondLife); handlers.Controls.Add(hop); Controls.Add(handlers);
        message = new Label { Text = "In Default apps, search link types: secondlife, then hop.\r\nSelect Stellarys for each.", Left = 18, Top = 164, Width = 404, Height = 32, Font = new Font(Font.FontFamily, 9), ForeColor = Color.FromArgb(90, 86, 99), AutoEllipsis = true };
        Controls.Add(message);
        var setup = new Button { Text = "Set up SL links…", Left = 18, Top = 202, Width = 150, Height = 32,
            BackColor = Color.FromArgb(92, 73, 149), ForeColor = Color.White, FlatStyle = FlatStyle.Flat, UseVisualStyleBackColor = false };
        setup.FlatAppearance.BorderSize = 0;
        var refresh = new LinkLabel { Text = "Refresh", Left = 181, Top = 209, Width = 70, Height = 24, LinkColor = Color.FromArgb(92, 73, 149) };
        var close = new Button { Text = "Close", Left = 332, Top = 202, Width = 90, Height = 32, DialogResult = DialogResult.Cancel };
        Controls.Add(setup); Controls.Add(refresh); Controls.Add(close); CancelButton = close;
        setup.Click += (sender, e) => {
            try {
                using (RegistryKey root = RegistryKey.OpenBaseKey(RegistryHive.CurrentUser, RegistryView.Registry64)) LinkRegistration.Register(root, LinkRegistration.Viewer);
                LinkRegistration.Notify(); LinkRegistration.OpenDefaults(); RefreshStatus();
            } catch (InvalidDataException) {
                message.Text = "Viewer missing. Open link setup from Stellarys Preferences.";
            } catch {
                message.Text = "Windows link setup failed. Please retry or use Default apps.";
            }
        };
        refresh.LinkClicked += (sender, e) => RefreshStatus(); close.Click += (sender, e) => Close();
        Activated += (sender, e) => RefreshStatus();
        RefreshStatus();
    }
    void RefreshStatus()
    {
        secondLife.Text = LinkRegistration.CurrentHandler("secondlife");
        hop.Text = LinkRegistration.CurrentHandler("hop");
    }
}
