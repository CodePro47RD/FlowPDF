package dev.reportforge;

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

public class ReportForgeEngine {

    @Structure.FieldOrder({"data", "length", "success", "errorMessage"})
    public static class ReportForgeResult extends Structure {
        public Pointer data;
        public long length;
        public byte success;
        public Pointer errorMessage;

        public static class ByValue extends ReportForgeResult implements Structure.ByValue {}
    }

    public interface ReportForgeNativeLib extends Library {
        ReportForgeResult.ByValue reportforge_render_pdf(byte[] docJson, byte[] dataJson);
        void reportforge_free_result(ReportForgeResult.ByValue result);
        Pointer reportforge_version();
    }

    private static ReportForgeNativeLib libInstance;
    private static File extractedTempFile;

    private static synchronized ReportForgeNativeLib getLib() {
        if (libInstance == null) {
            String libPath = resolveOrExtractLibrary();
            libInstance = Native.load(libPath, ReportForgeNativeLib.class);
        }
        return libInstance;
    }

    private static String resolveOrExtractLibrary() {
        String os = System.getProperty("os.name").toLowerCase();
        String rid;
        String fileName;

        if (os.contains("win")) {
            rid = "win-x64";
            fileName = "reportforge_native.dll";
        } else if (os.contains("mac")) {
            rid = "osx-x64";
            fileName = "libreportforge_native.dylib";
        } else {
            rid = "linux-x64";
            fileName = "libreportforge_native.so";
        }

        // Check local filesystem paths
        List<String> searchPaths = Arrays.asList(
            "src/main/resources/runtimes/" + rid + "/native/" + fileName,
            "runtimes/" + rid + "/native/" + fileName,
            "../runtimes/" + rid + "/native/" + fileName,
            "../../runtimes/" + rid + "/native/" + fileName,
            "../csharp/ReportForge/runtimes/" + rid + "/native/" + fileName,
            "../../sdk/csharp/ReportForge/runtimes/" + rid + "/native/" + fileName,
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
        try (InputStream in = ReportForgeEngine.class.getResourceAsStream(resourcePath)) {
            if (in != null) {
                Path tempDir = Files.createTempDirectory("reportforge_native_");
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
        Pointer ptr = getLib().reportforge_version();
        return ptr != null ? ptr.getString(0, "UTF-8") : "ReportForge Rust Core v2.0";
    }

    public static byte[] renderPdf(String documentJson, String dataJson) {
        ReportForgeNativeLib lib = getLib();
        byte[] docBytes = (documentJson + "\0").getBytes(StandardCharsets.UTF_8);
        byte[] dataBytes = dataJson != null ? (dataJson + "\0").getBytes(StandardCharsets.UTF_8) : null;
        ReportForgeResult.ByValue result = lib.reportforge_render_pdf(docBytes, dataBytes);

        try {
            if (result.success == 0) {
                String err = result.errorMessage != null ? result.errorMessage.getString(0, "UTF-8") : "Unknown native error";
                throw new RuntimeException("ReportForge Native Error: " + err);
            }

            int len = (int) result.length;
            if (len > 0 && result.data != null) {
                return result.data.getByteArray(0, len);
            }
            return new byte[0];
        } finally {
            lib.reportforge_free_result(result);
        }
    }

    public static byte[] renderPdf(String documentJson) {
        return renderPdf(documentJson, null);
    }
}
