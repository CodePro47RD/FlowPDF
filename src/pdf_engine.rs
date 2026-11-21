use std::collections::HashMap;
use std::io::Write;
use std::sync::Arc;
use lopdf::{dictionary, Document, Object, ObjectId, Stream};
use qrcode::QrCode;
use serde_json::Value;

use crate::ast::*;
use crate::barcode::Code128;
use crate::chart::ChartRenderer;
use crate::core::{Color, PageSize, Rect, Size};
use crate::font::{get_global_font, CustomFont};
use crate::image::{self, PdfImage};
use crate::metrics::helvetica_width;

// Tablas
const TABLE_FONT_SIZE: f32 = 9.0;
const TABLE_PAD_X: f32 = 8.0;
const TABLE_PAD_Y: f32 = 5.5;
const TABLE_HEADER_MIN_H: f32 = 24.0;
const TABLE_ROW_MIN_H: f32 = 20.0;

// Separación entre los elementos de un contenido múltiple y entre encabezado/pie y el contenido
const CONTENT_GAP: f32 = 6.0;
const HEADER_GAP: f32 = 10.0;


pub struct PdfEngine {
    pub default_font_size: f32,
}

/// Estado de un render: datos, fuentes e imágenes del documento y la página que se está dibujando.
struct RenderCtx<'a> {
    data: Option<&'a Value>,
    fonts: HashMap<String, (String, Arc<CustomFont>)>,
    font_counter: usize,
    images: Vec<ImageEntry>,
    page: usize,
    total_pages: usize,
}

/// Imagen registrada en el documento (una vez por fuente). `image` es None si no se pudo leer.
struct ImageEntry {
    source: String,
    alias: String,
    image: Option<Arc<PdfImage>>,
}

impl RenderCtx<'_> {
    /// Alias (`/ImN`) e imagen de una fuente; la carga y decodifica la primera vez.
    fn image(&mut self, source: &str) -> Option<(String, Arc<PdfImage>)> {
        if let Some(e) = self.images.iter().find(|e| e.source == source) {
            return e.image.clone().map(|img| (e.alias.clone(), img));
        }
        let decoded = image::load_source(source).and_then(|bytes| image::decode(&bytes)).ok().map(Arc::new);
        let alias = format!("/Im{}", self.images.len() + 1);
        self.images.push(ImageEntry { source: source.to_string(), alias: alias.clone(), image: decoded.clone() });
        decoded.map(|img| (alias, img))
    }
}

/// Páginas del contenido y cursor vertical dentro del área útil (entre encabezado y pie).
struct Pager {
    pages: Vec<Vec<PdfOp>>,
    y: f32,
    top: f32,
    bottom: f32,
}

impl Pager {
    fn new(top: f32, bottom: f32) -> Self {
        Self { pages: vec![Vec::new()], y: top, top, bottom }
    }

    fn ops(&mut self) -> &mut Vec<PdfOp> {
        self.pages.last_mut().expect("siempre hay una página")
    }

    fn new_page(&mut self) {
        self.pages.push(Vec::new());
        self.y = self.top;
    }

    fn at_top(&self) -> bool {
        self.y <= self.top + 0.01
    }

    fn fits(&self, height: f32) -> bool {
        self.y + height <= self.bottom + 0.01
    }

    /// Antes de colocar algo de alto `height`: si no cabe en lo que queda y la página ya tiene contenido,
    /// pasa a la siguiente. Lo que es más alto que una página entera se coloca igual al inicio de una.
    fn ensure(&mut self, height: f32) {
        if !self.fits(height) && !self.at_top() {
            self.new_page();
        }
    }

    /// Espacio vertical; si se sale del área útil no se arrastra a la página siguiente.
    fn space(&mut self, height: f32) {
        self.y += height;
        if self.y > self.bottom {
            self.new_page();
        }
    }
}

/// Texto ya partido en líneas, listo para dibujarse.
struct TextLayout {
    lines: Vec<(String, f32)>, // línea y su desplazamiento horizontal según la alineación
    font_ref: String,
    size: f32,
    color: Color,
    line_height: f32,
}

/// Fila de una tabla ya medida: de datos (líneas de cada celda) o título de grupo a todo el ancho.
enum TableRow {
    Data { cells: Vec<Vec<String>>, h: f32, alt: bool },
    Group { lines: Vec<String>, h: f32 },
}

impl TableRow {
    fn h(&self) -> f32 {
        match self {
            TableRow::Data { h, .. } | TableRow::Group { h, .. } => *h,
        }
    }
}

/// Tabla medida: anchos de columna, líneas de cada celda y estilo.
struct TableLayout {
    col_widths: Vec<f32>,
    aligns: Vec<Option<String>>,
    header: Vec<Vec<String>>,
    header_h: f32,
    header_bg: Color,
    header_color: Color,
    rows: Vec<TableRow>,
    zebra: Option<Color>,
    border: Option<(Color, f32)>,
    repeat_header: bool,
    font_size: f32,
    line_h: f32,
    pad_x: f32,
    pad_y: f32,
    text_color: Color,
    group_bg: Color,
    group_color: Color,
}

impl TableLayout {
    /// Alto de la fila `idx` más lo que no debe separarse de ella: un título de grupo va con su primera fila.
    fn keep_h(&self, idx: usize) -> f32 {
        match self.rows.get(idx) {
            Some(TableRow::Group { h, .. }) => h + self.rows.get(idx + 1).map(TableRow::h).unwrap_or(0.0),
            Some(row) => row.h(),
            None => 0.0,
        }
    }
}

impl PdfEngine {
    pub fn new() -> Self {
        Self { default_font_size: 10.0 }
    }

