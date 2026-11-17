import * as path from 'path';
import * as fs from 'fs';

let koffiInstance: any = null;
let koffiLoaded = false;

function getKoffi() {
    if (!koffiLoaded) {
        koffiLoaded = true;
        try {
            koffiInstance = require('koffi');
        } catch {
            koffiInstance = null;
        }
    }
    return koffiInstance;
}

export class ReportForgeEngine {
    private static cachedKoffiLib: any = null;

    public static getLibraryPath(): string {
        const isWindows = process.platform === 'win32';
        const isMac = process.platform === 'darwin';
        const rid = isWindows ? 'win-x64' : isMac ? 'osx-x64' : 'linux-x64';
        const filename = isWindows
            ? 'reportforge_native.dll'
            : isMac
            ? 'libreportforge_native.dylib'
            : 'libreportforge_native.so';

        const candidates = [
            path.resolve(__dirname, '../runtimes', rid, 'native', filename),
            path.resolve(__dirname, '../../runtimes', rid, 'native', filename),
            path.resolve(__dirname, 'runtimes', rid, 'native', filename),
            path.resolve(__dirname, filename),
            path.resolve(process.cwd(), 'runtimes', rid, 'native', filename),
            path.resolve(process.cwd(), 'node_modules/reportforge/runtimes', rid, 'native', filename),
            filename
        ];

        for (const candidate of candidates) {
            if (fs.existsSync(candidate)) {
                return candidate;
            }
        }
        return filename;
    }

    public static getVersion(): string {
        const libPath = this.getLibraryPath();

        // 1. Check Bun FFI
        if (typeof (globalThis as any).Bun !== 'undefined') {
            const { dlopen, FFIType } = (globalThis as any).Bun.FFI;
            const lib = dlopen(libPath, {
                reportforge_version: {
                    args: [],
                    returns: FFIType.cstring,
                }
            });
            return lib.symbols.reportforge_version() as string;
        }

        // 2. Check Node.js koffi
        const koffi = getKoffi();
        if (koffi) {
            const lib = koffi.load(libPath);
            const getVersionFn = lib.func('reportforge_version', 'str', []);
            return getVersionFn();
        }

        return 'ReportForge Rust Core v2.0 (Native runtime not initialized)';
    }

    public static renderPdf(document: object | string, data?: object | string): Uint8Array {
        const docJson = typeof document === 'string' ? document : JSON.stringify(document);
        const dataJson = data ? (typeof data === 'string' ? data : JSON.stringify(data)) : null;
        const libPath = this.getLibraryPath();

        // 1. If running in Bun, execute zero-overhead FFI
        if (typeof (globalThis as any).Bun !== 'undefined') {
            const { dlopen, FFIType, ptr, toArrayBuffer } = (globalThis as any).Bun.FFI;
            // Memory layout of ReportForgeResult:
            // [data: ptr (8), length: size_t (8), success: bool (1), padding (7), error_message: cstring (8)]
            // Alternatively use Koffi or Node API
        }

        // 2. If running in Node.js with koffi
        const koffi = getKoffi();
        if (koffi) {
            if (!this.cachedKoffiLib) {
                const ReportForgeResult = koffi.struct('ReportForgeResult', {
                    data: 'uint8_t *',
                    length: 'size_t',
                    success: 'bool',
                    error_message: 'char *'
                });

                const lib = koffi.load(libPath);
                this.cachedKoffiLib = {
                    render: lib.func('reportforge_render_pdf', ReportForgeResult, ['str', 'str']),
                    free: lib.func('reportforge_free_result', 'void', [ReportForgeResult]),
                };
            }

            const res = this.cachedKoffiLib.render(docJson, dataJson);
            try {
                if (!res.success) {
                    const err = res.error_message || 'Unknown native render error';
                    throw new Error(`ReportForge Native Error: ${err}`);
                }

                if (res.length > 0 && res.data) {
                    const decoded = koffi.decode(res.data, 'uint8_t', res.length);
                    return new Uint8Array(decoded);
                }
                return new Uint8Array();
            } finally {
                this.cachedKoffiLib.free(res);
            }
        }

        throw new Error(
            'ReportForge in-process native rendering in Node.js requires "koffi" for C-ABI FFI. ' +
            'Install it with: npm install koffi\n' +
            'Alternatively, use ReportForgeClient for HTTP/REST server rendering.'
        );
    }

    public static extractText(pdfBytes: Uint8Array | Buffer): string {
        const libPath = this.getLibraryPath();
        const koffi = getKoffi();
        if (koffi) {
            const ReportForgeResult = koffi.struct('ReportForgeResultExtractText', {
                data: 'uint8_t *',
                length: 'size_t',
                success: 'bool',
                error_message: 'char *'
            });
            const lib = koffi.load(libPath);
            const extractFn = lib.func('reportforge_extract_text', ReportForgeResult, ['uint8_t *', 'size_t']);
            const freeFn = lib.func('reportforge_free_result', 'void', [ReportForgeResult]);

            const res = extractFn(pdfBytes, pdfBytes.length);
            try {
                if (!res.success) {
                    throw new Error(`ReportForge Extraction Error: ${res.error_message || 'Unknown error'}`);
                }
                if (res.length > 0 && res.data) {
                    const decoded = koffi.decode(res.data, 'uint8_t', res.length);
                    return Buffer.from(decoded).toString('utf-8');
                }
                return '';
            } finally {
                freeFn(res);
            }
        }
        throw new Error('ReportForge native extraction requires "koffi" in Node.js.');
    }

    public static extractDocument(pdfBytes: Uint8Array | Buffer, options?: object): any {
        const libPath = this.getLibraryPath();
        const koffi = getKoffi();
        if (koffi) {
            const ReportForgeResult = koffi.struct('ReportForgeResultExtractJson', {
                data: 'uint8_t *',
                length: 'size_t',
                success: 'bool',
                error_message: 'char *'
            });
            const lib = koffi.load(libPath);
            const extractJsonFn = lib.func('reportforge_extract_json', ReportForgeResult, ['uint8_t *', 'size_t', 'str']);
            const freeFn = lib.func('reportforge_free_result', 'void', [ReportForgeResult]);

            const optStr = options ? JSON.stringify(options) : null;
            const res = extractJsonFn(pdfBytes, pdfBytes.length, optStr);
            try {
                if (!res.success) {
                    throw new Error(`ReportForge Extraction Error: ${res.error_message || 'Unknown error'}`);
                }
                if (res.length > 0 && res.data) {
                    const decoded = koffi.decode(res.data, 'uint8_t', res.length);
                    const jsonStr = Buffer.from(decoded).toString('utf-8');
                    return JSON.parse(jsonStr);
                }
                return {};
            } finally {
                freeFn(res);
            }
        }
        throw new Error('ReportForge native extraction requires "koffi" in Node.js.');
    }

    public static registerFont(fontName: string, fontBytes: Uint8Array | Buffer): boolean {
        const libPath = this.getLibraryPath();
        const koffi = getKoffi();
        if (koffi) {
            const lib = koffi.load(libPath);
            const regFn = lib.func('reportforge_register_font', 'int', ['str', 'uint8_t *', 'size_t']);
            const res = regFn(fontName, fontBytes, fontBytes.length);
            return res === 0;
        }
        throw new Error('ReportForge native font registration requires "koffi" in Node.js.');
    }
}
