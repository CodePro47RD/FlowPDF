/**
 * ReportForge WebAssembly SDK
 * Motor de Generación y Extracción de PDFs en WebAssembly (Wasm)
 * Copyright (c) 2026 Edwin Abreu & ReportForge Contributors
 */

class ReportForgeWasm {
  constructor() {
    this.instance = null;
    this.exports = null;
    this.memory = null;
    this.isReady = false;
  }

  async init(wasmUrl = 'reportforge.wasm') {
    if (this.isReady) return;

    let response;
    try {
      response = await fetch(wasmUrl);
    } catch (e) {
      // Fallback a ruta relativa de assets si es necesario
      response = await fetch('assets/reportforge.wasm');
    }

    const wasmBytes = await response.arrayBuffer();
    const { instance } = await WebAssembly.instantiate(wasmBytes, {});
    this.instance = instance;
    this.exports = instance.exports;
    this.memory = this.exports.memory;
    this.isReady = true;
    console.log("🚀 ReportForge WebAssembly Core inicializado exitosamente.");
  }

  /**
   * Renderiza una definición JSON de documento directamente a bytes PDF en Wasm
   * @param {object|string} documentJson
   * @returns {Uint8Array} bytes del PDF generado
   */
  renderPdf(documentJson) {
    if (!this.isReady) throw new Error("ReportForge Wasm no está inicializado. Llama a init() primero.");

    const jsonStr = typeof documentJson === 'string' ? documentJson : JSON.stringify(documentJson);
    const encoder = new TextEncoder();
    const encoded = encoder.encode(jsonStr);

    const ptr = this.exports.reportforge_wasm_alloc(encoded.length);
    new Uint8Array(this.memory.buffer).set(encoded, ptr);

    const result64 = this.exports.reportforge_wasm_render(ptr, encoded.length);
    this.exports.reportforge_wasm_dealloc(ptr, encoded.length);

    if (result64 === 0n || result64 === 0) {
      throw new Error("Error en la compilación del documento en ReportForge Wasm.");
    }

    const outPtr = Number(result64 >> 32n);
    const outLen = Number(result64 & 0xFFFFFFFFn);

    const pdfBytes = new Uint8Array(this.memory.buffer.slice(outPtr, outPtr + outLen));
    this.exports.reportforge_wasm_dealloc(outPtr, outLen);

    return pdfBytes;
  }

  /**
   * Extrae texto plano de un PDF en Wasm
   * @param {Uint8Array} pdfBytes
   * @returns {string} texto extraído
   */
  extractText(pdfBytes) {
    if (!this.isReady) throw new Error("ReportForge Wasm no está inicializado.");

    const ptr = this.exports.reportforge_wasm_alloc(pdfBytes.length);
    new Uint8Array(this.memory.buffer).set(pdfBytes, ptr);

    const result64 = this.exports.reportforge_wasm_extract_text(ptr, pdfBytes.length);
    this.exports.reportforge_wasm_dealloc(ptr, pdfBytes.length);

    if (result64 === 0n || result64 === 0) {
      throw new Error("Error extrayendo texto del PDF en Wasm.");
    }

    const outPtr = Number(result64 >> 32n);
    const outLen = Number(result64 & 0xFFFFFFFFn);

    const textBytes = new Uint8Array(this.memory.buffer.slice(outPtr, outPtr + outLen));
    this.exports.reportforge_wasm_dealloc(outPtr, outLen);

    return new TextDecoder().decode(textBytes);
  }

  /**
   * Registra una fuente TrueType global en memoria Wasm
   * @param {string} fontName
   * @param {Uint8Array} ttfBytes
   */
  registerFont(fontName, ttfBytes) {
    if (!this.isReady) throw new Error("ReportForge Wasm no está inicializado.");

    const enc = new TextEncoder();
    const nameBytes = enc.encode(fontName);

    const namePtr = this.exports.reportforge_wasm_alloc(nameBytes.length);
    new Uint8Array(this.memory.buffer).set(nameBytes, namePtr);

    const fontPtr = this.exports.reportforge_wasm_alloc(ttfBytes.length);
    new Uint8Array(this.memory.buffer).set(ttfBytes, fontPtr);

    const code = this.exports.reportforge_wasm_register_font(namePtr, nameBytes.length, fontPtr, ttfBytes.length);
    this.exports.reportforge_wasm_dealloc(namePtr, nameBytes.length);
    this.exports.reportforge_wasm_dealloc(fontPtr, ttfBytes.length);

    if (code !== 0) {
      throw new Error(`Error registrando fuente TTF '${fontName}' en Wasm (código: ${code}).`);
    }
  }
}

// Instancia global disponible en navegador
window.ReportForgeWasm = ReportForgeWasm;
window.reportforgeWasm = new ReportForgeWasm();