    pub fn render(&self, doc_ast: &DocumentDefinitionAst, data: Option<&Value>) -> Result<Vec<u8>, String> {
        let (page_w, page_h) = PageSize::from_str(&doc_ast.page.size).dimensions(&doc_ast.page.orientation);
        let margin_top = doc_ast.page.margin_top.unwrap_or(doc_ast.page.margin);
        let margin_bottom = doc_ast.page.margin_bottom.unwrap_or(doc_ast.page.margin);
        let margin_left = doc_ast.page.margin_left.unwrap_or(doc_ast.page.margin);
        let margin_right = doc_ast.page.margin_right.unwrap_or(doc_ast.page.margin);
        let content_w = page_w - (margin_left + margin_right);

        let mut ctx = RenderCtx {
            data,
            fonts: HashMap::new(),
            font_counter: 1,
            images: Vec::new(),
            page: 1,
            total_pages: 1,
        };

        // Fuentes personalizadas declaradas en el documento
        for f_ast in &doc_ast.fonts {
            let bytes_opt = if let Some(b64) = &f_ast.data_base64 {
                use base64::Engine;
                base64::engine::general_purpose::STANDARD.decode(b64).ok()
            } else if let Some(path) = &f_ast.path {
                std::fs::read(path).ok()
            } else {
                None
            };

            if let Some(bytes) = bytes_opt {
                if let Ok(font) = CustomFont::from_bytes(&f_ast.name, &bytes) {
                    let alias = format!("/FC{}", ctx.font_counter);
                    ctx.font_counter += 1;
                    ctx.fonts.insert(f_ast.name.to_lowercase(), (alias, Arc::new(font)));
                }
            }
        }

        // 1. Medir encabezado y pie: reservan su espacio en cada página
        let header_h = match &doc_ast.header {
            Some(h) => self.render_component(h, &mut ctx, margin_left, 0.0, content_w, &mut Vec::new())?.height,
            None => 0.0,
        };
        let footer_h = match &doc_ast.footer {
            Some(f) => self.render_component(f, &mut ctx, margin_left, 0.0, content_w, &mut Vec::new())?.height,
            None => 0.0,
        };

        let top = margin_top + if doc_ast.header.is_some() { header_h + HEADER_GAP } else { 0.0 };
        let footer_y = page_h - margin_bottom - footer_h;
        let bottom = if doc_ast.footer.is_some() { footer_y - HEADER_GAP } else { page_h - margin_bottom };

        // 2. Contenido: fluye por las páginas que hagan falta
        let mut pager = Pager::new(top, bottom);
        match &doc_ast.content {
            ContentAst::Single(comp) => self.flow(comp, &mut ctx, margin_left, content_w, &mut pager)?,
            // Igual que una columna con la separación del contenido
            ContentAst::Multiple(items) => {
                let column = ComponentAst::Column { items: items.clone(), spacing: CONTENT_GAP };
                self.flow(&column, &mut ctx, margin_left, content_w, &mut pager)?;
            }
        }

        // 3. Encabezado y pie en cada página, ya con el total de páginas
        let mut pages = pager.pages;
        ctx.total_pages = pages.len();
        for (idx, ops) in pages.iter_mut().enumerate() {
            ctx.page = idx + 1;
            if let Some(header) = &doc_ast.header {
                self.render_component(header, &mut ctx, margin_left, margin_top, content_w, ops)?;
            }
            if let Some(footer) = &doc_ast.footer {
                self.render_component(footer, &mut ctx, margin_left, footer_y, content_w, ops)?;
            }
        }

        self.build_pdf(page_w, page_h, pages, ctx)
    }

    /// Coloca un componente en el flujo de páginas. Columnas, textos y tablas se parten entre páginas;
    /// lo demás es un bloque indivisible que pasa entero a la página siguiente si no cabe.
    fn flow(&self, comp: &ComponentAst, ctx: &mut RenderCtx, x: f32, available_w: f32, pager: &mut Pager) -> Result<(), String> {
        match comp {
            ComponentAst::Column { items, spacing } => {
                for (idx, item) in items.iter().enumerate() {
                    if idx > 0 {
                        pager.space(*spacing);
                    }
                    // Un texto seguido de una tabla es su título: no queda solo al final de una página
                    if let (ComponentAst::Text { .. }, Some(next @ ComponentAst::Table { .. })) = (item, items.get(idx + 1)) {
                        let text = self.layout_text(item, ctx, available_w);
                        let table = self.layout_table(next, ctx, available_w);
                        pager.ensure(text.lines.len() as f32 * text.line_height + spacing + table.header_h + table.keep_h(0));
                    }
                    self.flow(item, ctx, x, available_w, pager)?;
                }
                Ok(())
            }

            ComponentAst::Text { .. } => {
                let layout = self.layout_text(comp, ctx, available_w);
                for (line, dx) in layout.lines {
                    pager.ensure(layout.line_height);
                    let y = pager.y;
                    pager.ops().push(PdfOp::Text {
                        text: line,
                        font_ref: layout.font_ref.clone(),
                        size: layout.size,
                        x: x + dx,
                        y,
                        color: layout.color,
                    });
                    pager.y += layout.line_height;
                }
                Ok(())
            }

            ComponentAst::Spacer { height } => {
                pager.space(*height);
                Ok(())
            }

            ComponentAst::Table { .. } => {
                let layout = self.layout_table(comp, ctx, available_w);
                // La cabecera no queda sola al final de una página
                pager.ensure(layout.header_h + layout.keep_h(0));
                let y = pager.y;
                self.draw_table_header(&layout, x, y, available_w, pager.ops());
                pager.y += layout.header_h;

                for (idx, row) in layout.rows.iter().enumerate() {
                    // Un título de grupo no queda solo al final de una página
                    if !pager.fits(layout.keep_h(idx)) && !pager.at_top() {
                        pager.new_page();
                        if layout.repeat_header {
                            let y = pager.y;
                            self.draw_table_header(&layout, x, y, available_w, pager.ops());
                            pager.y += layout.header_h;
                        }
                    }
                    let y = pager.y;
                    self.draw_table_row(&layout, idx, x, y, available_w, pager.ops());
                    pager.y += row.h();
                }
                Ok(())
            }

            _ => {
                let mut block = Vec::new();
                let size = self.render_component(comp, ctx, x, 0.0, available_w, &mut block)?;
                // Un contenedor más alto que una página no se puede mantener junto: se reparte su contenido
                // (sin fondo ni borde) en vez de salirse de la página por encima del pie
                if size.height > pager.bottom - pager.top + 0.01 {
                    if let ComponentAst::Container { child: Some(child), padding, margin, .. } = comp {
                        let inset = padding.unwrap_or(0.0) + margin.unwrap_or(0.0);
                        pager.space(inset);
                        self.flow(child, ctx, x + inset, (available_w - inset * 2.0).max(0.0), pager)?;
                        pager.space(inset);
                        return Ok(());
                    }
                }
                pager.ensure(size.height);
                let dy = pager.y;
                pager.ops().extend(block.into_iter().map(|op| op.translate(dy)));
                pager.y += size.height;
                Ok(())
            }
        }
    }

