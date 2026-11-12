using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;

namespace ReportForge.Native
{
    [StructLayout(LayoutKind.Sequential)]
    internal struct ReportForgeResultNative
    {
        public IntPtr Data;
        public UIntPtr Length;
        [MarshalAs(UnmanagedType.I1)]
        public bool Success;
        public IntPtr ErrorMessage;
    }

    /// <summary>
    /// Direct in-process C-ABI Native Bindings for ReportForge v2.0 (Rust Core).
    /// Ultra-high performance: Generates PDFs in microseconds with zero network overhead.
    /// </summary>
    public static class ReportForgeEngine
    {
        private const string LibName = "reportforge";

        [DllImport(LibName, EntryPoint = "reportforge_render_pdf", CallingConvention = CallingConvention.Cdecl)]
        private static extern ReportForgeResultNative NativeRenderPdf(byte[] docJson, byte[]? dataJson);

        [DllImport(LibName, EntryPoint = "reportforge_free_result", CallingConvention = CallingConvention.Cdecl)]
        private static extern void NativeFreeResult(ReportForgeResultNative result);

        [DllImport(LibName, EntryPoint = "reportforge_version", CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr NativeVersion();

        public static string GetVersion()
        {
            IntPtr ptr = NativeVersion();
            return Marshal.PtrToStringUTF8(ptr) ?? "Unknown";
        }

        public static byte[] RenderPdf(string documentJson, string? dataJson = null)
        {
            byte[] docBytes = Encoding.UTF8.GetBytes(documentJson + "\0");
            byte[]? dataBytes = dataJson != null ? Encoding.UTF8.GetBytes(dataJson + "\0") : null;

            ReportForgeResultNative result = NativeRenderPdf(docBytes, dataBytes);

            try
            {
                if (!result.Success)
                {
                    string error = result.ErrorMessage != IntPtr.Zero
                        ? Marshal.PtrToStringUTF8(result.ErrorMessage) ?? "Unknown native error"
                        : "Unknown native error";
                    throw new InvalidOperationException($"ReportForge Native Error: {error}");
                }

                int length = (int)result.Length.ToUInt32();
                byte[] managedBytes = new byte[length];
                if (length > 0 && result.Data != IntPtr.Zero)
                {
                    Marshal.Copy(result.Data, managedBytes, 0, length);
                }
                return managedBytes;
            }
            finally
            {
                NativeFreeResult(result);
            }
        }
    }
}
