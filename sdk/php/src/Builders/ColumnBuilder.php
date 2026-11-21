<?php

namespace FlowPdf\Builders;

class ColumnBuilder
{
    private array $column = [
        'type' => 'column',
        'items' => [],
        'spacing' => 0.0
    ];

    public function __construct(float $spacing = 0.0)
    {
        $this->column['spacing'] = $spacing;
    }

    public function text(string $value, ?callable $configure = null): self
    {
        $b = new TextBuilder($value);
        if ($configure !== null) {
            $configure($b);
        }
        $this->column['items'][] = $b->build();
        return $this;
    }

    public function spacer(float $height = 10.0): self
    {
        $this->column['items'][] = ['type' => 'spacer', 'height' => $height];
        return $this;
    }

    public function divider(float $thickness = 1.0, ?string $color = null, float $margin = 5.0): self
    {
        $div = ['type' => 'divider', 'thickness' => $thickness, 'margin' => $margin];
        if ($color !== null) {
            $div['color'] = $color;
        }
        $this->column['items'][] = $div;
        return $this;
    }

    public function row(callable $configure, float $spacing = 0.0): self
    {
        $b = new RowBuilder($spacing);
        $configure($b);
        $this->column['items'][] = $b->build();
        return $this;
    }

    public function table(callable $configure): self
    {
        $b = new TableBuilder();
        $configure($b);
        $this->column['items'][] = $b->build();
        return $this;
    }

    public function qr(string $value, float $size = 80.0, ?string $fillColor = null, ?string $backColor = null): self
    {
        $qr = ['type' => 'qr', 'value' => $value, 'size' => $size];
        if ($fillColor !== null) {
            $qr['fill_color'] = $fillColor;
        }
        if ($backColor !== null) {
            $qr['back_color'] = $backColor;
        }
        $this->column['items'][] = $qr;
        return $this;
    }

    public function qrCode(string $value, float $size = 80.0, ?string $fillColor = null, ?string $backColor = null): self
    {
        return $this->qr($value, $size, $fillColor, $backColor);
    }

    public function barcode(string $value, string $barcodeType = 'code128', float $width = 150.0, float $height = 40.0, bool $includeText = true): self
    {
        $this->column['items'][] = [
            'type' => 'barcode',
            'value' => $value,
            'barcode_type' => $barcodeType,
            'width' => $width,
            'height' => $height,
            'include_text' => $includeText
        ];
        return $this;
    }

    public function container(callable $configure): self
    {
        $b = new ContainerBuilder();
        $configure($b);
        $this->column['items'][] = $b->build();
        return $this;
    }

    public function image(string $source, ?float $width = null, ?float $height = null, ?string $fit = null, ?string $alignment = null): self
    {
        $img = ['type' => 'image', 'source' => $source];
        if ($width !== null) $img['width'] = $width;
        if ($height !== null) $img['height'] = $height;
        if ($fit !== null) $img['fit'] = $fit;
        if ($alignment !== null) $img['alignment'] = $alignment;
        $this->column['items'][] = $img;
        return $this;
    }

    public function build(): array
    {
        return $this->column;
    }
}
