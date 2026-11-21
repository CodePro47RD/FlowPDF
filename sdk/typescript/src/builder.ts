import {
    AnyComponent,
    BarcodeComponent,
    BarcodeType,
    ChartComponent,
    ChartType,
    ColumnComponent,
    ContainerComponent,
    DividerComponent,
    DocumentDefinition,
    HorizontalAlignment,
    ImageComponent,
    ImageFit,
    PageConfig,
    PageNumberComponent,
    PageOrientation,
    PageSize,
    RowComponent,
    RowItem,
    SpacerComponent,
    TableColumn,
    TableComponent,
    TextAlignment,
    TextComponent,
    TextStyle
} from './types';

export class PageConfigBuilder {
    private readonly config: PageConfig = {};

    size(size: PageSize): this {
        this.config.size = size;
        return this;
    }

    a4(): this { return this.size('A4'); }
    letter(): this { return this.size('Letter'); }
    legal(): this { return this.size('Legal'); }
    a3(): this { return this.size('A3'); }
    a5(): this { return this.size('A5'); }

    orientation(orientation: PageOrientation): this {
        this.config.orientation = orientation;
        return this;
    }

    portrait(): this { return this.orientation('portrait'); }
    landscape(): this { return this.orientation('landscape'); }

    margin(margin: number): this {
        this.config.margin = margin;
        return this;
    }

    margins(top: number, right: number, bottom: number, left: number): this {
        this.config.margin_top = top;
        this.config.margin_right = right;
        this.config.margin_bottom = bottom;
        this.config.margin_left = left;
        return this;
    }

    build(): PageConfig {
        return this.config;
    }
}

export class TextBuilder {
    private readonly _text: TextComponent;

    constructor(value: string) {
        this._text = { type: 'text', value };
    }

    style(style: TextStyle): this { this._text.style = style; return this; }
    h1(): this { return this.style('h1'); }
    h2(): this { return this.style('h2'); }
    h3(): this { return this.style('h3'); }
    body(): this { return this.style('body'); }
    caption(): this { return this.style('caption'); }

    color(color: string): this { this._text.color = color; return this; }
    fontSize(size: number): this { this._text.font_size = size; return this; }
    align(alignment: TextAlignment): this { this._text.alignment = alignment; return this; }
    alignLeft(): this { return this.align('left'); }
    alignCenter(): this { return this.align('center'); }
    alignRight(): this { return this.align('right'); }
    justify(): this { return this.align('justify'); }

    bold(bold = true): this { this._text.bold = bold; return this; }
    italic(italic = true): this { this._text.italic = italic; return this; }
    underline(underline = true): this { this._text.underline = underline; return this; }
    strike(strike = true): this { this._text.strike = strike; return this; }
    font(font: string): this { this._text.font = font; return this; }

    build(): TextComponent {
        return this._text;
    }
}

export class TableColumnsBuilder {
    private readonly columns: TableColumn[] = [];

    column(field: string, title: string, options?: Partial<Omit<TableColumn, 'field' | 'title'>>): this {
        this.columns.push({
            field,
            title,
            flex: options?.flex ?? 1.0,
            ...options
        });
        return this;
    }

    add(title: string, options?: Partial<Omit<TableColumn, 'title'>>): this {
        this.columns.push({
            title,
            flex: options?.flex ?? 1.0,
            ...options
        });
        return this;
    }

    build(): TableColumn[] {
        return this.columns;
    }
}

export class TableBuilder {
    private readonly _table: TableComponent = {
        type: 'table',
        columns: []
    };

    source(source: string): this {
        this._table.source = source;
        return this;
    }

    data(data: Array<Record<string, any>>): this {
        this._table.data = data;
        return this;
    }

    zebra(zebra = true): this {
        this._table.zebra = zebra;
        return this;
    }

    headerBackground(color: string): this {
        this._table.header_background = color;
        return this;
    }

    border(color = '#E2E8F0', width = 0.5): this {
        this._table.border_color = color;
        this._table.border_width = width;
        return this;
    }

    repeatHeader(repeat = true): this {
        this._table.repeat_header = repeat;
        return this;
    }

    /** Tamaño de letra de las celdas (pt). */
    fontSize(size: number): this {
        this._table.font_size = size;
        return this;
    }

