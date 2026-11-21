package io.github.codepro47rd.flowpdf;

import com.sun.jna.Library;
import com.sun.jna.Native;
import com.sun.jna.Pointer;
import com.sun.jna.Structure;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;

public class FlowPdfEngine {

    @Structure.FieldOrder({"data", "length", "success", "errorMessage"})
    public static class FlowPdfResult extends Structure {
        public Pointer data;
        public long length;
        public byte success;
        public Pointer errorMessage;

        public static class ByValue extends FlowPdfResult implements Structure.ByValue {}
    }

    public interface FlowPdfNativeLib extends Library {
        FlowPdfResult.ByValue flowpdf_render_pdf(byte[] docJson, byte[] dataJson);
        FlowPdfResult.ByValue flowpdf_extract_text(byte[] pdfData, long pdfLen);
        FlowPdfResult.ByValue flowpdf_extract_json(byte[] pdfData, long pdfLen, byte[] optionsJson);
        int flowpdf_register_font(byte[] fontName, byte[] fontBytes, long fontLen);
        void flowpdf_free_result(FlowPdfResult.ByValue result);
        Pointer flowpdf_version();
    }

    private static FlowPdfNativeLib libInstance;
    private static File extractedTempFile;

    private static synchronized FlowPdfNativeLib getLib() {
        if (libInstance == null) {
            String libPath = resolveOrExtractLibrary();
            libInstance = Native.load(libPath, FlowPdfNativeLib.class);
        }
        return libInstance;
    }

    private static String resolveOrExtractLibrary() {
        String os = System.getProperty("os.name").toLowerCase();
        String rid;
        String fileName;

        if (os.contains("win")) {
            rid = "win-x64";
            fileName = "flowpdf_native.dll";
        } else if (os.contains("mac")) {
            rid = "osx-x64";
            fileName = "libflowpdf_native.dylib";
        } else {
            rid = "linux-x64";
            fileName = "libflowpdf_native.so";
        }

        // Check local filesystem paths
        List<String> searchPaths = Arrays.asList(
            "src/main/resources/runtimes/" + rid + "/native/" + fileName,
            "runtimes/" + rid + "/native/" + fileName,
            "../runtimes/" + rid + "/native/" + fileName,
            "../../runtimes/" + rid + "/native/" + fileName,
            "../csharp/FlowPdf/runtimes/" + rid + "/native/" + fileName,
            "../../sdk/csharp/FlowPdf/runtimes/" + rid + "/native/" + fileName,
            fileName
        );

        for (String p : searchPaths) {
            File f = new File(p);
            if (f.exists() && f.isFile()) {
                return f.getAbsolutePath();
            }
        }

        // Extract from JAR resource
        String resourcePath = "/runtimes/" + rid + "/native/" + fileName;
        try (InputStream in = FlowPdfEngine.class.getResourceAsStream(resourcePath)) {
            if (in != null) {
                Path tempDir = Files.createTempDirectory("flowpdf_native_");
                File tempFile = tempDir.resolve(fileName).toFile();
                tempFile.deleteOnExit();

                try (FileOutputStream out = new FileOutputStream(tempFile)) {
                    byte[] buffer = new byte[8192];
                    int bytesRead;
                    while ((bytesRead = in.read(buffer)) != -1) {
                        out.write(buffer, 0, bytesRead);
                    }
                }
                extractedTempFile = tempFile;
                return tempFile.getAbsolutePath();
            }
        } catch (Exception e) {
            // fallback to system library loader
        }

        return fileName;
    }

    public static String getVersion() {
        Pointer ptr = getLib().flowpdf_version();
        return ptr != null ? ptr.getString(0, "UTF-8") : "FlowPDF Rust Core";
    }

    public static byte[] renderPdf(String documentJson, String dataJson) {
        FlowPdfNativeLib lib = getLib();
        byte[] docBytes = (documentJson + "\0").getBytes(StandardCharsets.UTF_8);
        byte[] dataBytes = dataJson != null ? (dataJson + "\0").getBytes(StandardCharsets.UTF_8) : null;
        FlowPdfResult.ByValue result = lib.flowpdf_render_pdf(docBytes, dataBytes);

        try {
            if (result.success == 0) {
                String err = result.errorMessage != null ? result.errorMessage.getString(0, "UTF-8") : "Unknown native error";
                throw new RuntimeException("FlowPDF Native Error: " + err);
            }

            int len = (int) result.length;
            if (len > 0 && result.data != null) {
                return result.data.getByteArray(0, len);
            }
            return new byte[0];
        } finally {
            lib.flowpdf_free_result(result);
        }
    }

    public static byte[] renderPdf(String documentJson) {
        return renderPdf(documentJson, null);
    }

    public static String extractText(byte[] pdfBytes) {
        if (pdfBytes == null || pdfBytes.length == 0) {
            return "";
        }
        FlowPdfNativeLib lib = getLib();
        FlowPdfResult.ByValue result = lib.flowpdf_extract_text(pdfBytes, pdfBytes.length);
        try {
            if (result.success == 0) {
                String err = result.errorMessage != null ? result.errorMessage.getString(0, "UTF-8") : "Unknown native error";
                throw new RuntimeException("FlowPDF Extraction Error: " + err);
            }
            int len = (int) result.length;
            if (len > 0 && result.data != null) {
                byte[] bytes = result.data.getByteArray(0, len);
                return new String(bytes, StandardCharsets.UTF_8);
            }
            return "";
        } finally {
            lib.flowpdf_free_result(result);
        }
    }

    public static String extractJson(byte[] pdfBytes, String optionsJson) {
        if (pdfBytes == null || pdfBytes.length == 0) {
            return "{}";
        }
        FlowPdfNativeLib lib = getLib();
        byte[] optBytes = optionsJson != null ? (optionsJson + "\0").getBytes(StandardCharsets.UTF_8) : null;
        FlowPdfResult.ByValue result = lib.flowpdf_extract_json(pdfBytes, pdfBytes.length, optBytes);
        try {
            if (result.success == 0) {
                String err = result.errorMessage != null ? result.errorMessage.getString(0, "UTF-8") : "Unknown native error";
                throw new RuntimeException("FlowPDF Extraction Error: " + err);
            }
            int len = (int) result.length;
            if (len > 0 && result.data != null) {
                byte[] bytes = result.data.getByteArray(0, len);
                return new String(bytes, StandardCharsets.UTF_8);
            }
            return "{}";
        } finally {
            lib.flowpdf_free_result(result);
        }
    }

    public static boolean registerFont(String fontName, byte[] fontBytes) {
        if (fontName == null || fontBytes == null || fontBytes.length == 0) return false;
        FlowPdfNativeLib lib = getLib();
        byte[] nameBytes = (fontName + "\0").getBytes(StandardCharsets.UTF_8);
        return lib.flowpdf_register_font(nameBytes, fontBytes, fontBytes.length) == 0;
    }
}