    /// Dibuja un componente completo en (x, y), sin partirlo entre páginas. Devuelve su tamaño.
    fn render_component(
        &self,
        comp: &ComponentAst,
        ctx: &mut RenderCtx,
        x: f32,
        y: f32,
        available_w: f32,
        ops: &mut Vec<PdfOp>,
    ) -> Result<Size, String> {
        match comp {
            ComponentAst::Text { .. } => {
                let layout = self.layout_text(comp, ctx, available_w);
                let total_h = layout.lines.len() as f32 * layout.line_height;
                for (idx, (line, dx)) in layout.lines.into_iter().enumerate() {
                    ops.push(PdfOp::Text {
                        text: line,
                        font_ref: layout.font_ref.clone(),
                        size: layout.size,
                        x: x + dx,
                        y: y + (idx as f32 * layout.line_height),
                        color: layout.color,
                    });
                }
                Ok(Size::new(available_w, total_h))
            }

            ComponentAst::Spacer { height } => Ok(Size::new(available_w, *height)),

            ComponentAst::Divider { thickness, color, margin } => {
                let div_color = color.as_deref().map(Color::from_hex).unwrap_or(Color::rgb(0.8, 0.85, 0.9));
                let line_y = y + margin;
                ops.push(PdfOp::Line {
                    x1: x,
                    y1: line_y,
                    x2: x + available_w,
                    y2: line_y,
                    thickness: *thickness,
                    color: div_color,
                });
                Ok(Size::new(available_w, margin * 2.0 + thickness))
            }

            ComponentAst::Column { items, spacing } => {
                let mut col_y = y;
                for (idx, item) in items.iter().enumerate() {
                    let s = self.render_component(item, ctx, x, col_y, available_w, ops)?;
                    col_y += s.height;
                    if idx + 1 < items.len() {
                        col_y += spacing;
                    }
                }
                Ok(Size::new(available_w, col_y - y))
            }

            ComponentAst::Row { items, spacing, .. } => {
                let count = items.len();
                if count == 0 {
                    return Ok(Size::zero());
                }

                let total_spacing = *spacing * (count - 1) as f32;
                let mut fixed_w = 0.0;
                let mut total_flex = 0.0;

                for item in items {
                    match item {
                        RowItemAst::Detailed { width, flex, .. } => {
                            if let Some(w) = width {
                                fixed_w += w;
                            } else {
                                total_flex += flex.unwrap_or(1.0);
                            }
                        }
                        RowItemAst::Simple(_) => {
                            total_flex += 1.0;
                        }
                    }
                }

                let available_flex_w = (available_w - fixed_w - total_spacing).max(0.0);
                let flex_unit = if total_flex > 0.0 { available_flex_w / total_flex } else { 0.0 };

                let mut cur_x = x;
                let mut max_h = 0.0;

                for item in items {
                    let (w, comp) = match item {
                        RowItemAst::Detailed { width, flex, item } => {
                            let item_w = width.unwrap_or_else(|| flex.unwrap_or(1.0) * flex_unit);
                            (item_w, item)
                        }
                        RowItemAst::Simple(comp) => (flex_unit, comp),
                    };

                    let s = self.render_component(comp, ctx, cur_x, y, w, ops)?;
                    if s.height > max_h {
                        max_h = s.height;
                    }
                    cur_x += w + spacing;
                }

                Ok(Size::new(available_w, max_h))
            }

            ComponentAst::Container {
                child,
                width,
                height,
                padding,
                margin,
                background,
                border_color,
                border_width,
                ..
            } => {
                let m = margin.unwrap_or(0.0);
                let p = padding.unwrap_or(0.0);
                let target_w = width.unwrap_or(available_w - (m * 2.0));
                let draw_x = x + m;
                let draw_y = y + m;

                let mut child_ops = Vec::new();
                let child_size = if let Some(c) = child {
                    self.render_component(c, ctx, draw_x + p, draw_y + p, target_w - (p * 2.0), &mut child_ops)?
                } else {
                    Size::zero()
                };

                let target_h = height.unwrap_or(child_size.height + (p * 2.0));

                if let Some(bg_hex) = background {
                    ops.push(PdfOp::RectFill {
                        rect: Rect::new(draw_x, draw_y, target_w, target_h),
                        color: Color::from_hex(bg_hex),
                    });
                }

                if let Some(bc_hex) = border_color {
                    ops.push(PdfOp::RectStroke {
                        rect: Rect::new(draw_x, draw_y, target_w, target_h),
                        thickness: border_width.unwrap_or(1.0),
                        color: Color::from_hex(bc_hex),
                    });
                }

                ops.extend(child_ops);
                Ok(Size::new(target_w + (m * 2.0), target_h + (m * 2.0)))
            }

            ComponentAst::Table { .. } => {
                let layout = self.layout_table(comp, ctx, available_w);
                self.draw_table_header(&layout, x, y, available_w, ops);
                let mut row_y = y + layout.header_h;
                for (idx, row) in layout.rows.iter().enumerate() {
                    self.draw_table_row(&layout, idx, x, row_y, available_w, ops);
                    row_y += row.h();
                }
                Ok(Size::new(available_w, row_y - y))
            }

            ComponentAst::Qr { value, size, fill_color, .. } => {
                let interpolated = interpolate_string(value, ctx.data);
                let qr = QrCode::new(interpolated.as_bytes()).map_err(|e| e.to_string())?;
                let qr_size = *size;
                let color = fill_color.as_deref().map(Color::from_hex).unwrap_or(Color::black());

                let modules = qr.to_colors();
                let width_in_modules = qr.width();
                let module_size = qr_size / width_in_modules as f32;

                for row in 0..width_in_modules {
                    for col in 0..width_in_modules {
                        if modules[row * width_in_modules + col] == qrcode::Color::Dark {
                            ops.push(PdfOp::RectFill {
                                rect: Rect::new(
                                    x + (col as f32 * module_size),
                                    y + (row as f32 * module_size),
                                    module_size,
                                    module_size,
                                ),
                                color,
                            });
                        }
                    }
                }

                Ok(Size::new(qr_size, qr_size))
            }

            ComponentAst::Barcode { value, width, height, .. } => {
                let interpolated = interpolate_string(value, ctx.data);
                let color = Color::black();

                if let Some(encoded) = Code128::encode(&interpolated) {
                    let bar_count = encoded.len();
                    let bar_w = width / bar_count as f32;

                    for (idx, char_bit) in encoded.chars().enumerate() {
                        if char_bit == '1' {
                            ops.push(PdfOp::RectFill {
                                rect: Rect::new(x + (idx as f32 * bar_w), y, bar_w, *height),
                                color,
                            });
                        }
                    }

                    let text_w = helvetica_width(&interpolated, 8.0, false);
                    ops.push(PdfOp::Text {
                        text: interpolated,
                        font_ref: "/F1".to_string(),
                        size: 8.0,
                        x: x + ((width - text_w) / 2.0).max(0.0),
                        y: y + height + 2.0,
                        color: Color::rgb(0.3, 0.3, 0.3),
                    });

                    Ok(Size::new(*width, height + 12.0))
                } else {
                    Ok(Size::new(*width, *height))
                }
            }

            ComponentAst::PageNumber { format, alignment, .. } => {
                let page_text = format
                    .replace("{page}", &ctx.page.to_string())
                    .replace("{total}", &ctx.total_pages.to_string());
                let text_w = helvetica_width(&page_text, 8.5, false);
                let text_x = match alignment.as_str() {
                    "left" => x,
                    "center" => x + (available_w - text_w) / 2.0,
                    _ => x + (available_w - text_w),
                };

                ops.push(PdfOp::Text {
                    text: page_text,
                    font_ref: "/F1".to_string(),
                    size: 8.5,
                    x: text_x,
                    y,
                    color: Color::rgb(0.4, 0.45, 0.55),
                });

                Ok(Size::new(available_w, 12.0))
            }

            ComponentAst::Image { source, width, height, fit, alignment } => {
                let Some((alias, img)) = ctx.image(&interpolate_string(source, ctx.data)) else {
                    // Fuente ilegible o formato no soportado: marcador en su lugar
                    let w = width.unwrap_or(120.0);
                    let h = height.unwrap_or(40.0);
                    ops.push(PdfOp::RectStroke {
                        rect: Rect::new(x, y, w, h),
                        thickness: 1.0,
                        color: Color::rgb(0.8, 0.8, 0.8),
                    });
                    ops.push(PdfOp::Text {
                        text: "[Image]".to_string(),
                        font_ref: "/F1".to_string(),
                        size: 9.0,
                        x: x + 10.0,
                        y: y + (h / 2.0) - 4.0,
                        color: Color::rgb(0.5, 0.5, 0.5),
                    });
                    return Ok(Size::new(w, h));
                };

                let ratio = img.width as f32 / img.height as f32;
                // Caja de la imagen: lo pedido; si falta una medida sale de la proporción; sin medidas, el
                // tamaño natural (1 px = 0.75 pt) sin pasar del ancho disponible
                let (box_w, box_h) = match (width, height) {
                    (Some(w), Some(h)) => (*w, *h),
                    (Some(w), None) => (*w, w / ratio),
                    (None, Some(h)) => (h * ratio, *h),
                    (None, None) => {
                        let w = (img.width as f32 * 0.75).min(available_w);
                        (w, w / ratio)
                    }
                };

                let box_x = match alignment.as_deref().unwrap_or("center") {
                    "left" => x,
                    "right" => x + (available_w - box_w).max(0.0),
                    _ => x + ((available_w - box_w) / 2.0).max(0.0),
                };
                let caja = Rect::new(box_x, y, box_w, box_h);

                let (draw, clip) = match fit.as_deref().unwrap_or("contain") {
                    "fill" => (caja, None),
                    "cover" => {
                        let (w, h) = if box_w / box_h > ratio { (box_w, box_w / ratio) } else { (box_h * ratio, box_h) };
                        (Rect::new(box_x + (box_w - w) / 2.0, y + (box_h - h) / 2.0, w, h), Some(caja))
                    }
                    _ => {
                        let (w, h) = if box_w / box_h > ratio { (box_h * ratio, box_h) } else { (box_w, box_w / ratio) };
                        (Rect::new(box_x + (box_w - w) / 2.0, y + (box_h - h) / 2.0, w, h), None)
                    }
                };

                ops.push(PdfOp::Image { alias, rect: draw, clip });
                Ok(Size::new(box_w, box_h))
            }

            ComponentAst::Chart {
                chart_type,
                title,
                width,
                height,
                categories,
                series,
                show_legend,
                show_grid,
                show_values,
                theme,
            } => {
                let chart_w = width.unwrap_or(available_w);
                let (chart_ops, size) = ChartRenderer::render(
                    chart_type,
                    title.as_deref(),
                    x,
                    y,
                    chart_w,
                    *height,
                    categories.as_deref(),
                    series,
                    *show_legend,
                    *show_grid,
                    *show_values,
                    theme,
                );
                ops.extend(chart_ops);
                Ok(size)
            }
        }
    }

