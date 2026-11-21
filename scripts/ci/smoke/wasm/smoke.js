// Prueba de humo del WASM del sitio (docs/): usa el mismo loader que el navegador, carga el
// binario desde la copia base64 embebida, genera un PDF y le extrae el texto.
//   node scripts/ci/smoke/wasm/smoke.js
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const docs = path.resolve(__dirname, '../../../../docs');
const MARKER = 'FlowPDF WASM smoke OK';

(async () => {
  // 1. La copia base64 (file://) debe ser idéntica a docs/flowpdf.wasm (HTTP)
  global.window = {};
  vm.runInThisContext(fs.readFileSync(path.join(docs, 'flowpdf-wasm-data.js'), 'utf8').replace(/^﻿/, ''));
  const embedded = Buffer.from(window.FLOWPDF_WASM_BASE64, 'base64');
  const file = fs.readFileSync(path.join(docs, 'flowpdf.wasm'));
  if (!embedded.equals(file)) throw new Error('flowpdf-wasm-data.js no coincide con flowpdf.wasm (ejecuta scripts/dev/build-wasm.sh)');
  console.log(`WASM: ${file.length.toLocaleString('es')} bytes; copia base64 idéntica`);

  // 2. El loader real del sitio
  const { FlowPdfWasm } = require(path.join(docs, 'flowpdf-wasm.js'));
  const wasm = new FlowPdfWasm();
  await wasm.init();

  const doc = {
    page: { size: 'A4', orientation: 'portrait', margin: 20 },
    content: [
      { type: 'text', value: MARKER, style: 'h2' },
      { type: 'text', value: 'Acentos: áéíóú ñ Ñ', style: 'body' },
    ],
  };
  const pdf = wasm.renderPdf(doc);
  if (pdf.length < 500 || Buffer.from(pdf.slice(0, 5)).toString() !== '%PDF-') throw new Error(`PDF inválido (${pdf.length} bytes)`);
  console.log(`PDF generado: ${pdf.length.toLocaleString('es')} bytes`);

  const text = wasm.extractText(pdf);
  if (!text.includes(MARKER)) throw new Error(`El texto extraído no contiene el marcador:\n${text}`);
  console.log('Extracción de texto: OK');
  console.log('WASM SMOKE TEST PASSED');
})().catch(e => { console.error(e); process.exit(1); });
