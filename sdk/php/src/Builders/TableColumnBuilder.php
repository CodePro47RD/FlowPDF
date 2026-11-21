<?php

namespace FlowPdf\Builders;

class TableColumnBuilder
{
    private array $column;

    public function __construct(string $title)
    {
        $this->column = [
            'title' => $title,
            'flex' => 1.0,
            'align' => 'left'
        ];
    }

    public function field(string $field): self { $this->column['field'] = $field; return $this; }
    public function width(float $width): self { $this->column['width'] = $width; return $this; }
    public function flex(float $flex): self { $this->column['flex'] = $flex; return $this; }
    public function align(string $align): self { $this->column['align'] = $align; return $this; }
    public function right(): self { return $this->align('right'); }
    public function center(): self { return $this->align('center'); }
    public function left(): self { return $this->align('left'); }

    /** Ancho según el contenido (texto más ancho de la columna, cabecera incluida). Su texto no se parte. */
    public function auto(bool $enabled = true): self { $this->column['auto'] = $enabled; return $this; }

    /** Formateador del valor: currency, number, percentage, date, uppercase, lowercase. */
    public function format(string $format): self { $this->column['format'] = $format; return $this; }
    public function currency(): self { return $this->format('currency'); }
    public function number(): self { return $this->format('number'); }
    public function percentage(): self { return $this->format('percentage'); }
    public function date(): self { return $this->format('date'); }
    public function uppercase(): self { return $this->format('uppercase'); }

    public function build(): array
    {
        return $this->column;
    }
}