    /** Relleno de cada celda (pt): horizontal y vertical. */
    padding(horizontal: number, vertical: number): this {
        this._table.padding_x = horizontal;
        this._table.padding_y = vertical;
        return this;
    }

    /** Color del texto de la cabecera. */
    headerColor(color: string): this {
        this._table.header_color = color;
        return this;
    }

    /** Color del texto de las celdas. */
    textColor(color: string): this {
        this._table.text_color = color;
        return this;
    }

    /** Filas alternas con fondo de este color (activa zebra). */
    zebraColor(color: string): this {
        this._table.zebra = true;
        this._table.zebra_color = color;
        return this;
    }

    /**
     * Agrupa las filas por un campo: cada vez que cambia su valor se intercala un título a todo el ancho
     * (las filas deben venir ordenadas por ese campo).
     */
    groupBy(field: string, background?: string, color?: string): this {
        this._table.group_by = field;
        if (background !== undefined) this._table.group_background = background;
        if (color !== undefined) this._table.group_color = color;
        return this;
    }

    columns(fn: (b: TableColumnsBuilder) => void): this {
        const b = new TableColumnsBuilder();
        fn(b);
        this._table.columns = b.build();
        return this;
    }

    build(): TableComponent {
        return this._table;
    }
}

export class SingleContainerBuilder {
    private component?: AnyComponent;

    set(component: AnyComponent): this {
        this.component = component;
        return this;
    }

    text(value: string, fn?: (t: TextBuilder) => void): this {
        const b = new TextBuilder(value);
        if (fn) fn(b);
        this.component = b.build();
        return this;
    }

    image(source: string, options?: { width?: number; height?: number; fit?: ImageFit; alignment?: HorizontalAlignment }): this {
        this.component = { type: 'image', source, ...options };
        return this;
    }

    qr(value: string, size = 80, fillColor?: string, backColor?: string): this {
        this.component = { type: 'qr', value, size, fill_color: fillColor, back_color: backColor };
        return this;
    }

    barcode(value: string, barcodeType: BarcodeType = 'code128', width = 180, height = 50, includeText = true): this {
        this.component = { type: 'barcode', value, barcode_type: barcodeType, width, height, include_text: includeText };
        return this;
    }

    pageNumber(format = 'Página {page} de {total}', alignment: HorizontalAlignment = 'right', style?: TextStyle): this {
        this.component = { type: 'page_number', format, alignment, style };
        return this;
    }

    column(fn: (c: ColumnBuilder) => void): this {
        const b = new ColumnBuilder();
        fn(b);
        this.component = b.build();
        return this;
    }

    row(fn: (r: RowBuilder) => void): this {
        const b = new RowBuilder();
        fn(b);
        this.component = b.build();
        return this;
    }

    table(fn: (t: TableBuilder) => void): this {
        const b = new TableBuilder();
        fn(b);
        this.component = b.build();
        return this;
    }

    build(): AnyComponent {
        return this.component ?? { type: 'text', value: '' };
    }
}

export class ColumnBuilder {
    private readonly _column: ColumnComponent = {
        type: 'column',
        items: [],
        spacing: 0
    };

    spacing(spacing: number): this {
        this._column.spacing = spacing;
        return this;
    }

    add(component: AnyComponent): this {
        this._column.items.push(component);
        return this;
    }

    text(value: string, fn?: (t: TextBuilder) => void): this {
        const b = new TextBuilder(value);
        if (fn) fn(b);
        this._column.items.push(b.build());
        return this;
    }

    spacer(height = 10): this {
        this._column.items.push({ type: 'spacer', height });
        return this;
    }

    divider(color?: string, thickness = 1.0, margin = 8.0): this {
        this._column.items.push({ type: 'divider', color, thickness, margin });
        return this;
    }

    table(fn: (t: TableBuilder) => void): this {
        const b = new TableBuilder();
        fn(b);
        this._column.items.push(b.build());
        return this;
    }

    row(fn: (r: RowBuilder) => void): this {
        const b = new RowBuilder();
        fn(b);
        this._column.items.push(b.build());
        return this;
    }

    column(fn: (c: ColumnBuilder) => void): this {
        const b = new ColumnBuilder();
        fn(b);
        this._column.items.push(b.build());
        return this;
    }

