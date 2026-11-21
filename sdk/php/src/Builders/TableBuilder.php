<?php

namespace FlowPdf\Builders;

class TableBuilder
{
    private array $table = [
        'type' => 'table',
        'columns' => [],
        'zebra' => true,
        'repeat_header' => true
    ];

    public function column(string $title, ?string $field = null, ?callable $configure = null): self
    {
        $b = new TableColumnBuilder($title);
        if ($field !== null) {
            $b->field($field);
        }
        if ($configure !== null) {
            $configure($b);
        }
        $this->table['columns'][] = $b->build();
        return $this;
    }

    public function source(string $expression): self
    {
        $this->table['source'] = $expression;
        return $this;
    }

    public function data(array $rows): self
    {
        $this->table['data'] = $rows;
        return $this;
    }

    public function rows(array $rows): self
    {
        return $this->data($rows);
    }

    public function headerBackground(string $color): self
    {
        $this->table['header_background'] = $color;
        return $this;
    }

    public function zebra(bool $enabled = true): self
    {
        $this->table['zebra'] = $enabled;
        return $this;
    }

    public function border(string $color, float $width = 0.5): self
    {
        $this->table['border_color'] = $color;
        $this->table['border_width'] = $width;
        return $this;
    }

    public function build(): array
    {
        return $this->table;
    }
}
