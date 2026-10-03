using System;
using System.Runtime.InteropServices;
using System.Windows.Forms;
internal static class ViewerShutdownTests
{
    sealed class Fixture : NativeWindow, IDisposable
    {
        internal int Calls;
        internal Fixture() { CreateHandle(new CreateParams { Parent = new IntPtr(-3), Caption = "Stellarys IPC fixture" }); }
        protected override void WndProc(ref Message message)
        {
            if (message.Msg == 0x004A)
            {
                var data = (ViewerShutdown.CopyData)Marshal.PtrToStructure(message.LParam, typeof(ViewerShutdown.CopyData));
                if (data.Type.ToInt64() != 0x53555154 || data.Bytes != 26 ||
                    Marshal.PtrToStringAnsi(data.Data) != "Stellarys update approved") throw new Exception("IPC contract mismatch.");
                Calls++; message.Result = IntPtr.Zero; return;
            }
            base.WndProc(ref message);
        }
        public void Dispose() { DestroyHandle(); }
    }
    [STAThread]
    static int Main()
    {
        using (var fixture = new Fixture())
        {
            ViewerShutdown.Request(fixture.Handle);
            if (fixture.Calls != 1) throw new Exception("Shutdown request not received exactly once.");
        }
        bool rejected = false;
        try { ViewerShutdown.Request(IntPtr.Zero); } catch (InvalidOperationException) { rejected = true; }
        if (!rejected) throw new Exception("Missing window accepted.");
        Console.WriteLine("Graceful shutdown IPC contract and missing-window checks passed; no viewer was closed."); return 0;
    }
}
