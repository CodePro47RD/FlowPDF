<?php

namespace FlowPdf;

class FlowPdfEngine
{
    private static ?\FFI $ffi = null;

    public static function getLibraryPath(): string
    {
        $isWindows = strtoupper(substr(PHP_OS, 0, 3)) === 'WIN';
        $isMac = PHP_OS === 'Darwin';
        $rid = $isWindows ? 'win-x64' : ($isMac ? 'osx-x64' : 'linux-x64');
        $filename = $isWindows ? 'flowpdf_native.dll' : ($isMac ? 'libflowpdf_native.dylib' : 'libflowpdf_native.so');

        $candidates = [
            __DIR__ . "/../runtimes/{$rid}/native/{$filename}",
            __DIR__ . "/../../runtimes/{$rid}/native/{$filename}",
            getcwd() . "/runtimes/{$rid}/native/{$filename}",
            getcwd() . "/vendor/codepro47rd/flowpdf/runtimes/{$rid}/native/{$filename}",
            $filename
        ];

        foreach ($candidates as $cand) {
            if (file_exists($cand)) {
                return realpath($cand);
            }
        }
        return $filename;
    }

    public static function isFfiAvailable(): bool
    {
        return extension_loaded('ffi') && (ini_get('ffi.enable') === '1' || ini_get('ffi.enable') === 'true' || ini_get('ffi.enable') === 'preload' || PHP_SAPI === 'cli');
    }

    public static function getFFI(): \FFI
    {
        if (self::$ffi === null) {
            if (!extension_loaded('ffi')) {
                throw new \RuntimeException(
                    "PHP FFI extension is not loaded. Enable 'extension=ffi' in php.ini to use FlowPDF in-process native rendering."
                );
            }

            $cdef = '
                typedef struct {
                    uint8_t *data;
                    size_t length;
                    bool success;
                    char *error_message;
                } FlowPdfResult;

                FlowPdfResult flowpdf_render_pdf(const char *doc_json, const char *data_json);
                FlowPdfResult flowpdf_render_xlsx(const char *doc_json, const char *data_json);
                FlowPdfResult flowpdf_render_docx(const char *doc_json, const char *data_json);
                FlowPdfResult flowpdf_render_document(const char *doc_json, const char *data_json, const char *format);
                FlowPdfResult flowpdf_extract_text(const uint8_t *pdf_data, size_t pdf_len);
                FlowPdfResult flowpdf_extract_json(const uint8_t *pdf_data, size_t pdf_len, const char *options_json);
                int flowpdf_register_font(const char *font_name, const uint8_t *font_bytes, size_t font_len);
                void flowpdf_free_result(FlowPdfResult result);
                const char *flowpdf_version(void);
            ';

            $libPath = self::getLibraryPath();
            try {
                self::$ffi = \FFI::cdef($cdef, $libPath);
            } catch (\Throwable $e) {
                throw new \RuntimeException("Failed to load FlowPDF native library at '{$libPath}': " . $e->getMessage(), 0, $e);
            }
        }
        return self::$ffi;
    }

    public static function getVersion(): string
    {
        return self::getFFI()->flowpdf_version();
    }

    public static function renderPdf(mixed $document, mixed $data = null): string
    {
        if (is_object($document) && method_exists($document, 'build')) {
            $document = $document->build();
        }

        $docJson = is_string($document) ? $document : json_encode($document, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        $dataJson = $data !== null ? (is_string($data) ? $data : json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)) : null;

        $ffi = self::getFFI();
        $result = $ffi->flowpdf_render_pdf($docJson, $dataJson);

        try {
            if (!$result->success) {
                $err = $result->error_message ? \FFI::string($result->error_message) : 'Unknown native render error';
                throw new \RuntimeException("FlowPDF Native Error: {$err}");
            }

            if ($result->length > 0 && $result->data !== null) {
                return \FFI::string($result->data, $result->length);
            }
            return '';
        } finally {
            $ffi->flowpdf_free_result($result);
        }
    }

