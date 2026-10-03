// SPDX-License-Identifier: LGPL-2.1-only
// Local IPC requests graceful update shutdown; this is never a browser SLURL.
using System;
using System.Runtime.InteropServices;
using System.Text;
internal static class ViewerShutdown
{
    internal const int MessageType = 0x53555154;
    internal const string Payload = "Stellarys update approved";
    [StructLayout(LayoutKind.Sequential)]
    internal struct CopyData { internal IntPtr Type; internal int Bytes; internal IntPtr Data; }
    [DllImport("user32.dll", SetLastError = true)]
    static extern IntPtr SendMessageTimeout(IntPtr window, uint message, IntPtr wParam,
        ref CopyData data, uint flags, uint timeout, out IntPtr result);
    internal static void Request(IntPtr window)
    {
        if (window == IntPtr.Zero) throw new InvalidOperationException("Stellarys has no available window. Close it normally, then retry installation.");
        byte[] bytes = Encoding.UTF8.GetBytes(Payload + "\0");
        IntPtr memory = Marshal.AllocHGlobal(bytes.Length);
        try
        {
            Marshal.Copy(bytes, 0, memory, bytes.Length);
            var data = new CopyData { Type = new IntPtr(MessageType), Bytes = bytes.Length, Data = memory };
            IntPtr result;
            // WM_COPYDATA; SMTO_BLOCK | SMTO_ABORTIFHUNG. Do not hang or kill a viewer.
            if (SendMessageTimeout(window, 0x004A, IntPtr.Zero, ref data, 3, 2000, out result) == IntPtr.Zero)
                throw new InvalidOperationException("Stellarys did not respond to update shutdown. Close it normally, then retry installation.");
        }
        finally { Marshal.FreeHGlobal(memory); }
    }
}