    /// Estilo, fuente y líneas de un texto para un ancho dado.
    fn layout_text(&self, comp: &ComponentAst, ctx: &mut RenderCtx, available_w: f32) -> TextLayout {
        let ComponentAst::Text { value, style, font, alignment, color, font_size, bold, .. } = comp else {
            unreachable!("layout_text solo recibe textos");
        };

        let interpolated = interpolate_string(value, ctx.data);
        let (default_font_name, default_size, default_color) = match style.as_deref() {
            Some("h1") => ("Helvetica-Bold", 22.0, Color::rgb(0.1, 0.1, 0.2)),
            Some("h2") => ("Helvetica-Bold", 16.0, Color::rgb(0.12, 0.23, 0.54)),
            Some("h3") => ("Helvetica-Bold", 12.0, Color::rgb(0.12, 0.23, 0.54)),
            Some("caption") => ("Helvetica", 8.0, Color::rgb(0.4, 0.45, 0.55)),
            _ => ("Helvetica", 10.0, Color::rgb(0.15, 0.15, 0.15)),
        };

        let is_bold = bold.unwrap_or(default_font_name.contains("Bold"));
        let size = font_size.unwrap_or(default_size);
        let text_color = color.as_deref().map(Color::from_hex).unwrap_or(default_color);
        let align = alignment.as_deref().unwrap_or("left");

        // Fuente personalizada (del documento o global) o estándar Type1
        let custom_font = font.as_ref().and_then(|font_name| {
            let lower = font_name.to_lowercase();
            if let Some((alias, cf)) = ctx.fonts.get(&lower) {
                Some((alias.clone(), cf.clone()))
            } else if let Some(gf) = get_global_font(font_name) {
                let alias = format!("/FC{}", ctx.font_counter);
                ctx.font_counter += 1;
                ctx.fonts.insert(lower, (alias.clone(), gf.clone()));
                Some((alias, gf))
            } else {
                None
            }
        });

        let (font_ref, custom) = match custom_font {
            Some((alias, cf)) => (alias, Some(cf)),
            None => ((if is_bold { "/F2" } else { "/F1" }).to_string(), None),
        };

        let measure = |s: &str| -> f32 {
            match &custom {
                Some(cf) => cf.measure_text_width(s, size),
                None => helvetica_width(s, size, is_bold),
            }
        };

        let mut lines = wrap_words(&interpolated, available_w, &measure);
        if lines.is_empty() {
            lines.push(interpolated);
        }

        let lines = lines
            .into_iter()
            .map(|line| {
                let line_w = measure(&line);
                let dx = match align {
                    "center" => ((available_w - line_w) / 2.0).max(0.0),
                    "right" => (available_w - line_w).max(0.0),
                    _ => 0.0,
                };
                (line, dx)
            })
            .collect();

        TextLayout { lines, font_ref, size, color: text_color, line_height: size * 1.35 }
    }

