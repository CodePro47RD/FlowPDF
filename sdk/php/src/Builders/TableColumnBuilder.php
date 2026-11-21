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

    public function build(): array
    {
        return $this->column;
    }
}