    public static function renderXlsx(mixed $document, mixed $data = null): string
    {
        if (is_object($document) && method_exists($document, 'build')) {
            $document = $document->build();
        }

        $docJson = is_string($document) ? $document : json_encode($document, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        $dataJson = $data !== null ? (is_string($data) ? $data : json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)) : null;

        $ffi = self::getFFI();
        $result = $ffi->flowpdf_render_xlsx($docJson, $dataJson);

        try {
            if (!$result->success) {
                $err = $result->error_message ? \FFI::string($result->error_message) : 'Unknown native render error';
                throw new \RuntimeException("FlowPDF Native Error: {$err}");
            }

            if ($result->length > 0 && $result->data !== null) {
                return \FFI::string($result->data, $result->length);
            }
            return '';
        } finally {
            $ffi->flowpdf_free_result($result);
        }
    }

    public static function renderDocx(mixed $document, mixed $data = null): string
    {
        if (is_object($document) && method_exists($document, 'build')) {
            $document = $document->build();
        }

        $docJson = is_string($document) ? $document : json_encode($document, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        $dataJson = $data !== null ? (is_string($data) ? $data : json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)) : null;

        $ffi = self::getFFI();
        $result = $ffi->flowpdf_render_docx($docJson, $dataJson);

        try {
            if (!$result->success) {
                $err = $result->error_message ? \FFI::string($result->error_message) : 'Unknown native render error';
                throw new \RuntimeException("FlowPDF Native Error: {$err}");
            }

            if ($result->length > 0 && $result->data !== null) {
                return \FFI::string($result->data, $result->length);
            }
            return '';
        } finally {
            $ffi->flowpdf_free_result($result);
        }
    }

    public static function render(mixed $document, mixed $data = null, string $format = 'pdf'): string
    {
        if (is_object($document) && method_exists($document, 'build')) {
            $document = $document->build();
        }

        $docJson = is_string($document) ? $document : json_encode($document, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        $dataJson = $data !== null ? (is_string($data) ? $data : json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)) : null;

        $ffi = self::getFFI();
        $result = $ffi->flowpdf_render_document($docJson, $dataJson, $format);

        try {
            if (!$result->success) {
                $err = $result->error_message ? \FFI::string($result->error_message) : 'Unknown native render error';
                throw new \RuntimeException("FlowPDF Native Error: {$err}");
            }

            if ($result->length > 0 && $result->data !== null) {
                return \FFI::string($result->data, $result->length);
            }
            return '';
        } finally {
            $ffi->flowpdf_free_result($result);
        }
    }

    public static function extractText(string $pdfBytes): string
    {
        $len = strlen($pdfBytes);
        if ($len === 0) return '';
        $ffi = self::getFFI();
        $buf = $ffi->new("uint8_t[$len]");
        \FFI::memcpy($buf, $pdfBytes, $len);
        $result = $ffi->flowpdf_extract_text(\FFI::cast("uint8_t*", $buf), $len);
        try {
            if (!$result->success) {
                $err = $result->error_message ? \FFI::string($result->error_message) : 'Unknown native extraction error';
                throw new \RuntimeException("FlowPDF Extraction Error: {$err}");
            }
            if ($result->length > 0 && $result->data !== null) {
                return \FFI::string($result->data, $result->length);
            }
            return '';
        } finally {
            $ffi->flowpdf_free_result($result);
        }
    }

    public static function extractDocument(string $pdfBytes, ?array $options = null): array
    {
        $len = strlen($pdfBytes);
        if ($len === 0) return [];
        $ffi = self::getFFI();
        $buf = $ffi->new("uint8_t[$len]");
        \FFI::memcpy($buf, $pdfBytes, $len);
        $optJson = $options !== null ? json_encode($options) : null;
        $result = $ffi->flowpdf_extract_json(\FFI::cast("uint8_t*", $buf), $len, $optJson);
        try {
            if (!$result->success) {
                $err = $result->error_message ? \FFI::string($result->error_message) : 'Unknown native extraction error';
                throw new \RuntimeException("FlowPDF Extraction Error: {$err}");
            }
            if ($result->length > 0 && $result->data !== null) {
                $json = \FFI::string($result->data, $result->length);
                return json_decode($json, true) ?: [];
            }
            return [];
        } finally {
            $ffi->flowpdf_free_result($result);
        }
    }

    public static function registerFont(string $fontName, string $fontBytes): bool
    {
        $len = strlen($fontBytes);
        if ($len === 0 || empty($fontName)) return false;
        $ffi = self::getFFI();
        $buf = $ffi->new("uint8_t[$len]");
        \FFI::memcpy($buf, $fontBytes, $len);
        $res = $ffi->flowpdf_register_font($fontName, \FFI::cast("uint8_t*", $buf), $len);
        return $res === 0;
    }
}