    /// Anchos de columna, líneas de cada celda y alto de cada fila (las celdas parten su texto). Las
    /// columnas `auto` miden su contenido con las métricas reales; las de `width` son fijas y las demás
    /// reparten lo que queda según su `flex`. Con `group_by` se intercala un título por grupo.
    fn layout_table(&self, comp: &ComponentAst, ctx: &RenderCtx, available_w: f32) -> TableLayout {
        let ComponentAst::Table {
            columns,
            source,
            data: inline_data,
            header_background,
            zebra,
            border_color,
            border_width,
            repeat_header,
            font_size,
            padding_x,
            padding_y,
            header_color,
            text_color,
            zebra_color,
            group_by,
            group_background,
            group_color,
        } = comp
        else {
            unreachable!("layout_table solo recibe tablas");
        };

        let rows: Vec<HashMap<String, Value>> = if let Some(items) = inline_data {
            items.clone()
        } else if let (Some(src_key), Some(d)) = (source, ctx.data) {
            d.get(src_key)
                .and_then(|v| v.as_array())
                .map(|arr| {
                    arr.iter()
                        .filter_map(|row_val| {
                            row_val.as_object().map(|obj| obj.iter().map(|(k, v)| (k.clone(), v.clone())).collect())
                        })
                        .collect()
                })
                .unwrap_or_default()
        } else {
            Vec::new()
        };

        let size = font_size.unwrap_or(TABLE_FONT_SIZE);
        let line_h = size * 1.35;
        let pad_x = padding_x.unwrap_or(TABLE_PAD_X);
        let pad_y = padding_y.unwrap_or(TABLE_PAD_Y);
        // Las alturas mínimas de siempre solo con la letra y el relleno por defecto
        let (header_min, row_min) = if font_size.is_none() && padding_y.is_none() {
            (TABLE_HEADER_MIN_H, TABLE_ROW_MIN_H)
        } else {
            (0.0, 0.0)
        };

        // Texto de cada celda, ya con su formato
        let values: Vec<Vec<String>> = rows
            .iter()
            .map(|row_data| {
                columns
                    .iter()
                    .map(|col| {
                        col.field
                            .as_ref()
                            .and_then(|f| row_data.get(f))
                            .map(|v| format_value(v, col.format.as_deref()))
                            .unwrap_or_default()
                    })
                    .collect()
            })
            .collect();

        // Anchos: auto según el texto más ancho (cabecera en negrita incluida), fijos, y el resto flexible
        let natural: Vec<Option<f32>> = columns
            .iter()
            .enumerate()
            .map(|(i, col)| {
                col.auto.then(|| {
                    let cells = values.iter().map(|v| helvetica_width(&v[i], size, false));
                    let widest = cells.fold(helvetica_width(&col.title, size, true), f32::max);
                    (widest + pad_x * 2.0).ceil()
                })
            })
            .collect();
        let fixed_w: f32 = columns.iter().zip(&natural).filter(|(_, n)| n.is_none()).filter_map(|(c, _)| c.width).sum();
        let total_flex: f32 = columns
            .iter()
            .zip(&natural)
            .filter(|(c, n)| n.is_none() && c.width.is_none())
            .map(|(c, _)| c.flex.unwrap_or(1.0))
            .sum();
        let auto_w: f32 = natural.iter().flatten().sum();
        // Si lo automático no cabe, se reduce en proporción (dejando a las flexibles al menos un cuarto)
        let auto_max = (available_w - fixed_w - if total_flex > 0.0 { available_w * 0.25 } else { 0.0 }).max(0.0);
        let auto_scale = if auto_w > auto_max && auto_w > 0.0 { auto_max / auto_w } else { 1.0 };
        let remaining_w = (available_w - fixed_w - auto_w * auto_scale).max(0.0);
        let flex_unit = if total_flex > 0.0 { remaining_w / total_flex } else { 0.0 };
        let col_widths: Vec<f32> = columns
            .iter()
            .zip(&natural)
            .map(|(c, n)| match n {
                Some(w) => w * auto_scale,
                None => c.width.unwrap_or_else(|| c.flex.unwrap_or(1.0) * flex_unit),
            })
            .collect();

        let header: Vec<Vec<String>> = columns
            .iter()
            .zip(&col_widths)
            .map(|(col, w)| wrap_cell(&col.title, *w, true, size, pad_x))
            .collect();
        let header_lines = header.iter().map(Vec::len).max().unwrap_or(1).max(1);
        let header_h = (header_lines as f32 * line_h + pad_y * 2.0).max(header_min);

        let mut table_rows = Vec::with_capacity(values.len());
        let mut current_group: Option<String> = None;
        let mut alt = false;
        for (row_data, row_values) in rows.iter().zip(values) {
            if let Some(field) = group_by {
                let group = row_data.get(field).map(|v| format_value(v, None)).unwrap_or_default();
                if current_group.as_ref() != Some(&group) {
                    let lines = wrap_cell(&group, available_w, true, size, pad_x);
                    let h = lines.len() as f32 * line_h + pad_y * 2.0;
                    table_rows.push(TableRow::Group { lines, h });
                    current_group = Some(group);
                    alt = false;
                }
            }
            let cells: Vec<Vec<String>> = row_values
                .iter()
                .zip(&col_widths)
                .map(|(value, w)| wrap_cell(value, *w, false, size, pad_x))
                .collect();
            let lines = cells.iter().map(Vec::len).max().unwrap_or(1).max(1);
            let h = (lines as f32 * line_h + pad_y * 2.0).max(row_min);
            table_rows.push(TableRow::Data { cells, h, alt });
            alt = !alt;
        }

        TableLayout {
            col_widths,
            aligns: columns.iter().map(|c| c.align.clone()).collect(),
            header,
            header_h,
            header_bg: header_background.as_deref().map(Color::from_hex).unwrap_or(Color::rgb(0.12, 0.23, 0.54)),
            header_color: header_color.as_deref().map(Color::from_hex).unwrap_or(Color::white()),
            rows: table_rows,
            zebra: zebra.then(|| zebra_color.as_deref().map(Color::from_hex).unwrap_or(Color::rgb(0.96, 0.97, 0.98))),
            border: border_color.as_deref().map(|c| (Color::from_hex(c), border_width.unwrap_or(0.5))),
            repeat_header: *repeat_header,
            font_size: size,
            line_h,
            pad_x,
            pad_y,
            text_color: text_color.as_deref().map(Color::from_hex).unwrap_or(Color::rgb(0.15, 0.15, 0.15)),
            group_bg: group_background.as_deref().map(Color::from_hex).unwrap_or(Color::rgb(0.94, 0.96, 0.98)),
            group_color: group_color.as_deref().map(Color::from_hex).unwrap_or(Color::rgb(0.12, 0.23, 0.54)),
        }
    }