    image(source: string, options?: { width?: number; height?: number; fit?: ImageFit; alignment?: HorizontalAlignment }): this {
        this._column.items.push({ type: 'image', source, ...options });
        return this;
    }

    qr(value: string, size = 80): this {
        this._column.items.push({ type: 'qr', value, size });
        return this;
    }

    barcode(value: string, barcodeType: BarcodeType = 'code128', width = 180, height = 50): this {
        this._column.items.push({ type: 'barcode', value, barcode_type: barcodeType, width, height });
        return this;
    }

    chart(type: ChartType, options: {
        title?: string;
        labels?: string[];
        values?: number[];
        series?: Array<{ name: string; values: number[]; color?: string }>;
        width?: number;
        height?: number;
        colors?: string[];
        theme?: 'light' | 'dark';
        donut?: boolean;
    }): this {
        this._column.items.push({
            type: 'chart',
            chart_type: type,
            width: options.width ?? 400,
            height: options.height ?? 200,
            ...options
        });
        return this;
    }

    build(): ColumnComponent {
        return this._column;
    }
}

export class RowBuilder {
    private readonly _row: RowComponent = {
        type: 'row',
        items: [],
        spacing: 0
    };

    spacing(spacing: number): this {
        this._row.spacing = spacing;
        return this;
    }

    verticalAlignment(align: 'top' | 'middle' | 'bottom'): this {
        this._row.vertical_alignment = align;
        return this;
    }

    constantItem(width: number, componentOrFn: AnyComponent | ((c: SingleContainerBuilder) => void)): this {
        if (typeof componentOrFn === 'function') {
            const b = new SingleContainerBuilder();
            componentOrFn(b);
            this._row.items.push({ width, item: b.build() });
        } else {
            this._row.items.push({ width, item: componentOrFn });
        }
        return this;
    }

    relativeItem(flex: number, componentOrFn: AnyComponent | ((c: SingleContainerBuilder) => void)): this {
        if (typeof componentOrFn === 'function') {
            const b = new SingleContainerBuilder();
            componentOrFn(b);
            this._row.items.push({ flex, item: b.build() });
        } else {
            this._row.items.push({ flex, item: componentOrFn });
        }
        return this;
    }

    build(): RowComponent {
        return this._row;
    }
}

export class ReportDocument {
    private readonly doc: DocumentDefinition = {
        content: []
    };

    static create(fn?: (b: PageConfigBuilder) => void): ReportDocument {
        const doc = new ReportDocument();
        if (fn) {
            const b = new PageConfigBuilder();
            fn(b);
            doc.doc.page = b.build();
        }
        return doc;
    }

    page(fn: (b: PageConfigBuilder) => void): this {
        const b = new PageConfigBuilder();
        fn(b);
        this.doc.page = b.build();
        return this;
    }

    header(fn: (b: SingleContainerBuilder) => void): this {
        const b = new SingleContainerBuilder();
        fn(b);
        this.doc.header = b.build();
        return this;
    }

    content(fn: (b: ColumnBuilder) => void): this {
        const b = new ColumnBuilder();
        fn(b);
        this.doc.content = b.build();
        return this;
    }

    footer(fn: (b: SingleContainerBuilder) => void): this {
        const b = new SingleContainerBuilder();
        fn(b);
        this.doc.footer = b.build();
        return this;
    }

    addFont(name: string, path?: string, data?: string): this {
        if (!this.doc.fonts) {
            this.doc.fonts = [];
        }
        this.doc.fonts.push({ name, path, data });
        return this;
    }

    static registerFont(name: string, fontBytes: Uint8Array | Buffer): boolean {
        const { FlowPdfEngine } = require('./native');
        return FlowPdfEngine.registerFont(name, fontBytes);
    }

    build(): DocumentDefinition {
        return this.doc;
    }

    renderPdf(data?: object | string): Uint8Array {
        const { FlowPdfEngine } = require('./native');
        return FlowPdfEngine.renderPdf(this.build(), data);
    }

    static extractText(pdfBytes: Uint8Array | Buffer): string {
        const { FlowPdfEngine } = require('./native');
        return FlowPdfEngine.extractText(pdfBytes);
    }

    static extractDocument(pdfBytes: Uint8Array | Buffer, options?: object): any {
        const { FlowPdfEngine } = require('./native');
        return FlowPdfEngine.extractDocument(pdfBytes, options);
    }
}
