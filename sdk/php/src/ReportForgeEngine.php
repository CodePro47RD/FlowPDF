<?php

namespace ReportForge;

class ReportForgeEngine
{
    private static ?\FFI $ffi = null;

    public static function getLibraryPath(): string
    {
        $isWindows = strtoupper(substr(PHP_OS, 0, 3)) === 'WIN';
        $isMac = PHP_OS === 'Darwin';
        $rid = $isWindows ? 'win-x64' : ($isMac ? 'osx-x64' : 'linux-x64');
        $filename = $isWindows ? 'reportforge_native.dll' : ($isMac ? 'libreportforge_native.dylib' : 'libreportforge_native.so');

        $candidates = [
            __DIR__ . "/../runtimes/{$rid}/native/{$filename}",
            __DIR__ . "/../../runtimes/{$rid}/native/{$filename}",
            getcwd() . "/runtimes/{$rid}/native/{$filename}",
            getcwd() . "/vendor/reportforge/reportforge/runtimes/{$rid}/native/{$filename}",
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
                    "PHP FFI extension is not loaded. Enable 'extension=ffi' in php.ini to use ReportForge in-process native rendering."
                );
            }

            $cdef = '
                typedef struct {
                    uint8_t *data;
                    size_t length;
                    bool success;
                    char *error_message;
                } ReportForgeResult;

                ReportForgeResult reportforge_render_pdf(const char *doc_json, const char *data_json);
                void reportforge_free_result(ReportForgeResult result);
                const char *reportforge_version(void);
            ';

            $libPath = self::getLibraryPath();
            try {
                self::$ffi = \FFI::cdef($cdef, $libPath);
            } catch (\Throwable $e) {
                throw new \RuntimeException("Failed to load ReportForge native library at '{$libPath}': " . $e->getMessage(), 0, $e);
            }
        }
        return self::$ffi;
    }

    public static function getVersion(): string
    {
        return self::getFFI()->reportforge_version();
    }

    public static function renderPdf(mixed $document, mixed $data = null): string
    {
        if (is_object($document) && method_exists($document, 'build')) {
            $document = $document->build();
        }

        $docJson = is_string($document) ? $document : json_encode($document, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        $dataJson = $data !== null ? (is_string($data) ? $data : json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)) : null;

        $ffi = self::getFFI();
        $result = $ffi->reportforge_render_pdf($docJson, $dataJson);

        try {
            if (!$result->success) {
                $err = $result->error_message ? \FFI::string($result->error_message) : 'Unknown native render error';
                throw new \RuntimeException("ReportForge Native Error: {$err}");
            }

            if ($result->length > 0 && $result->data !== null) {
                return \FFI::string($result->data, $result->length);
            }
            return '';
        } finally {
            $ffi->reportforge_free_result($result);
        }
    }
}