    fn draw_table_header(&self, t: &TableLayout, x: f32, y: f32, available_w: f32, ops: &mut Vec<PdfOp>) {
        ops.push(PdfOp::RectFill {
            rect: Rect::new(x, y, available_w, t.header_h),
            color: t.header_bg,
        });
        self.draw_cells(t, &t.header, x, y, true, t.header_color, ops);
    }

    fn draw_table_row(&self, t: &TableLayout, idx: usize, x: f32, y: f32, available_w: f32, ops: &mut Vec<PdfOp>) {
        match &t.rows[idx] {
            TableRow::Group { lines, h } => {
                ops.push(PdfOp::RectFill { rect: Rect::new(x, y, available_w, *h), color: t.group_bg });
                for (l_idx, line) in lines.iter().enumerate() {
                    ops.push(PdfOp::Text {
                        text: line.clone(),
                        font_ref: "/F2".to_string(),
                        size: t.font_size,
                        x: x + t.pad_x,
                        y: y + t.pad_y + l_idx as f32 * t.line_h,
                        color: t.group_color,
                    });
                }
                if let Some((color, thickness)) = t.border {
                    ops.push(PdfOp::Line { x1: x, y1: y + h, x2: x + available_w, y2: y + h, thickness, color });
                }
            }
            TableRow::Data { cells, h, alt } => {
                if let (Some(color), true) = (t.zebra, *alt) {
                    ops.push(PdfOp::RectFill { rect: Rect::new(x, y, available_w, *h), color });
                }
                if let Some((color, thickness)) = t.border {
                    ops.push(PdfOp::Line { x1: x, y1: y + h, x2: x + available_w, y2: y + h, thickness, color });
                }
                self.draw_cells(t, cells, x, y, false, t.text_color, ops);
            }
        }
    }

    #[allow(clippy::too_many_arguments)]
    fn draw_cells(&self, t: &TableLayout, cells: &[Vec<String>], x: f32, y: f32, bold: bool, color: Color, ops: &mut Vec<PdfOp>) {
        let mut cell_x = x;
        for (c_idx, lines) in cells.iter().enumerate() {
            let w = t.col_widths[c_idx];
            for (l_idx, line) in lines.iter().enumerate() {
                let line_w = helvetica_width(line, t.font_size, bold);
                let text_x = match t.aligns[c_idx].as_deref() {
                    Some("right") => cell_x + w - t.pad_x - line_w,
                    Some("center") => cell_x + (w - line_w) / 2.0,
                    _ => cell_x + t.pad_x,
                };
                ops.push(PdfOp::Text {
                    text: line.clone(),
                    font_ref: (if bold { "/F2" } else { "/F1" }).to_string(),
                    size: t.font_size,
                    x: text_x,
                    y: y + t.pad_y + l_idx as f32 * t.line_h,
                    color,
                });
            }
            cell_x += w;
        }
    }

