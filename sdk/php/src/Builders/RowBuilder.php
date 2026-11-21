<?php

namespace FlowPdf\Builders;

class RowBuilder
{
    private array $row = [
        'type' => 'row',
        'items' => [],
        'spacing' => 0.0
    ];

    public function __construct(float $spacing = 0.0)
    {
        $this->row['spacing'] = $spacing;
    }

    public function item(mixed $componentOrFn, ?float $width = null, ?float $flex = null): self
    {
        if (is_callable($componentOrFn)) {
            $col = new ColumnBuilder();
            $componentOrFn($col);
            $comp = $col->build();
        } elseif (is_object($componentOrFn) && method_exists($componentOrFn, 'build')) {
            $comp = $componentOrFn->build();
        } else {
            $comp = $componentOrFn;
        }

        $this->row['items'][] = [
            'width' => $width,
            'flex' => $flex,
            'item' => $comp
        ];
        return $this;
    }

    public function column(callable $configure, ?float $width = null, ?float $flex = null): self
    {
        $col = new ColumnBuilder();
        $configure($col);
        return $this->item($col, $width, $flex);
    }

    public function build(): array
    {
        return $this->row;
    }
}
