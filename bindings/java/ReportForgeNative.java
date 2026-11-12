package com.reportforge.native_engine;

import java.io.File;
import java.nio.charset.StandardCharsets;

/**
 * ReportForge v2.0 Java Native Binding.
 * Interoperates with the Rust dynamic library via JNA (Java Native Access) or JNI.
 */
public class ReportForgeEngine {

    public interface ReportForgeLib extends com.sun.jna.Library {
        ReportForgeLib INSTANCE = com.sun.jna.Native.load(findLibrary(), ReportForgeLib.class);

        class Result extends com.sun.jna.Structure {
            public static class ByValue extends Result implements com.sun.jna.Structure.ByValue {}

            public com.sun.jna.Pointer data;
            public com.sun.jna.NativeLong length;
            public boolean success;
            public String errorMessage;

            @Override
            protected java.util.List<String> getFieldOrder() {
                return java.util.Arrays.asList("data", "length", "success", "errorMessage");
            }
        }

        Result.ByValue reportforge_render_pdf(String docJson, String dataJson);
        void reportforge_free_result(Result.ByValue result);
        String reportforge_version();
    }

    private static String findLibrary() {
        String[] candidates = {
            "reportforge",
            "libreportforge",
            "../../engine-rust/target/release/reportforge.dll",
            "../../engine-rust/target/release/libreportforge.so"
        };
        for (String c : candidates) {
            if (new File(c).exists()) {
                return new File(c).getAbsolutePath();
            }
        }
        return "reportforge";
    }

    public static String getVersion() {
        return ReportForgeLib.INSTANCE.reportforge_version();
    }

    public static byte[] renderPdf(String documentJson, String dataJson) {
        ReportForgeLib.Result.ByValue result = ReportForgeLib.INSTANCE.reportforge_render_pdf(documentJson, dataJson);
        try {
            if (!result.success) {
                String err = result.errorMessage != null ? result.errorMessage : "Unknown native error";
                throw new RuntimeException("ReportForge Native Error: " + err);
            }

            int len = result.length.intValue();
            if (len <= 0 || result.data == null) {
                return new byte[0];
            }

            return result.data.getByteArray(0, len);
        } finally {
            ReportForgeLib.INSTANCE.reportforge_free_result(result);
        }
    }
}
