<?php

namespace FlowPdf\Builders;

class ContainerBuilder
{
    private array $container = [
        'type' => 'container'
    ];

    public function padding(float $padding): self
    {
        $this->container['padding'] = $padding;
        return $this;
    }

    public function margin(float $margin): self
    {
        $this->container['margin'] = $margin;
        return $this;
    }

    public function background(string $color): self
    {
        $this->container['background'] = $color;
        return $this;
    }

    public function border(string $color, float $width = 1.0, float $radius = 0.0): self
    {
        $this->container['border_color'] = $color;
        $this->container['border_width'] = $width;
        $this->container['border_radius'] = $radius;
        return $this;
    }

    public function child(mixed $component): self
    {
        $this->container['child'] = is_object($component) && method_exists($component, 'build')
            ? $component->build()
            : $component;
        return $this;
    }

    public function build(): array
    {
        return $this->container;
    }
}
