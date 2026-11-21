using System;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.Json;
using FlowPdf.Models;
using FlowPdf.Fluent;

namespace FlowPdf.Native
{
    [StructLayout(LayoutKind.Sequential)]
    internal struct FlowPdfResultNative
    {
        public IntPtr Data;
        public UIntPtr Length;
        [MarshalAs(UnmanagedType.I1)]
        public bool Success;
        public IntPtr ErrorMessage;
    }

    /// <summary>
    /// Direct in-process C-ABI Native Bindings for FlowPDF (Rust Core).
    /// Ultra-high performance: Generates PDFs in microseconds with zero network overhead.
    /// </summary>
    public static class FlowPdfEngine
    {
        private const string LibName = "flowpdf_native";

        static FlowPdfEngine()
        {
            NativeLibrary.SetDllImportResolver(typeof(FlowPdfEngine).Assembly, DllImportResolver);
        }

        private static IntPtr DllImportResolver(string libraryName, Assembly assembly, DllImportSearchPath? searchPath)
        {
            if (libraryName != LibName && libraryName != "flowpdf" && libraryName != "libflowpdf")
                return IntPtr.Zero;

            string rid;
            string fileName;
            if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
            {
                rid = "win-x64";
                fileName = "flowpdf_native.dll";
            }
            else if (RuntimeInformation.IsOSPlatform(OSPlatform.Linux))
            {
                rid = "linux-x64";
                fileName = "libflowpdf_native.so";
            }
            else if (RuntimeInformation.IsOSPlatform(OSPlatform.OSX))
            {
                rid = "osx-x64";
                fileName = "libflowpdf_native.dylib";
            }
            else
            {
                return IntPtr.Zero;
            }

            string baseDir = AppContext.BaseDirectory;
            string asmDir = Path.GetDirectoryName(assembly.Location) ?? baseDir;

            string[] searchPaths = new[]
            {
                Path.Combine(baseDir, "runtimes", rid, "native", fileName),
                Path.Combine(asmDir, "runtimes", rid, "native", fileName),
                Path.Combine(baseDir, fileName),
                Path.Combine(asmDir, fileName),
                Path.Combine(baseDir, "..", "..", "..", "runtimes", rid, "native", fileName),
                Path.Combine(baseDir, "..", "..", "..", "..", "runtimes", rid, "native", fileName),
                Path.Combine(baseDir, "..", "..", "..", "..", "..", "sdk", "csharp", "FlowPDF", "runtimes", rid, "native", fileName),
                Path.Combine(baseDir, "..", "..", "..", "..", "..", "engine-rust", "target", "x86_64-pc-windows-gnu", "release", "flowpdf.dll"),
                Path.Combine(baseDir, "..", "..", "..", "..", "..", "engine-rust", "target", "release", "libflowpdf.so"),
            };

            foreach (var path in searchPaths)
            {
                if (File.Exists(path) && NativeLibrary.TryLoad(path, out IntPtr handle))
                {
                    return handle;
                }
            }

            if (NativeLibrary.TryLoad(libraryName, assembly, searchPath, out IntPtr defaultHandle))
            {
                return defaultHandle;
            }

            return IntPtr.Zero;
        }

        [DllImport(LibName, EntryPoint = "flowpdf_render_pdf", CallingConvention = CallingConvention.Cdecl)]
        private static extern FlowPdfResultNative NativeRenderPdf(byte[] docJson, byte[]? dataJson);

        [DllImport(LibName, EntryPoint = "flowpdf_extract_text", CallingConvention = CallingConvention.Cdecl)]
        private static extern FlowPdfResultNative NativeExtractText(byte[] pdfData, UIntPtr pdfLen);

        [DllImport(LibName, EntryPoint = "flowpdf_extract_json", CallingConvention = CallingConvention.Cdecl)]
        private static extern FlowPdfResultNative NativeExtractJson(byte[] pdfData, UIntPtr pdfLen, byte[]? optionsJson);

        [DllImport(LibName, EntryPoint = "flowpdf_register_font", CallingConvention = CallingConvention.Cdecl)]
        private static extern int NativeRegisterFont(byte[] fontName, byte[] fontBytes, UIntPtr fontLen);

        [DllImport(LibName, EntryPoint = "flowpdf_free_result", CallingConvention = CallingConvention.Cdecl)]
        private static extern void NativeFreeResult(FlowPdfResultNative result);

