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

    public function repeatHeader(bool $enabled = true): self
    {
        $this->table['repeat_header'] = $enabled;
        return $this;
    }

    /** Tamaño de letra de las celdas (pt). Por defecto 9. */
    public function fontSize(float $size): self
    {
        $this->table['font_size'] = $size;
        return $this;
    }

    /** Relleno de cada celda (pt): horizontal y vertical. Por defecto 8 y 5.5. */
    public function padding(float $horizontal, float $vertical): self
    {
        $this->table['padding_x'] = $horizontal;
        $this->table['padding_y'] = $vertical;
        return $this;
    }

    /** Color del texto de la cabecera. */
    public function headerColor(string $color): self
    {
        $this->table['header_color'] = $color;
        return $this;
    }

    /** Color del texto de las celdas. */
    public function textColor(string $color): self
    {
        $this->table['text_color'] = $color;
        return $this;
    }

    /** Filas alternas con fondo de este color (activa zebra). */
    public function zebraColor(string $color): self
    {
        $this->table['zebra'] = true;
        $this->table['zebra_color'] = $color;
        return $this;
    }

    /**
     * Agrupa las filas por un campo: cada vez que cambia su valor se intercala un título a todo el ancho
     * (las filas deben venir ordenadas por ese campo).
     */
    public function groupBy(string $field, ?string $background = null, ?string $color = null): self
    {
        $this->table['group_by'] = $field;
        if ($background !== null) {
            $this->table['group_background'] = $background;
        }
        if ($color !== null) {
            $this->table['group_color'] = $color;
        }
        return $this;
    }

    public function build(): array
    {
        return $this->table;
    }
}
