<?php
// Prueba de humo del SDK de PHP (FFI): tabla agrupada con los métodos fluidos de 1.0 (groupBy, fontSize,
// padding, zebraColor, columnas auto/format), PDF real y extracción de texto.
//   php -d ffi.enable=1 scripts/ci/smoke/sdks/smoke.php

spl_autoload_register(function (string $class): void {
    if (str_starts_with($class, 'FlowPdf\\')) {
        require __DIR__ . '/../../../../sdk/php/src/' . str_replace('\\', '/', substr($class, 8)) . '.php';
    }
});

use FlowPdf\ReportDocument;

$rows = [
    ['categoria' => 'Servidores', 'sku' => 'SRV-01', 'descripcion' => 'Servidor 32GB RAM', 'monto' => 3850],
    ['categoria' => 'Servidores', 'sku' => 'SRV-02', 'descripcion' => 'Servidor 64GB RAM', 'monto' => 5200],
    ['categoria' => 'Redes', 'sku' => 'SW-48P', 'descripcion' => 'Switch 48 puertos PoE+', 'monto' => 1450],
];

$doc = ReportDocument::create()->content(fn($c) => $c->table(fn($t) => $t
    ->groupBy('categoria', '#E8F0FE', '#1F3B8A')
    ->fontSize(8.5)->padding(6, 4)
    ->headerColor('#FFFFFF')->textColor('#111827')->zebraColor('#F8FAFC')
    ->column('Código', 'sku', fn($col) => $col->auto())
    ->column('Descripción', 'descripcion', fn($col) => $col->flex(1))
    ->column('Monto', 'monto', fn($col) => $col->auto()->currency()->right())
    ->data($rows)));

$text = ReportDocument::extractText($doc->renderPdf());
foreach (['Servidores', 'Redes', 'SRV-01', '$3850.00'] as $k) {
    if (!str_contains($text, $k)) {
        fwrite(STDERR, "Falta \"$k\" en el PDF:\n$text\n");
        exit(1);
    }
}
echo "SDK PHP: SMOKE TEST PASSED\n";
