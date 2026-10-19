// Tests use a disposable registry subtree; never real Windows associations.
using System;
using System.IO;
using Microsoft.Win32;
internal static class LinkRegistrationTests
{
    static int checks;
    static void Check(bool value) { if (!value) throw new Exception("Link registration check failed."); checks++; }
    static string Read(RegistryKey root, string key, string name)
    { using (RegistryKey k = root.OpenSubKey(key)) return k == null ? null : k.GetValue(name) as string; }
    static int Main()
    {
        string name = @"Software\StellarysDisposableTests\" + Guid.NewGuid().ToString("N");
        string files = Path.Combine(Path.GetTempPath(), "Stellarys link test " + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(files);
        string exe = Path.Combine(files, "StellarysViewer.exe"); File.WriteAllText(exe, "fixture only");
        string otherDir = Path.Combine(files, "other install"); Directory.CreateDirectory(otherDir);
        string other = Path.Combine(otherDir, "StellarysViewer.exe"); File.WriteAllText(other, "fixture only");
        try
        {
            using (RegistryKey root = Registry.CurrentUser.CreateSubKey(name))
            {
                using (RegistryKey key = root.CreateSubKey(@"Software\Classes\secondlife\shell\open\command")) key.SetValue("", "existing viewer command");
                using (RegistryKey key = root.CreateSubKey(@"Software\Classes\secondlife")) key.SetValue("URL Protocol", "existing protocol marker");
                using (RegistryKey key = root.CreateSubKey(@"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\secondlife\UserChoice"))
                { key.SetValue("ProgId", "OtherViewer"); key.SetValue("Hash", "unchanged fixture"); }
                using (RegistryKey key = root.CreateSubKey(@"Software\Classes\hop\OpenWithProgids")) key.SetValue("OtherViewer.hop", new byte[0], RegistryValueKind.None);
                using (RegistryKey legacy = root.CreateSubKey(LinkRegistration.AppKey + @"\Capabilities"))
                    legacy.SetValue("ApplicationName", "Stellarys Viewer 0.1.3");
                using (RegistryKey legacy = root.CreateSubKey(@"Software\RegisteredApplications"))
                    legacy.SetValue(LinkRegistration.LegacyAppName, LinkRegistration.AppKey + @"\Capabilities");
                LinkRegistration.Register(root, exe);
                Check(Read(root, LinkRegistration.AppKey + @"\Capabilities", "ApplicationName") == "Stellarys");
                Check(Read(root, LinkRegistration.AppKey + @"\Capabilities", "ApplicationName") == LinkRegistration.AppName);
                Check(Read(root, @"Software\RegisteredApplications", LinkRegistration.LegacyAppName) == null);
                Check(LinkRegistration.DefaultsUri() == "ms-settings:defaultapps?registeredAppUser=Stellarys");
                Check(LinkRegistration.Owns(root, exe)); Check(!LinkRegistration.Owns(root, other));
                Check(Read(root, @"Software\RegisteredApplications", LinkRegistration.AppName) == LinkRegistration.AppKey + @"\Capabilities");
                Check(Read(root, @"Software\Classes\secondlife\shell\open\command", "") == "existing viewer command");
                Check(Read(root, @"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\secondlife\UserChoice", "ProgId") == "OtherViewer");
                Check(Read(root, @"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\secondlife\UserChoice", "Hash") == "unchanged fixture");
                foreach (string scheme in LinkRegistration.Schemes)
                {
                    string id = LinkRegistration.ProgId(scheme);
                    Check(Read(root, @"Software\Classes\" + id + @"\shell\open\command", "") == "\"" + exe + "\" --url \"%1\"");
                    Check(Read(root, @"Software\Classes\" + id, "URL Protocol") == "");
                    Check(Read(root, @"Software\Classes\" + id + @"\Application", "ApplicationName") == "Stellarys");
                    Check(Read(root, @"Software\Classes\" + id + @"\shell\open", "FriendlyAppName") == "Stellarys");
                    Check(Read(root, LinkRegistration.AppKey + @"\Capabilities\URLAssociations", scheme) == id);
                    using (RegistryKey key = root.OpenSubKey(@"Software\Classes\" + scheme + @"\OpenWithProgids"))
                        Check(key.GetValueKind(id) == RegistryValueKind.None);
                }
                Check(Read(root, @"Software\Classes\secondlife", "URL Protocol") == "existing protocol marker");
                Check(Read(root, @"Software\Classes\hop", "URL Protocol") == "");
                Check(Read(root, @"Software\Classes\hop", "") == null);
                Check(Read(root, @"Software\Classes\hop\shell\open\command", "") == null);
                LinkRegistration.Register(root, exe); Check(LinkRegistration.Owns(root, exe)); // update in place
                // A similarly named application with a different capabilities path is untouched.
                using (RegistryKey legacy = root.CreateSubKey(@"Software\RegisteredApplications"))
                    legacy.SetValue(LinkRegistration.LegacyAppName, @"Software\Unrelated\Capabilities");
                LinkRegistration.Register(root, exe);
                Check(Read(root, @"Software\RegisteredApplications", LinkRegistration.LegacyAppName) == @"Software\Unrelated\Capabilities");
                LinkRegistration.Remove(root, other); Check(LinkRegistration.Owns(root, exe)); // stale uninstall
                LinkRegistration.Register(root, other); LinkRegistration.Remove(root, exe); // new folder owns it
                Check(LinkRegistration.Owns(root, other));
                using (RegistryKey key = root.OpenSubKey(@"Software\Classes\StellarysViewer.hop\shell\open\command", true)) key.SetValue("", "changed command");
                LinkRegistration.Remove(root, other); Check(LinkRegistration.Owns(root, other)); // preserve modified key
                LinkRegistration.Register(root, other); LinkRegistration.Remove(root, other);
                Check(!LinkRegistration.Owns(root, other)); Check(Read(root, @"Software\RegisteredApplications", LinkRegistration.AppName) == null);
                Check(Read(root, @"Software\RegisteredApplications", LinkRegistration.LegacyAppName) == @"Software\Unrelated\Capabilities");
                foreach (string scheme in LinkRegistration.Schemes)
                {
                    Check(Read(root, @"Software\Classes\" + LinkRegistration.ProgId(scheme), "URL Protocol") == null);
                    using (RegistryKey key = root.OpenSubKey(@"Software\Classes\" + scheme + @"\OpenWithProgids"))
                        Check(key.GetValue(LinkRegistration.ProgId(scheme)) == null);
                }
                Check(Read(root, @"Software\Classes\secondlife\shell\open\command", "") == "existing viewer command");
                using (RegistryKey key = root.OpenSubKey(@"Software\Classes\hop\OpenWithProgids")) Check(key.GetValue("OtherViewer.hop") != null);
                Check(Read(root, @"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\secondlife\UserChoice", "Hash") == "unchanged fixture");
                bool rejected = false;
                try { LinkRegistration.Register(root, Path.Combine(files, "missing", "StellarysViewer.exe")); } catch (InvalidDataException) { rejected = true; }
                Check(rejected); Check(!LinkRegistration.Owns(root, other));
                // Older installations can be unregistered directly, without first upgrading.
                LinkRegistration.Register(root, exe);
                using (RegistryKey legacy = root.OpenSubKey(@"Software\RegisteredApplications", true))
                {
                    legacy.DeleteValue(LinkRegistration.AppName);
                    legacy.SetValue(LinkRegistration.LegacyAppName, LinkRegistration.AppKey + @"\Capabilities");
                }
                LinkRegistration.Remove(root, exe);
                Check(Read(root, @"Software\RegisteredApplications", LinkRegistration.LegacyAppName) == null);
                Check(!LinkRegistration.Owns(root, exe));
            }
            Console.WriteLine(checks + " registry fixture checks passed; real Windows associations untouched."); return 0;
        }
        finally
        {
            Registry.CurrentUser.DeleteSubKeyTree(name, false);
            File.Delete(exe); File.Delete(other); Directory.Delete(otherDir); Directory.Delete(files);
        }
    }
}