        [DllImport(LibName, EntryPoint = "flowpdf_version", CallingConvention = CallingConvention.Cdecl)]
        private static extern IntPtr NativeVersion();

        public static string GetVersion()
        {
            IntPtr ptr = NativeVersion();
            return Marshal.PtrToStringUTF8(ptr) ?? "Unknown";
        }

        public static bool RegisterFont(string fontName, byte[] fontBytes)
        {
            if (string.IsNullOrEmpty(fontName) || fontBytes == null || fontBytes.Length == 0)
                return false;
            byte[] nameBytes = Encoding.UTF8.GetBytes(fontName + "\0");
            int res = NativeRegisterFont(nameBytes, fontBytes, (UIntPtr)fontBytes.Length);
            return res == 0;
        }

        public static byte[] RenderPdf(string documentJson, string? dataJson = null)
        {
            byte[] docBytes = Encoding.UTF8.GetBytes(documentJson + "\0");
            byte[]? dataBytes = dataJson != null ? Encoding.UTF8.GetBytes(dataJson + "\0") : null;

            FlowPdfResultNative result = NativeRenderPdf(docBytes, dataBytes);

            try
            {
                if (!result.Success)
                {
                    string error = result.ErrorMessage != IntPtr.Zero
                        ? Marshal.PtrToStringUTF8(result.ErrorMessage) ?? "Unknown native error"
                        : "Unknown native error";
                    throw new InvalidOperationException($"FlowPDF Native Error: {error}");
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

        private static readonly JsonSerializerOptions JsonOptions = new()
        {
            DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull
        };

        public static byte[] RenderPdf(DocumentDefinition document, object? data = null)
        {
            string docJson = JsonSerializer.Serialize(document, JsonOptions);
            string? dataJson = data != null ? JsonSerializer.Serialize(data, JsonOptions) : null;
            return RenderPdf(docJson, dataJson);
        }

        public static byte[] RenderPdf(ReportDocument document, object? data = null)
        {
            return RenderPdf(document.Build(), data);
        }

        public static string ExtractText(byte[] pdfBytes)
        {
            if (pdfBytes == null || pdfBytes.Length == 0)
                throw new ArgumentException("PDF bytes cannot be null or empty", nameof(pdfBytes));

            FlowPdfResultNative result = NativeExtractText(pdfBytes, (UIntPtr)pdfBytes.Length);
            try
            {
                if (!result.Success)
                {
                    string error = result.ErrorMessage != IntPtr.Zero
                        ? Marshal.PtrToStringUTF8(result.ErrorMessage) ?? "Unknown native error"
                        : "Unknown native error";
                    throw new InvalidOperationException($"FlowPDF Extraction Error: {error}");
                }

                int length = (int)result.Length.ToUInt32();
                if (length == 0 || result.Data == IntPtr.Zero)
                    return string.Empty;

                byte[] managedBytes = new byte[length];
                Marshal.Copy(result.Data, managedBytes, 0, length);
                return Encoding.UTF8.GetString(managedBytes);
            }
            finally
            {
                NativeFreeResult(result);
            }
        }

        public static string ExtractJson(byte[] pdfBytes, string? optionsJson = null)
        {
            if (pdfBytes == null || pdfBytes.Length == 0)
                throw new ArgumentException("PDF bytes cannot be null or empty", nameof(pdfBytes));

            byte[]? optBytes = optionsJson != null ? Encoding.UTF8.GetBytes(optionsJson + "\0") : null;
            FlowPdfResultNative result = NativeExtractJson(pdfBytes, (UIntPtr)pdfBytes.Length, optBytes);
            try
            {
                if (!result.Success)
                {
                    string error = result.ErrorMessage != IntPtr.Zero
                        ? Marshal.PtrToStringUTF8(result.ErrorMessage) ?? "Unknown native error"
                        : "Unknown native error";
                    throw new InvalidOperationException($"FlowPDF Extraction Error: {error}");
                }

                int length = (int)result.Length.ToUInt32();
                if (length == 0 || result.Data == IntPtr.Zero)
                    return "{}";

                byte[] managedBytes = new byte[length];
                Marshal.Copy(result.Data, managedBytes, 0, length);
                return Encoding.UTF8.GetString(managedBytes);
            }
            finally
            {
                NativeFreeResult(result);
            }
        }
    }
}
