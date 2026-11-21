<?php

namespace FlowPdf\Builders;

class TextBuilder
{
    private array $text;

    public function __construct(string $value)
    {
        $this->text = [
            'type' => 'text',
            'value' => $value
        ];
    }

    public function style(string $style): self { $this->text['style'] = $style; return $this; }
    public function h1(): self { return $this->style('h1'); }
    public function h2(): self { return $this->style('h2'); }
    public function h3(): self { return $this->style('h3'); }
    public function body(): self { return $this->style('body'); }
    public function caption(): self { return $this->style('caption'); }

    public function align(string $align): self { $this->text['alignment'] = $align; return $this; }
    public function left(): self { return $this->align('left'); }
    public function center(): self { return $this->align('center'); }
    public function right(): self { return $this->align('right'); }

    public function color(string $hexOrName): self { $this->text['color'] = $hexOrName; return $this; }
    public function fontSize(float $size): self { $this->text['font_size'] = $size; return $this; }
    public function bold(bool $bold = true): self { $this->text['bold'] = $bold; return $this; }
    public function italic(bool $italic = true): self { $this->text['italic'] = $italic; return $this; }
    public function underline(bool $underline = true): self { $this->text['underline'] = $underline; return $this; }

    public function build(): array
    {
        return $this->text;
    }
}
