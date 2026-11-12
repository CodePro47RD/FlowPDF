<?php

declare(strict_types=1);

namespace ReportForge\Native;

/**
 * ReportForge v2.0 PHP Native FFI Binding.
 * Calls into the Rust Core directly in-process via PHP's Foreign Function Interface (\FFI).
 */
class ReportForgeEngine
{
    private static ?\FFI $ffi = null;

    private static function getFfi(): \FFI
    {
        if (self::$ffi !== null) {
            return self::$ffi;
        }

        $header = "
            typedef struct {
                uint8_t* data;
                size_t length;
                bool success;
                char* error_message;
            } ReportForgeResult;

            ReportForgeResult reportforge_render_pdf(const char* doc_json, const char* data_json);
            void reportforge_free_result(ReportForgeResult result);
            const char* reportforge_version(void);
        ";

        $candidates = [
            'reportforge.dll',
            'libreportforge.so',
            'libreportforge.dylib',
            __DIR__ . '/../../engine-rust/target/release/reportforge.dll',
            __DIR__ . '/../../engine-rust/target/release/libreportforge.so',
        ];

        $libPath = 'reportforge';
        foreach ($candidates as $candidate) {
            if (file_exists($candidate)) {
                $libPath = realpath($candidate);
                break;
            }
        }

        self::$ffi = \FFI::cdef($header, $libPath);
        return self::$ffi;
    }

    public static function version(): string
    {
        return \FFI::string(self::getFfi()->reportforge_version());
    }

    public static function renderPdf(array|string $document, array|string|null $data = null): string
    {
        $ffi = self::getFfi();

        $docJson = is_array($document) ? json_encode($document, JSON_UNESCAPED_UNICODE) : $document;
        $dataJson = is_array($data) ? json_encode($data, JSON_UNESCAPED_UNICODE) : $data;

        $result = $ffi->reportforge_render_pdf($docJson, $dataJson);

        try {
            if (!$result->success) {
                $errorMsg = $result->error_message !== null ? \FFI::string($result->error_message) : 'Unknown native error';
                throw new \RuntimeException("ReportForge Native Error: " . $errorMsg);
            }

            if ($result->length === 0 || $result->data === null) {
                return '';
            }

            return \FFI::string($result->data, $result->length);
        } finally {
            $ffi->reportforge_free_result($result);
        }
    }
}
