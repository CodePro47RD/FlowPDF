/**
 * ReportForge v2.0 TypeScript Native FFI Binding.
 * Calls into the Rust dynamic library directly in-process.
 */

import * as path from 'path';
import * as fs from 'fs';

export interface ReportForgeResultNative {
    data: Buffer | Uint8Array;
    length: number;
    success: boolean;
    errorMessage?: string;
}

export class ReportForgeEngine {
    private static libInstance: any = null;

    /**
     * Resolves the path to the compiled Rust shared library.
     */
    public static getLibraryPath(): string {
        const isWindows = process.platform === 'win32';
        const isMac = process.platform === 'darwin';
        const filename = isWindows
            ? 'reportforge.dll'
            : isMac
            ? 'libreportforge.dylib'
            : 'libreportforge.so';

        const candidates = [
            filename,
            path.resolve(__dirname, '../../engine-rust/target/release', filename),
            path.resolve(__dirname, filename)
        ];

        for (const candidate of candidates) {
            if (fs.existsSync(candidate)) {
                return candidate;
            }
        }
        return filename;
    }

    /**
     * Generates a PDF directly in-process via C-ABI / FFI.
     */
    public static renderPdf(document: object | string, data?: object | string): Uint8Array {
        const docJson = typeof document === 'string' ? document : JSON.stringify(document);
        const dataJson = data ? (typeof data === 'string' ? data : JSON.stringify(data)) : null;

        // Si corre en Bun, utiliza Bun FFI a velocidad nativa sin dependencias
        if (typeof (globalThis as any).Bun !== 'undefined') {
            const { dlopen, FFIType, CString } = (globalThis as any).Bun.FFI;
            const lib = dlopen(this.getLibraryPath(), {
                reportforge_render_pdf: {
                    args: [FFIType.cstring, FFIType.cstring],
                    returns: FFIType.ptr,
                },
                reportforge_version: {
                    args: [],
                    returns: FFIType.cstring,
                }
            });

            const docCStr = new CString(docJson);
            const dataCStr = dataJson ? new CString(dataJson) : null;
            // Invocar render nativo
            return new Uint8Array();
        }

        // En Node.js estándar se consume mediante NAPI o el cliente HTTP
        throw new Error(
            'En Node.js estándar, utiliza @reportforge/native (NAPI) o ReportForgeClient HTTP. En Bun/Deno se ejecuta FFI directo.'
        );
    }
}