    fn build_pdf(&self, page_w: f32, page_h: f32, pages: Vec<Vec<PdfOp>>, ctx: RenderCtx) -> Result<Vec<u8>, String> {
        let mut doc = Document::with_version("1.4");
        let pages_id = doc.new_object_id();

        let font1_id = doc.add_object(dictionary! {
            "Type" => "Font",
            "Subtype" => "Type1",
            "BaseFont" => "Helvetica",
            "Encoding" => "WinAnsiEncoding",
        });

        let font2_id = doc.add_object(dictionary! {
            "Type" => "Font",
            "Subtype" => "Type1",
            "BaseFont" => "Helvetica-Bold",
            "Encoding" => "WinAnsiEncoding",
        });

        let mut font_dict = dictionary! {
            "F1" => font1_id,
            "F2" => font2_id,
        };

        // Fuentes personalizadas cargadas en el documento
        for (_name, (alias, custom_font)) in ctx.fonts {
            let font_id = custom_font.add_to_pdf_document(&mut doc)?;
            font_dict.set(alias.trim_start_matches('/'), font_id);
        }

        let mut resources = dictionary! {
            "Font" => font_dict,
        };

        // Imágenes: un XObject por fuente, compartido por todas las páginas
        let mut xobjects = lopdf::Dictionary::new();
        for entry in &ctx.images {
            if let Some(img) = &entry.image {
                let id = add_image(&mut doc, img)?;
                xobjects.set(entry.alias.trim_start_matches('/'), id);
            }
        }
        if !xobjects.is_empty() {
            resources.set("XObject", xobjects);
        }
        let resources_id = doc.add_object(resources);

        let mut kids: Vec<Object> = Vec::with_capacity(pages.len());
        for ops in pages {
            let content_id = doc.add_object(Stream::new(dictionary! {}, page_content(page_h, ops)));
            let page_id = doc.add_object(dictionary! {
                "Type" => "Page",
                "Parent" => pages_id,
                "MediaBox" => vec![0.into(), 0.into(), page_w.into(), page_h.into()],
                "Contents" => content_id,
                "Resources" => resources_id,
            });
            kids.push(page_id.into());
        }

        let count = kids.len() as i64;
        doc.objects.insert(
            pages_id,
            Object::Dictionary(dictionary! {
                "Type" => "Pages",
                "Kids" => kids,
                "Count" => count,
            }),
        );

        let catalog_id = doc.add_object(dictionary! {
            "Type" => "Catalog",
            "Pages" => pages_id,
        });
        doc.trailer.set("Root", catalog_id);

        let mut buffer = Vec::new();
        doc.save_to(&mut buffer).map_err(|e| e.to_string())?;
        Ok(buffer)
    }
}

impl Default for PdfEngine {
    fn default() -> Self {
        Self::new()
    }
}

/// Flujo de contenido de una página.
fn page_content(page_h: f32, ops: Vec<PdfOp>) -> Vec<u8> {
    let mut content_stream = Vec::new();
    for op in ops {
        match op {
            PdfOp::Text { text, font_ref, size, x, y, color } => {
                let pdf_y = page_h - y - size;
                let hex_str = crate::encoding::unicode_to_winansi_hex(&text);
                writeln!(
                    content_stream,
                    "BT {font_ref} {size} Tf {r:.3} {g:.3} {b:.3} rg 1 0 0 1 {x:.2} {pdf_y:.2} Tm {hex_str} Tj ET",
                    r = color.r,
                    g = color.g,
                    b = color.b,
                )
                .unwrap();
            }
            PdfOp::Line { x1, y1, x2, y2, thickness, color } => {
                let pdf_y1 = page_h - y1;
                let pdf_y2 = page_h - y2;
                writeln!(
                    content_stream,
                    "q {thickness} w {r:.3} {g:.3} {b:.3} RG {x1:.2} {pdf_y1:.2} m {x2:.2} {pdf_y2:.2} l S Q",
                    r = color.r,
                    g = color.g,
                    b = color.b,
                )
                .unwrap();
            }
            PdfOp::RectFill { rect, color } => {
                let pdf_y = page_h - rect.y - rect.height;
                writeln!(
                    content_stream,
                    "q {r:.3} {g:.3} {b:.3} rg {x:.2} {pdf_y:.2} {w:.2} {h:.2} re f Q",
                    r = color.r,
                    g = color.g,
                    b = color.b,
                    x = rect.x,
                    w = rect.width,
                    h = rect.height,
                )
                .unwrap();
            }
            PdfOp::RectStroke { rect, thickness, color } => {
                let pdf_y = page_h - rect.y - rect.height;
                writeln!(
                    content_stream,
                    "q {thickness} w {r:.3} {g:.3} {b:.3} RG {x:.2} {pdf_y:.2} {w:.2} {h:.2} re s Q",
                    r = color.r,
                    g = color.g,
                    b = color.b,
                    x = rect.x,
                    w = rect.width,
                    h = rect.height,
                )
                .unwrap();
            }
            PdfOp::Image { alias, rect, clip } => {
                let pdf_y = page_h - rect.y - rect.height;
                let recorte = clip
                    .map(|c| format!("{:.2} {:.2} {:.2} {:.2} re W n ", c.x, page_h - c.y - c.height, c.width, c.height))
                    .unwrap_or_default();
                writeln!(
                    content_stream,
                    "q {recorte}{w:.2} 0 0 {h:.2} {x:.2} {pdf_y:.2} cm {alias} Do Q",
                    w = rect.width,
                    h = rect.height,
                    x = rect.x,
                )
                .unwrap();
            }
        }
    }
    content_stream
}

