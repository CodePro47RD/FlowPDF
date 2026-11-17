<?php

namespace ReportForge;

use ReportForge\Builders\PageConfigBuilder;
use ReportForge\Builders\ColumnBuilder;
use ReportForge\Builders\SingleContainerBuilder;

class ReportDocument
{
    private array $doc;

    public function __construct()
    {
        $this->doc = [
            'version' => '2.0',
            'page' => (new PageConfigBuilder())->build(),
            'content' => ['type' => 'column', 'items' => []]
        ];
    }

    public static function create(?callable $pageConfigure = null): self
    {
        $doc = new self();
        if ($pageConfigure !== null) {
            $doc->page($pageConfigure);
        }
        return $doc;
    }

    public function title(string $title): self
    {
        $this->doc['title'] = $title;
        return $this;
    }

    public function author(string $author): self
    {
        $this->doc['author'] = $author;
        return $this;
    }

    public function page(callable $configure): self
    {
        $b = new PageConfigBuilder();
        $configure($b);
        $this->doc['page'] = $b->build();
        return $this;
    }

    public function header(callable $configure): self
    {
        $b = new SingleContainerBuilder();
        $configure($b);
        $child = $b->build();
        if ($child !== null) {
            $this->doc['header'] = $child;
        }
        return $this;
    }

    public function content(callable $configure): self
    {
        $b = new ColumnBuilder();
        $configure($b);
        $this->doc['content'] = $b->build();
        return $this;
    }

    public function footer(callable $configure): self
    {
        $b = new SingleContainerBuilder();
        $configure($b);
        $child = $b->build();
        if ($child !== null) {
            $this->doc['footer'] = $child;
        }
        return $this;
    }

    public function addFont(string $name, ?string $path = null, ?string $data = null): self
    {
        if (!isset($this->doc['fonts'])) {
            $this->doc['fonts'] = [];
        }
        $fontDef = ['name' => $name];
        if ($path !== null) $fontDef['path'] = $path;
        if ($data !== null) $fontDef['data'] = $data;
        $this->doc['fonts'][] = $fontDef;
        return $this;
    }

    public static function registerFont(string $name, string $fontBytes): bool
    {
        return ReportForgeEngine::registerFont($name, $fontBytes);
    }

    public function build(): array
    {
        return $this->doc;
    }

    public function toJson(int $flags = JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE): string
    {
        return json_encode($this->build(), $flags);
    }

    public function renderPdf(mixed $data = null): string
    {
        return ReportForgeEngine::renderPdf($this->build(), $data);
    }

    public static function extractText(string $pdfBytes): string
    {
        return ReportForgeEngine::extractText($pdfBytes);
    }

    public static function extractDocument(string $pdfBytes, ?array $options = null): array
    {
        return ReportForgeEngine::extractDocument($pdfBytes, $options);
    }
}
