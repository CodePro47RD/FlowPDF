<?php

namespace ReportForge\Builders;

class SingleContainerBuilder
{
    private ?array $child = null;

    public function text(string $value, ?callable $configure = null): self
    {
        $b = new TextBuilder($value);
        if ($configure !== null) {
            $configure($b);
        }
        $this->child = $b->build();
        return $this;
    }

    public function row(callable $configure, float $spacing = 0.0): self
    {
        $b = new RowBuilder($spacing);
        $configure($b);
        $this->child = $b->build();
        return $this;
    }

    public function column(callable $configure, float $spacing = 0.0): self
    {
        $b = new ColumnBuilder($spacing);
        $configure($b);
        $this->child = $b->build();
        return $this;
    }

    public function table(callable $configure): self
    {
        $b = new TableBuilder();
        $configure($b);
        $this->child = $b->build();
        return $this;
    }

    public function qr(string $value, float $size = 80.0, ?string $fillColor = null, ?string $backColor = null): self
    {
        $qr = ['type' => 'qr', 'value' => $value, 'size' => $size];
        if ($fillColor !== null) $qr['fill_color'] = $fillColor;
        if ($backColor !== null) $qr['back_color'] = $backColor;
        $this->child = $qr;
        return $this;
    }

    public function qrCode(string $value, float $size = 80.0, ?string $fillColor = null, ?string $backColor = null): self
    {
        return $this->qr($value, $size, $fillColor, $backColor);
    }

    public function barcode(string $value, string $barcodeType = 'code128', float $width = 150.0, float $height = 40.0, bool $includeText = true): self
    {
        $this->child = [
            'type' => 'barcode',
            'value' => $value,
            'barcode_type' => $barcodeType,
            'width' => $width,
            'height' => $height,
            'include_text' => $includeText
        ];
        return $this;
    }

    public function build(): ?array
    {
        return $this->child;
    }
}
