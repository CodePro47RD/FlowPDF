<?php

namespace FlowPdf\Builders;

class PageConfigBuilder
{
    private array $config = [
        'size' => 'A4',
        'orientation' => 'portrait',
        'margin' => 15.0
    ];

    public function size(string $size): self
    {
        $this->config['size'] = $size;
        return $this;
    }

    public function a4(): self { return $this->size('A4'); }
    public function letter(): self { return $this->size('Letter'); }
    public function legal(): self { return $this->size('Legal'); }
    public function a3(): self { return $this->size('A3'); }
    public function a5(): self { return $this->size('A5'); }

    public function orientation(string $orientation): self
    {
        $this->config['orientation'] = $orientation;
        return $this;
    }

    public function portrait(): self { return $this->orientation('portrait'); }
    public function landscape(): self { return $this->orientation('landscape'); }

    public function margin(float $margin): self
    {
        $this->config['margin'] = $margin;
        return $this;
    }

    public function margins(float $top, float $right, float $bottom, float $left): self
    {
        $this->config['margin_top'] = $top;
        $this->config['margin_right'] = $right;
        $this->config['margin_bottom'] = $bottom;
        $this->config['margin_left'] = $left;
        return $this;
    }

    public function build(): array
    {
        return $this->config;
    }
}
