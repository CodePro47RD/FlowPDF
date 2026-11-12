use std::collections::HashMap;
use std::io::Write;
use lopdf::{dictionary, Document, Object, Stream};
use qrcode::QrCode;
use serde_json::Value;

use crate::ast::*;
use crate::barcode::Code128;
use crate::core::{Color, PageSize, Rect, Size};

pub struct PdfEngine {
    pub default_font_size: f32,
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
        let content_h = page_h - (margin_top + margin_bottom);

        // Resolver variables del template en el contenido
        let mut ops = Vec::new();

        // 1. Renderizar encabezado si existe
        let mut current_y = margin_top;
        if let Some(header) = &doc_ast.header {
            let h_size = self.render_component(header, data, margin_left, current_y, content_w, &mut ops)?;
            current_y += h_size.height + 10.0;
        }

        // 2. Renderizar contenido
        match &doc_ast.content {
            ContentAst::Single(comp) => {
                let c_size = self.render_component(comp, data, margin_left, current_y, content_w, &mut ops)?;
                current_y += c_size.height;
            }
            ContentAst::Multiple(items) => {
                for item in items {
                    let c_size = self.render_component(item, data, margin_left, current_y, content_w, &mut ops)?;
                    current_y += c_size.height + 6.0;
                }
            }
        }

        // 3. Renderizar pie de página si existe
        if let Some(footer) = &doc_ast.footer {
            let footer_y = page_h - margin_bottom - 20.0;
            self.render_component(footer, data, margin_left, footer_y, content_w, &mut ops)?;
        }

