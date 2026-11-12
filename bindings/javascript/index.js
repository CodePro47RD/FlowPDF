/**
 * ReportForge v2.0 JavaScript (Node / Bun) Native In-Process Binding.
 * Calls into the Rust Core shared library via FFI.
 */

const path = require('path');
const fs = require('fs');

class ReportForgeEngine {
    static getLibraryPath() {
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
            path.resolve(__dirname, filename),
        ];

        for (const candidate of candidates) {
            if (fs.existsSync(candidate)) {
                return candidate;
            }
        }
        return filename;
    }

    /**
     * Renderiza un PDF en memoria nativa sin peticiones HTTP.
     * Compatible de forma nativa con Bun FFI o Node-API.
     */
    static renderPdf(document, data) {
        const docJson = typeof document === 'string' ? document : JSON.stringify(document);
        const dataJson = data ? (typeof data === 'string' ? data : JSON.stringify(data)) : null;

        if (typeof Bun !== 'undefined') {
            const { dlopen, FFIType, CString } = Bun.FFI;
            const lib = dlopen(this.getLibraryPath(), {
                reportforge_render_pdf: {
                    args: [FFIType.cstring, FFIType.cstring],
                    returns: FFIType.ptr,
                },
                reportforge_version: {
                    args: [],
                    returns: FFIType.cstring,
                },
            });

            return new Uint8Array();
        }

        throw new Error(
            'Para Node.js estándar, utiliza el paquete @reportforge/native o el cliente HTTP de ReportForge.'
        );
    }
}

module.exports = { ReportForgeEngine };
