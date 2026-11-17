/**
 * ReportForge WebAssembly SDK
 * Motor de Generación y Extracción de PDFs en WebAssembly (Wasm)
 * Funciona 100% offline y tanto en servidor HTTP como directamente en file://
 * Copyright (c) 2026 Edwin Abreu & ReportForge Contributors
 */

class ReportForgeWasm {
  constructor() {
    this.instance = null;
    this.exports = null;
    this.isReady = false;
    this.initPromise = null;
  }

  /**
   * Inicializa el módulo WebAssembly.
   * Soporta:
   * 1. Carga instantánea vía base64 embebido (window.REPORTFORGE_WASM_BASE64) para file:// sin CORS.
   * 2. Carga vía fetch() para entornos HTTP/HTTPS.
   * 3. Pasaje directo de ArrayBuffer o Uint8Array.
   */
  async init(wasmSource = 'reportforge.wasm') {
    if (this.isReady) return true;
    if (this.initPromise) return this.initPromise;

    this.initPromise = (async () => {
      let wasmBytes = null;

      // 1. Si se pasó directamente un ArrayBuffer o Uint8Array
      if (wasmSource instanceof ArrayBuffer) {
        wasmBytes = wasmSource;
      } else if (wasmSource && wasmSource.buffer instanceof ArrayBuffer) {
        wasmBytes = wasmSource.buffer;
      }

      // 2. Si está disponible el binario base64 embebido en ventana (funciona en file:// sin web server)
      if (!wasmBytes && typeof window !== 'undefined' && window.REPORTFORGE_WASM_BASE64) {
        try {
          const binaryString = atob(window.REPORTFORGE_WASM_BASE64);
          const len = binaryString.length;
          const bytes = new Uint8Array(len);
          for (let i = 0; i < len; i++) {
            bytes[i] = binaryString.charCodeAt(i);
          }
          wasmBytes = bytes.buffer;
          console.log("⚡ ReportForge Wasm cargado desde binario embebido (Zero-CORS offline).");
        } catch (e) {
          console.warn("Fallo decodificando base64 embebido:", e);
        }
      }

      // 3. Si aún no tenemos bytes y hay fetch disponible (HTTP / HTTPS)
      if (!wasmBytes && typeof fetch !== 'undefined') {
        const candidates = [
          wasmSource,
          'reportforge.wasm',
          './reportforge.wasm',
          'docs/reportforge.wasm',
          'assets/reportforge.wasm'
        ];

        for (const url of candidates) {
          try {
            const resp = await fetch(url);
            if (resp.ok) {
              const buf = await resp.arrayBuffer();
              const head = new Uint8Array(buf.slice(0, 4));
              if (head[0] === 0x00 && head[1] === 0x61 && head[2] === 0x73 && head[3] === 0x6d) {
                wasmBytes = buf;
                console.log(`⚡ ReportForge Wasm cargado exitosamente desde '${url}'.`);
                break;
              }
            }
          } catch (_) {
            // Ignorar y probar el siguiente candidato
          }
        }
      }

      if (!wasmBytes) {
        throw new Error(
          "No se pudo cargar el archivo 'reportforge.wasm'. " +
          "Asegúrate de incluir 'reportforge-wasm-data.js' o ejecutar bajo un servidor HTTP local."
        );
      }

      const { instance } = await WebAssembly.instantiate(wasmBytes, {});
      this.instance = instance;
      this.exports = instance.exports;
      this.isReady = true;
      console.log("🚀 ReportForge WebAssembly Core inicializado exitosamente.");
      return true;
    })();

    return this.initPromise;
  }

  /**
   * Renderiza una definición JSON de documento directamente a bytes PDF en Wasm
   * @param {object|string} documentJson
   * @returns {Uint8Array} bytes del PDF generado
   */
  renderPdf(documentJson) {
    if (!this.isReady) {
      throw new Error("ReportForge Wasm no está inicializado. Llama a init() primero.");
    }

    const jsonStr = typeof documentJson === 'string' ? documentJson : JSON.stringify(documentJson);
    const encoder = new TextEncoder();
    const encoded = encoder.encode(jsonStr);

    const ptr = this.exports.reportforge_wasm_alloc(encoded.length);
    new Uint8Array(this.exports.memory.buffer).set(encoded, ptr);

    const result64 = this.exports.reportforge_wasm_render(ptr, encoded.length);
    this.exports.reportforge_wasm_dealloc(ptr, encoded.length);

    if (result64 === 0n || result64 === 0) {
      throw new Error("Error en la compilación del documento en ReportForge Wasm (AST inválido o error interno).");
    }

    const outPtr = Number(result64 >> 32n);
    const outLen = Number(result64 & 0xFFFFFFFFn);

    // Obtener los bytes usando el buffer actual de la memoria Wasm
    const pdfBytes = new Uint8Array(this.exports.memory.buffer.slice(outPtr, outPtr + outLen));
    this.exports.reportforge_wasm_dealloc(outPtr, outLen);

    return pdfBytes;
  }

  /**
   * Extrae texto plano de un PDF en Wasm
   * @param {Uint8Array} pdfBytes
   * @returns {string} texto extraído
   */
  extractText(pdfBytes) {
    if (!this.isReady) {
      throw new Error("ReportForge Wasm no está inicializado.");
    }

    const ptr = this.exports.reportforge_wasm_alloc(pdfBytes.length);
    new Uint8Array(this.exports.memory.buffer).set(pdfBytes, ptr);

    const result64 = this.exports.reportforge_wasm_extract_text(ptr, pdfBytes.length);
    this.exports.reportforge_wasm_dealloc(ptr, pdfBytes.length);

    if (result64 === 0n || result64 === 0) {
      throw new Error("Error extrayendo texto del PDF en Wasm.");
    }

    const outPtr = Number(result64 >> 32n);
    const outLen = Number(result64 & 0xFFFFFFFFn);

    const textBytes = new Uint8Array(this.exports.memory.buffer.slice(outPtr, outPtr + outLen));
    this.exports.reportforge_wasm_dealloc(outPtr, outLen);

    return new TextDecoder().decode(textBytes);
  }

  /**
   * Registra una fuente TrueType global en memoria Wasm
   * @param {string} fontName
   * @param {Uint8Array} ttfBytes
   */
  registerFont(fontName, ttfBytes) {
    if (!this.isReady) {
      throw new Error("ReportForge Wasm no está inicializado.");
    }

    const enc = new TextEncoder();
    const nameBytes = enc.encode(fontName);

    const namePtr = this.exports.reportforge_wasm_alloc(nameBytes.length);
    new Uint8Array(this.exports.memory.buffer).set(nameBytes, namePtr);

    const fontPtr = this.exports.reportforge_wasm_alloc(ttfBytes.length);
    new Uint8Array(this.exports.memory.buffer).set(ttfBytes, fontPtr);

    const code = this.exports.reportforge_wasm_register_font(namePtr, nameBytes.length, fontPtr, ttfBytes.length);
    this.exports.reportforge_wasm_dealloc(namePtr, nameBytes.length);
    this.exports.reportforge_wasm_dealloc(fontPtr, ttfBytes.length);

    if (code !== 0) {
      throw new Error(`Error registrando fuente TTF '${fontName}' en Wasm (código: ${code}).`);
    }
    return true;
  }
}

// Instancia global en navegador
if (typeof window !== 'undefined') {
  window.ReportForgeWasm = ReportForgeWasm;
  window.reportforgeWasm = new ReportForgeWasm();
}

// Soporte para Node.js / CommonJS
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { ReportForgeWasm };
}