        // Compilar a documento PDF válido usando lopdf
        self.build_pdf(page_w, page_h, ops)
    }

    fn render_component(
        &self,
        comp: &ComponentAst,
        data: Option<&Value>,
        x: f32,
        y: f32,
        available_w: f32,
        ops: &mut Vec<PdfOp>,
    ) -> Result<Size, String> {
        match comp {
            ComponentAst::Text {
                value,
                style,
                alignment,
                color,
                font_size,
                bold,
                italic,
                underline,
            } => {
                let interpolated = interpolate_string(value, data);
                let (font_name, default_size, default_color) = match style.as_deref() {
                    Some("h1") => ("Helvetica-Bold", 22.0, Color::rgb(0.1, 0.1, 0.2)),
                    Some("h2") => ("Helvetica-Bold", 16.0, Color::rgb(0.12, 0.23, 0.54)),
                    Some("h3") => ("Helvetica-Bold", 12.0, Color::rgb(0.12, 0.23, 0.54)),
                    Some("caption") => ("Helvetica", 8.0, Color::rgb(0.4, 0.45, 0.55)),
                    _ => ("Helvetica", 10.0, Color::rgb(0.15, 0.15, 0.15)),
                };

                let is_bold = bold.unwrap_or(font_name.contains("Bold"));
                let actual_font = if is_bold { "Helvetica-Bold" } else { "Helvetica" };
                let size = font_size.unwrap_or(default_size);
                let text_color = color.as_deref().map(Color::from_hex).unwrap_or(default_color);
                let align = alignment.as_deref().unwrap_or("left");

                // Medición y ajuste de líneas
                let char_width = size * 0.52;
                let max_chars_per_line = ((available_w / char_width).floor() as usize).max(1);
                let words: Vec<&str> = interpolated.split_whitespace().collect();
                let mut lines = Vec::new();
                let mut current_line = String::new();

                for word in words {
                    if current_line.is_empty() {
                        current_line.push_str(word);
                    } else if current_line.len() + 1 + word.len() <= max_chars_per_line {
                        current_line.push(' ');
                        current_line.push_str(word);
                    } else {
                        lines.push(current_line);
                        current_line = word.to_string();
                    }
                }
                if !current_line.is_empty() {
                    lines.push(current_line);
                }

                if lines.is_empty() {
                    lines.push(interpolated);
                }

                let line_height = size * 1.35;
                let total_h = lines.len() as f32 * line_height;

                for (idx, line) in lines.iter().enumerate() {
                    let line_y = y + (idx as f32 * line_height);
                    let line_w = line.len() as f32 * char_width;

                    let draw_x = match align {
                        "center" => x + ((available_w - line_w) / 2.0).max(0.0),
                        "right" => x + (available_w - line_w).max(0.0),
                        _ => x,
                    };

                    ops.push(PdfOp::Text {
                        text: line.clone(),
                        font: actual_font.to_string(),
                        size,
                        x: draw_x,
                        y: line_y,
                        color: text_color,
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
                    let s = self.render_component(item, data, x, col_y, available_w, ops)?;
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

                    let s = self.render_component(comp, data, cur_x, y, w, ops)?;
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
                    self.render_component(c, data, draw_x + p, draw_y + p, target_w - (p * 2.0), &mut child_ops)?
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

            ComponentAst::Table {
                columns,
                source,
                data: inline_data,
                header_background,
                zebra,
                border_color,
                border_width,
                ..
            } => {
                let rows: Vec<HashMap<String, Value>> = if let Some(items) = inline_data {
                    items.clone()
                } else if let Some(src_key) = source {
                    if let Some(d) = data {
                        d.get(src_key)
                            .and_then(|v| v.as_array())
                            .map(|arr| {
                                arr.iter()
                                    .filter_map(|row_val| {
                                        row_val.as_object().map(|obj| {
                                            obj.iter().map(|(k, v)| (k.clone(), v.clone())).collect()
                                        })
                                    })
                                    .collect()
                            })
                            .unwrap_or_default()
                    } else {
                        Vec::new()
                    }
                } else {
                    Vec::new()
                };

                // Calcular anchos de columnas
                let total_cols = columns.len();
                let mut fixed_w = 0.0;
                let mut total_flex = 0.0;

                for col in columns {
                    if let Some(w) = col.width {
                        fixed_w += w;
                    } else {
                        total_flex += col.flex.unwrap_or(1.0);
                    }
                }

                let remaining_w = (available_w - fixed_w).max(0.0);
                let flex_unit = if total_flex > 0.0 { remaining_w / total_flex } else { 0.0 };

                let col_widths: Vec<f32> = columns
                    .iter()
                    .map(|c| c.width.unwrap_or_else(|| c.flex.unwrap_or(1.0) * flex_unit))
                    .collect();

                let mut current_table_y = y;
                let header_h = 24.0;

                // 1. Dibujar Cabecera
                let header_bg = header_background.as_deref().map(Color::from_hex).unwrap_or(Color::rgb(0.12, 0.23, 0.54));
                ops.push(PdfOp::RectFill {
                    rect: Rect::new(x, current_table_y, available_w, header_h),
                    color: header_bg,
                });

                let mut cell_x = x;
                for (idx, col) in columns.iter().enumerate() {
                    let w = col_widths[idx];
                    let text_x = match col.align.as_deref() {
                        Some("right") => cell_x + w - 8.0 - (col.title.len() as f32 * 5.0),
                        Some("center") => cell_x + (w - (col.title.len() as f32 * 5.0)) / 2.0,
                        _ => cell_x + 8.0,
                    };
                    ops.push(PdfOp::Text {
                        text: col.title.clone(),
                        font: "Helvetica-Bold".to_string(),
                        size: 9.0,
                        x: text_x,
                        y: current_table_y + 7.0,
                        color: Color::white(),
                    });
                    cell_x += w;
                }
                current_table_y += header_h;

                // 2. Dibujar Filas de Datos
                let row_h = 20.0;
                let zebra_color = Color::rgb(0.96, 0.97, 0.98);

                for (r_idx, row_data) in rows.iter().enumerate() {
                    if *zebra && r_idx % 2 == 1 {
                        ops.push(PdfOp::RectFill {
                            rect: Rect::new(x, current_table_y, available_w, row_h),
                            color: zebra_color,
                        });
                    }

                    // Línea inferior de la fila
                    if let Some(bc_hex) = border_color {
                        ops.push(PdfOp::Line {
                            x1: x,
                            y1: current_table_y + row_h,
                            x2: x + available_w,
                            y2: current_table_y + row_h,
                            thickness: border_width.unwrap_or(0.5),
                            color: Color::from_hex(bc_hex),
                        });
                    }

                    let mut cell_x = x;
                    for (c_idx, col) in columns.iter().enumerate() {
                        let w = col_widths[c_idx];
                        if let Some(field) = &col.field {
                            let val_str = if let Some(v) = row_data.get(field) {
                                format_value(v, col.format.as_deref())
                            } else {
                                String::new()
                            };

                            let text_w = val_str.len() as f32 * 4.8;
                            let text_x = match col.align.as_deref() {
                                Some("right") => cell_x + w - 8.0 - text_w,
                                Some("center") => cell_x + (w - text_w) / 2.0,
                                _ => cell_x + 8.0,
                            };

                            ops.push(PdfOp::Text {
                                text: val_str,
                                font: "Helvetica".to_string(),
                                size: 9.0,
                                x: text_x,
                                y: current_table_y + 5.5,
                                color: Color::rgb(0.15, 0.15, 0.15),
                            });
                        }
                        cell_x += w;
                    }
                    current_table_y += row_h;
                }

                Ok(Size::new(available_w, current_table_y - y))
            }

            ComponentAst::Qr { value, size, fill_color, .. } => {
                let interpolated = interpolate_string(value, data);
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
                let interpolated = interpolate_string(value, data);
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

                    // Texto del código debajo
                    let text_w = interpolated.len() as f32 * 5.0;
                    ops.push(PdfOp::Text {
                        text: interpolated,
                        font: "Helvetica".to_string(),
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
                let page_text = format.replace("{page}", "1").replace("{total}", "1");
                let text_w = page_text.len() as f32 * 4.5;
                let text_x = match alignment.as_str() {
                    "left" => x,
                    "center" => x + (available_w - text_w) / 2.0,
                    _ => x + (available_w - text_w),
                };

                ops.push(PdfOp::Text {
                    text: page_text,
                    font: "Helvetica".to_string(),
                    size: 8.5,
                    x: text_x,
                    y,
                    color: Color::rgb(0.4, 0.45, 0.55),
                });

                Ok(Size::new(available_w, 12.0))
            }

            ComponentAst::Image { width, height, .. } => {
                let w = width.unwrap_or(120.0);
                let h = height.unwrap_or(40.0);
                ops.push(PdfOp::RectStroke {
                    rect: Rect::new(x, y, w, h),
                    thickness: 1.0,
                    color: Color::rgb(0.8, 0.8, 0.8),
                });
                ops.push(PdfOp::Text {
                    text: "[Image]".to_string(),
                    font: "Helvetica".to_string(),
                    size: 9.0,
                    x: x + 10.0,
                    y: y + (h / 2.0) - 4.0,
                    color: Color::rgb(0.5, 0.5, 0.5),
                });
                Ok(Size::new(w, h))
            }
        }
    }

    fn build_pdf(&self, page_w: f32, page_h: f32, ops: Vec<PdfOp>) -> Result<Vec<u8>, String> {
        let mut doc = Document::with_version("1.4");
        let pages_id = doc.new_object_id();

        let mut content_stream = Vec::new();

        for op in ops {
            match op {
                PdfOp::Text { text, font, size, x, y, color } => {
                    let pdf_y = page_h - y - size;
                    let font_ref = if font.contains("Bold") { "/F2" } else { "/F1" };
                    let sanitized = text.replace('\\', "\\\\").replace('(', "\\(").replace(')', "\\)");

                    writeln!(
                        content_stream,
                        "BT {font_ref} {size} Tf {r:.3} {g:.3} {b:.3} rg 1 0 0 1 {x:.2} {pdf_y:.2} Tm ({sanitized}) Tj ET",
                        r = color.r,
                        g = color.g,
                        b = color.b,
                    ).unwrap();
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
                    ).unwrap();
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
                    ).unwrap();
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
                    ).unwrap();
                }
            }
        }

        let content_id = doc.add_object(Stream::new(dictionary! {}, content_stream));

        let font1_id = doc.add_object(dictionary! {
            "Type" => "Font",
            "Subtype" => "Type1",
            "BaseFont" => "Helvetica",
        });

        let font2_id = doc.add_object(dictionary! {
            "Type" => "Font",
            "Subtype" => "Type1",
            "BaseFont" => "Helvetica-Bold",
        });

        let resources_id = doc.add_object(dictionary! {
            "Font" => dictionary! {
                "F1" => font1_id,
                "F2" => font2_id,
            },
        });

        let page_id = doc.add_object(dictionary! {
            "Type" => "Page",
            "Parent" => pages_id,
            "MediaBox" => vec![0.into(), 0.into(), page_w.into(), page_h.into()],
            "Contents" => content_id,
            "Resources" => resources_id,
        });

        let pages_dict = dictionary! {
            "Type" => "Pages",
            "Kids" => vec![page_id.into()],
            "Count" => 1,
        };
        doc.objects.insert(pages_id, Object::Dictionary(pages_dict));

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

pub enum PdfOp {
    Text { text: String, font: String, size: f32, x: f32, y: f32, color: Color },
    Line { x1: f32, y1: f32, x2: f32, y2: f32, thickness: f32, color: Color },
    RectFill { rect: Rect, color: Color },
    RectStroke { rect: Rect, thickness: f32, color: Color },
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

                // Nested check
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