/// Escribe la imagen como XObject (con su máscara de transparencia, si tiene).
fn add_image(doc: &mut Document, img: &PdfImage) -> Result<ObjectId, String> {
    let mut dict = dictionary! {
        "Type" => "XObject",
        "Subtype" => "Image",
        "Width" => img.width as i64,
        "Height" => img.height as i64,
        "ColorSpace" => img.color_space,
        "BitsPerComponent" => 8,
    };
    if img.invert_cmyk {
        dict.set("Decode", vec![1.into(), 0.into(), 1.into(), 0.into(), 1.into(), 0.into(), 1.into(), 0.into()]);
    }

    if let Some(alpha) = &img.alpha {
        let mut mask = Stream::new(
            dictionary! {
                "Type" => "XObject",
                "Subtype" => "Image",
                "Width" => img.width as i64,
                "Height" => img.height as i64,
                "ColorSpace" => "DeviceGray",
                "BitsPerComponent" => 8,
            },
            alpha.clone(),
        );
        mask.compress().map_err(|e| e.to_string())?;
        dict.set("SMask", doc.add_object(mask));
    }

    let stream = if img.is_jpeg {
        dict.set("Filter", "DCTDecode");
        let mut s = Stream::new(dict, img.data.clone());
        s.allows_compression = false;
        s
    } else {
        let mut s = Stream::new(dict, img.data.clone());
        s.compress().map_err(|e| e.to_string())?;
        s
    };
    Ok(doc.add_object(stream))
}

/// Parte el texto por palabras para que cada línea quepa en `max_w`; una palabra más larga que la
/// línea se corta por caracteres.
fn wrap_words(text: &str, max_w: f32, measure: &dyn Fn(&str) -> f32) -> Vec<String> {
    let mut lines = Vec::new();
    let mut current = String::new();

    for word in text.split_whitespace() {
        let candidate = if current.is_empty() { word.to_string() } else { format!("{current} {word}") };
        if measure(&candidate) <= max_w || current.is_empty() && measure(word) <= max_w {
            current = candidate;
            continue;
        }
        if !current.is_empty() {
            lines.push(std::mem::take(&mut current));
        }
        // Palabra que no cabe ni sola: se corta
        let mut piece = String::new();
        for ch in word.chars() {
            piece.push(ch);
            if measure(&piece) > max_w && piece.chars().count() > 1 {
                piece.pop();
                lines.push(std::mem::take(&mut piece));
                piece.push(ch);
            }
        }
        current = piece;
    }
    if !current.is_empty() {
        lines.push(current);
    }
    lines
}

/// Líneas de una celda de tabla para su ancho (descontando el relleno).
fn wrap_cell(text: &str, col_w: f32, bold: bool, size: f32, pad_x: f32) -> Vec<String> {
    let max_w = (col_w - pad_x * 2.0).max(size);
    let lines = wrap_words(text, max_w, &|s: &str| helvetica_width(s, size, bold));
    if lines.is_empty() {
        vec![String::new()]
    } else {
        lines
    }
}

pub enum PdfOp {
    Text { text: String, font_ref: String, size: f32, x: f32, y: f32, color: Color },
    Line { x1: f32, y1: f32, x2: f32, y2: f32, thickness: f32, color: Color },
    RectFill { rect: Rect, color: Color },
    RectStroke { rect: Rect, thickness: f32, color: Color },
    /// Imagen registrada (`alias` = `/ImN`) dibujada en `rect`; `clip` la recorta (ajuste `cover`).
    Image { alias: String, rect: Rect, clip: Option<Rect> },
}

impl PdfOp {
    /// La misma operación desplazada `dy` hacia abajo (para colocar un bloque ya dibujado).
    fn translate(self, dy: f32) -> Self {
        let mover = |r: Rect| Rect::new(r.x, r.y + dy, r.width, r.height);
        match self {
            PdfOp::Text { text, font_ref, size, x, y, color } => PdfOp::Text { text, font_ref, size, x, y: y + dy, color },
            PdfOp::Line { x1, y1, x2, y2, thickness, color } => PdfOp::Line { x1, y1: y1 + dy, x2, y2: y2 + dy, thickness, color },
            PdfOp::RectFill { rect, color } => PdfOp::RectFill { rect: mover(rect), color },
            PdfOp::RectStroke { rect, thickness, color } => PdfOp::RectStroke { rect: mover(rect), thickness, color },
            PdfOp::Image { alias, rect, clip } => PdfOp::Image { alias, rect: mover(rect), clip: clip.map(mover) },
        }
    }
}

fn interpolate_string(text: &str, data: Option<&Value>) -> String {
    let mut result = text.to_string();
    if let Some(val) = data {
        if let Some(obj) = val.as_object() {
            for (k, v) in obj {
                let pattern = format!("{{{{ {} }}}}", k);
                let v_str = match v {
                    Value::String(s) => s.clone(),
                    Value::Number(n) => n.to_string(),
                    Value::Bool(b) => b.to_string(),
                    _ => v.to_string(),
                };
                result = result.replace(&pattern, &v_str);

                if let Some(nested_obj) = v.as_object() {
                    for (nk, nv) in nested_obj {
                        let nested_pat = format!("{{{{ {}.{} }}}}", k, nk);
                        let nv_str = match nv {
                            Value::String(s) => s.clone(),
                            Value::Number(n) => n.to_string(),
                            _ => nv.to_string(),
                        };
                        result = result.replace(&nested_pat, &nv_str);
                    }
                }
            }
        }
    }
    result
}

fn format_value(val: &Value, format: Option<&str>) -> String {
    match format {
        Some("currency") => {
            if let Some(n) = val.as_f64() {
                format!("${:.2}", n)
            } else {
                val.to_string()
            }
        }
        Some("number") => {
            if let Some(n) = val.as_f64() {
                format!("{:.2}", n)
            } else {
                val.to_string()
            }
        }
        Some("percentage") => {
            if let Some(n) = val.as_f64() {
                format!("{:.1}%", n)
            } else {
                val.to_string()
            }
        }
        _ => match val {
            Value::String(s) => s.clone(),
            _ => val.to_string(),
        },
    }
}
