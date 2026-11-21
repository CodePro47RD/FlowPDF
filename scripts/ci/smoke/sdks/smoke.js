// Prueba de humo del SDK de TypeScript/JavaScript (dist/ compilado): tabla agrupada con los métodos fluidos
// de 1.0 (groupBy, fontSize, padding, zebraColor, columnas auto/format), PDF real y extracción de texto.
'use strict';
const path = require('path');
const { ReportDocument } = require(path.resolve(__dirname, '../../../../sdk/typescript/dist'));

const rows = [
  { categoria: 'Servidores', sku: 'SRV-01', descripcion: 'Servidor 32GB RAM', monto: 3850 },
  { categoria: 'Servidores', sku: 'SRV-02', descripcion: 'Servidor 64GB RAM', monto: 5200 },
  { categoria: 'Redes', sku: 'SW-48P', descripcion: 'Switch 48 puertos PoE+', monto: 1450 },
];

const doc = ReportDocument.create(p => p.a4()).content(c => c
  .table(t => t
    .groupBy('categoria', '#E8F0FE', '#1F3B8A')
    .fontSize(8.5).padding(6, 4)
    .headerColor('#FFFFFF').textColor('#111827').zebraColor('#F8FAFC')
    .columns(cols => cols
      .column('sku', 'Código', { auto: true })
      .column('descripcion', 'Descripción', { flex: 1 })
      .column('monto', 'Monto', { auto: true, format: 'currency', align: 'right' }))
    .data(rows)));

const text = ReportDocument.extractText(doc.renderPdf());
for (const k of ['Servidores', 'Redes', 'SRV-01', '$3850.00']) {
  if (!text.includes(k)) throw new Error(`Falta "${k}" en el PDF:\n${text}`);
}
console.log('SDK TypeScript: SMOKE TEST PASSED');
