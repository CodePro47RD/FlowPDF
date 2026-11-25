/**
 * FlowPDF TypeScript Strong Types & Schema Definitions
 * Fully aligned with FlowPDF Pydantic v2 AST Specifications.
 */

export type PageSize = 'A4' | 'Letter' | 'Legal' | 'A3' | 'A5' | string;
export type PageOrientation = 'portrait' | 'landscape';

export interface PageConfig {
    size?: PageSize;
    orientation?: PageOrientation;
    margin?: number;
    margin_top?: number;
    margin_bottom?: number;
    margin_left?: number;
    margin_right?: number;
}

export type TextStyle = 'h1' | 'h2' | 'h3' | 'h4' | 'body' | 'caption' | 'code' | string;
export type TextAlignment = 'left' | 'center' | 'right' | 'justify';
export type VerticalAlignment = 'top' | 'middle' | 'bottom';
export type HorizontalAlignment = 'left' | 'center' | 'right';
export type ImageFit = 'contain' | 'cover' | 'fill' | 'none';
export type ChartType = 'bar' | 'line' | 'pie' | 'area' | 'donut' | 'multi_bar';
export type BarcodeType = 'code128' | 'ean13';
export type ColumnFormat = 'currency' | 'number' | 'percentage' | 'date' | 'uppercase' | 'lowercase' | string;

export interface TextComponent {
    type: 'text';
    value: string;
    style?: TextStyle;
    alignment?: TextAlignment;
    color?: string;
    font_size?: number;
    bold?: boolean;
    italic?: boolean;
    underline?: boolean;
    strike?: boolean;
    font?: string;
}

export interface ImageComponent {
    type: 'image';
    source: string;
    width?: number;
    height?: number;
    fit?: ImageFit;
    alignment?: HorizontalAlignment;
}

export interface SpacerComponent {
    type: 'spacer';
    height?: number;
}

export interface DividerComponent {
    type: 'divider';
    thickness?: number;
    color?: string;
    margin?: number;
}

export interface PageNumberComponent {
    type: 'page_number';
    format?: string;
    alignment?: HorizontalAlignment;
    style?: TextStyle;
}

export interface RowItem {
    width?: number;
    flex?: number;
    item: AnyComponent;
}

export interface RowComponent {
    type: 'row';
    items: Array<AnyComponent | RowItem>;
    spacing?: number;
    vertical_alignment?: VerticalAlignment;
}

export interface ColumnComponent {
    type: 'column';
    items: AnyComponent[];
    spacing?: number;
}

export interface ContainerComponent {
    type: 'container';
    child?: AnyComponent;
    width?: number;
    height?: number;
    padding?: number;
    margin?: number;
    background?: string;
    border_color?: string;
    border_width?: number;
    border_radius?: number;
    alignment?: HorizontalAlignment;
}

export interface TableColumn {
    title: string;
    field?: string;
    width?: number;
    flex?: number;
    format?: ColumnFormat;
    align?: HorizontalAlignment;
    /** Ancho según el contenido (texto más ancho de la columna, cabecera incluida). Su texto no se parte. */
    auto?: boolean;
}

export interface TableComponent {
    type: 'table';
    columns: TableColumn[];
    source?: string;
    data?: Array<Record<string, any>>;
    header_background?: string;
    zebra?: boolean;
    border_color?: string;
    border_width?: number;
    repeat_header?: boolean;
    /** Tamaño de letra de las celdas (pt). Por defecto 9. */
    font_size?: number;
    /** Relleno horizontal y vertical de cada celda (pt). Por defecto 8 y 5.5. */
    padding_x?: number;
    padding_y?: number;
    /** Color del texto de la cabecera y de las celdas. */
    header_color?: string;
    text_color?: string;
    /** Fondo de las filas alternas (con zebra). */
    zebra_color?: string;
    /** Campo que agrupa las filas; las filas deben venir ordenadas por ese campo. */
    group_by?: string;
    group_background?: string;
    group_color?: string;
}

export interface ChartSeries {
    name: string;
    values: number[];
    color?: string;
}

export interface ChartComponent {
    type: 'chart';
    chart_type?: ChartType;
    title?: string;
    labels?: string[] | string;
    values?: number[] | string;
    series?: ChartSeries[] | string;
    width?: number;
    height?: number;
    colors?: string[];
    theme?: 'light' | 'dark';
    donut?: boolean;
}

export interface QrComponent {
    type: 'qr';
    value: string;
    size?: number;
    fill_color?: string;
    back_color?: string;
}

export interface BarcodeComponent {
    type: 'barcode';
    value: string;
    barcode_type?: BarcodeType;
    width?: number;
    height?: number;
    include_text?: boolean;
}

export type AnyComponent =
    | TextComponent
    | ImageComponent
    | SpacerComponent
    | DividerComponent
    | PageNumberComponent
    | ColumnComponent
    | RowComponent
    | ContainerComponent
    | TableComponent
    | ChartComponent
    | QrComponent
    | BarcodeComponent;

export interface CustomFontDefinition {
    name: string;
    path?: string;
    data?: string;
}

export interface WatermarkDefinition {
    text: string;
    x?: number;
    y?: number;
    position?: 'center' | 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'diagonal' | string;
    rotation?: number;
    opacity?: number;
    font_size?: number;
    color?: string;
    background?: boolean;
}

export interface DocumentDefinition {
    page?: PageConfig;
    header?: AnyComponent;
    content: AnyComponent | AnyComponent[];
    footer?: AnyComponent;
    metadata?: Record<string, any>;
    fonts?: CustomFontDefinition[];
    watermark?: WatermarkDefinition;
}

export interface ReportPayload<TData = any> {
    template?: string;
    document?: DocumentDefinition;
    data?: TData;
    format?: 'pdf' | 'xlsx' | 'docx' | 'html' | string;
    response_type?: 'binary' | 'json';
}

export type ReportJobStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface ReportJobResponse {
    job_id: string;
    status: ReportJobStatus;
    format: string;
    download_url?: string;
    error_message?: string;
    created_at?: string;
    completed_at?: string;
}

export interface ClientOptions {
    baseUrl: string;
    apiKey: string;
    timeoutMs?: number;
}
