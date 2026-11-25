use std::collections::HashMap;
use rust_xlsxwriter::{Color as XlsxColor, Format, FormatAlign, FormatBorder, Workbook, Worksheet};
use serde_json::Value;

use crate::ast::*;

pub struct ExcelEngine;

impl ExcelEngine {
    pub fn new() -> Self {
        Self
    }

    pub fn render(&self, doc_ast: &DocumentDefinitionAst, data: Option<&Value>) -> Result<Vec<u8>, String> {
        let mut workbook = Workbook::new();
        let worksheet = workbook.add_worksheet();

        // Estilos
        let title_format = Format::new()
            .set_bold()
            .set_font_size(14.0)
            .set_font_color(XlsxColor::RGB(0x1E40AF));

        let regular_format = Format::new()
            .set_font_size(10.0)
            .set_font_color(XlsxColor::RGB(0x111827));

        let mut current_row: u32 = 0;

        // 1. Encabezado
        if let Some(header) = &doc_ast.header {
            current_row = self.render_component(header, worksheet, current_row, data, &title_format, &regular_format)?;
            current_row += 1;
        }

        // 2. Contenido principal
        match &doc_ast.content {
            ContentAst::Single(comp) => {
                current_row = self.render_component(comp, worksheet, current_row, data, &title_format, &regular_format)?;
            }
            ContentAst::Multiple(items) => {
                for item in items {
                    current_row = self.render_component(item, worksheet, current_row, data, &title_format, &regular_format)?;
                }
            }
        }

        // 3. Pie de página
        if let Some(footer) = &doc_ast.footer {
            current_row += 1;
            let _ = self.render_component(footer, worksheet, current_row, data, &regular_format, &regular_format)?;
        }

        // 4. Marcas de agua flotantes
        let watermarks = doc_ast.all_watermarks();
        for wm in &watermarks {
            let text = interpolate_string(&wm.text, data);
            if !text.is_empty() {
                // Header de impresión estándar para marcas de agua en Excel
                worksheet.set_header(&format!("&C&\"Helvetica-Bold,Bold\"&36&K888888 {}", text));

                // Marca de agua flotante textual sobre la cuadrícula
                let wm_format = Format::new()
                    .set_bold()
                    .set_font_size(wm.font_size.min(28.0))
                    .set_font_color(parse_xlsx_color(wm.color.as_deref().unwrap_or("#888888")))
                    .set_align(FormatAlign::Center);

                let target_row = if let Some(y) = wm.y {
                    (y / 20.0).max(0.0) as u32
                } else {
                    (current_row / 2).max(1)
                };
                let target_col = if let Some(x) = wm.x {
                    (x / 60.0).max(0.0) as u16
                } else {
                    1
                };

                let _ = worksheet.write_string_with_format(target_row, target_col, &text, &wm_format);
            }
        }

        worksheet.autofit();
        workbook.save_to_buffer().map_err(|e| format!("Excel generation error: {}", e))
    }

    fn render_component(
        &self,
        comp: &ComponentAst,
        worksheet: &mut Worksheet,
        mut row: u32,
        data: Option<&Value>,
        title_format: &Format,
        regular_format: &Format,
    ) -> Result<u32, String> {
        match comp {
            ComponentAst::Text { value, style, bold, font_size, color, alignment, .. } => {
                let interpolated = interpolate_string(value, data);
                let mut fmt = Format::new();

                let is_bold = bold.unwrap_or(style.as_deref() == Some("h1") || style.as_deref() == Some("h2"));
                if is_bold {
                    fmt = fmt.set_bold();
                }

                if let Some(fs) = font_size {
                    fmt = fmt.set_font_size(*fs);
                } else {
                    match style.as_deref() {
                        Some("h1") => { fmt = fmt.set_font_size(16.0); }
                        Some("h2") => { fmt = fmt.set_font_size(13.0); }
                        Some("h3") => { fmt = fmt.set_font_size(11.0); }
                        _ => { fmt = fmt.set_font_size(10.0); }
                    }
                }

                if let Some(c) = color {
                    fmt = fmt.set_font_color(parse_xlsx_color(c));
                }

                if let Some(align) = alignment {
                    match align.as_str() {
                        "center" => { fmt = fmt.set_align(FormatAlign::Center); }
                        "right" => { fmt = fmt.set_align(FormatAlign::Right); }
                        _ => { fmt = fmt.set_align(FormatAlign::Left); }
                    }
                }

                worksheet.write_string_with_format(row, 0, &interpolated, &fmt)
                    .map_err(|e| e.to_string())?;
                row += 1;
            }

            ComponentAst::Spacer { height } => {
                let empty_rows = (height / 15.0).max(1.0) as u32;
                row += empty_rows;
            }

            ComponentAst::Divider { .. } => {
                row += 1;
            }

            ComponentAst::Column { items, .. } => {
                for item in items {
                    row = self.render_component(item, worksheet, row, data, title_format, regular_format)?;
                }
            }

            ComponentAst::Row { items, .. } => {
                let mut col_offset: u16 = 0;
                for row_item in items {
                    let item_comp = match row_item {
                        RowItemAst::Detailed { item, .. } => item,
                        RowItemAst::Simple(item) => item,
                    };
                    if let ComponentAst::Text { value, bold, .. } = item_comp {
                        let interpolated = interpolate_string(value, data);
                        let mut fmt = regular_format.clone();
                        if bold.unwrap_or(false) {
                            fmt = fmt.set_bold();
                        }
                        let _ = worksheet.write_string_with_format(row, col_offset, &interpolated, &fmt);
                        col_offset += 2;
                    } else {
                        row = self.render_component(item_comp, worksheet, row, data, title_format, regular_format)?;
                    }
                }
                if col_offset > 0 {
                    row += 1;
                }
            }

            ComponentAst::Container { child, .. } => {
                if let Some(c) = child {
                    row = self.render_component(c, worksheet, row, data, title_format, regular_format)?;
                }
            }

            ComponentAst::Table {
                columns,
                source,
                data: table_data,
                header_background,
                header_color,
                zebra,
                zebra_color,
                text_color,
                group_by,
                group_background,
                group_color,
                ..
            } => {
                // Formato de cabecera de tabla
                let mut header_fmt = Format::new()
                    .set_bold()
                    .set_border(FormatBorder::Thin);

                if let Some(bg) = header_background {
                    header_fmt = header_fmt.set_background_color(parse_xlsx_color(bg));
                } else {
                    header_fmt = header_fmt.set_background_color(XlsxColor::RGB(0x1E40AF));
                }

                if let Some(tc) = header_color {
                    header_fmt = header_fmt.set_font_color(parse_xlsx_color(tc));
                } else {
                    header_fmt = header_fmt.set_font_color(XlsxColor::RGB(0xFFFFFF));
                }

                // Escribir cabeceras de columnas
                for (col_idx, col) in columns.iter().enumerate() {
                    let col_u16 = col_idx as u16;
                    worksheet.write_string_with_format(row, col_u16, &col.title, &header_fmt)
                        .map_err(|e| e.to_string())?;

                    if let Some(w) = col.width {
                        worksheet.set_column_width(col_u16, (w / 7.0).max(10.0))
                            .map_err(|e| e.to_string())?;
                    }
                }
                row += 1;

                // Extraer filas de datos
                let empty_vec = Vec::new();
                let rows_data: &Vec<HashMap<String, Value>> = if let Some(td) = table_data {
                    td
                } else {
                    &empty_vec
                };

                // Si viene de source en data
                let resolved_rows: Vec<HashMap<String, Value>> = if !rows_data.is_empty() {
                    rows_data.clone()
                } else if let Some(src) = source {
                    if let Some(val) = data {
                        if let Some(arr) = val.get(src).and_then(|v| v.as_array()) {
                            arr.iter().filter_map(|item| {
                                if let Some(obj) = item.as_object() {
                                    Some(obj.iter().map(|(k, v)| (k.clone(), v.clone())).collect())
                                } else {
                                    None
                                }
                            }).collect()
                        } else {
                            Vec::new()
                        }
                    } else {
                        Vec::new()
                    }
                } else {
                    Vec::new()
                };

                let mut current_group: Option<String> = None;

                for (r_idx, row_map) in resolved_rows.iter().enumerate() {
                    // Agrupación si group_by está configurado
                    if let Some(grp_field) = group_by {
                        let grp_val = row_map.get(grp_field)
                            .map(|v| match v {
                                Value::String(s) => s.clone(),
                                _ => v.to_string(),
                            })
                            .unwrap_or_default();

                        if current_group.as_deref() != Some(&grp_val) {
                            current_group = Some(grp_val.clone());

                            let mut grp_fmt = Format::new()
                                .set_bold()
                                .set_border(FormatBorder::Thin);

                            if let Some(gbg) = group_background {
                                grp_fmt = grp_fmt.set_background_color(parse_xlsx_color(gbg));
                            } else {
                                grp_fmt = grp_fmt.set_background_color(XlsxColor::RGB(0xE2E8F0));
                            }

                            if let Some(gc) = group_color {
                                grp_fmt = grp_fmt.set_font_color(parse_xlsx_color(gc));
                            } else {
                                grp_fmt = grp_fmt.set_font_color(XlsxColor::RGB(0x0F172A));
                            }

                            worksheet.write_string_with_format(row, 0, &format!("▶ {}", grp_val), &grp_fmt)
                                .map_err(|e| e.to_string())?;

                            for c_i in 1..columns.len() {
                                let _ = worksheet.write_string_with_format(row, c_i as u16, "", &grp_fmt);
                            }
                            row += 1;
                        }
                    }

                    // Formatos de celdas normales y zebra
                    let is_zebra_row = *zebra && (r_idx % 2 == 1);
                    let mut base_cell_fmt = Format::new().set_border(FormatBorder::Thin);

                    if is_zebra_row {
                        if let Some(zc) = zebra_color {
                            base_cell_fmt = base_cell_fmt.set_background_color(parse_xlsx_color(zc));
                        } else {
                            base_cell_fmt = base_cell_fmt.set_background_color(XlsxColor::RGB(0xF8FAFC));
                        }
                    }

                    if let Some(tc) = text_color {
                        base_cell_fmt = base_cell_fmt.set_font_color(parse_xlsx_color(tc));
                    }

                    for (col_idx, col) in columns.iter().enumerate() {
                        let col_u16 = col_idx as u16;
                        let field_val = col.field.as_ref().and_then(|f| row_map.get(f));

                        let mut cell_fmt = base_cell_fmt.clone();
                        if let Some(align) = &col.align {
                            match align.as_str() {
                                "center" => { cell_fmt = cell_fmt.set_align(FormatAlign::Center); }
                                "right" => { cell_fmt = cell_fmt.set_align(FormatAlign::Right); }
                                _ => { cell_fmt = cell_fmt.set_align(FormatAlign::Left); }
                            }
                        }

                        match col.format.as_deref() {
                            Some("currency") => {
                                cell_fmt = cell_fmt.set_num_format("$#,##0.00");
                                if let Some(n) = field_val.and_then(|v| v.as_f64().or_else(|| v.as_str().and_then(|s| s.trim_start_matches('$').trim().parse::<f64>().ok()))) {
                                    worksheet.write_number_with_format(row, col_u16, n, &cell_fmt)
                                        .map_err(|e| e.to_string())?;
                                } else {
                                    let s = field_val.map(|v| v.to_string()).unwrap_or_default();
                                    worksheet.write_string_with_format(row, col_u16, &s, &cell_fmt)
                                        .map_err(|e| e.to_string())?;
                                }
                            }
                            Some("number") => {
                                cell_fmt = cell_fmt.set_num_format("#,##0.00");
                                if let Some(n) = field_val.and_then(|v| v.as_f64().or_else(|| v.as_str().and_then(|s| s.parse::<f64>().ok()))) {
                                    worksheet.write_number_with_format(row, col_u16, n, &cell_fmt)
                                        .map_err(|e| e.to_string())?;
                                } else {
                                    let s = field_val.map(|v| v.to_string()).unwrap_or_default();
                                    worksheet.write_string_with_format(row, col_u16, &s, &cell_fmt)
                                        .map_err(|e| e.to_string())?;
                                }
                            }
                            Some("percentage") => {
                                cell_fmt = cell_fmt.set_num_format("0.0%");
                                if let Some(n) = field_val.and_then(|v| v.as_f64()) {
                                    worksheet.write_number_with_format(row, col_u16, n / 100.0, &cell_fmt)
                                        .map_err(|e| e.to_string())?;
                                } else {
                                    let s = field_val.map(|v| v.to_string()).unwrap_or_default();
                                    worksheet.write_string_with_format(row, col_u16, &s, &cell_fmt)
                                        .map_err(|e| e.to_string())?;
                                }
                            }
                            _ => {
                                let str_val = field_val.map(|v| match v {
                                    Value::String(s) => s.clone(),
                                    _ => v.to_string(),
                                }).unwrap_or_default();

                                worksheet.write_string_with_format(row, col_u16, &str_val, &cell_fmt)
                                    .map_err(|e| e.to_string())?;
                            }
                        }
                    }
                    row += 1;
                }
                row += 1; // Espacio posterior a la tabla
            }

            _ => {
                // Otros componentes (qr, barcode, chart, image) se representan con placeholder textual en Excel
            }
        }
        Ok(row)
    }
}

impl Default for ExcelEngine {
    fn default() -> Self {
        Self::new()
    }
}

fn parse_xlsx_color(hex: &str) -> XlsxColor {
    let clean = hex.trim_start_matches('#');
    if clean.len() >= 6 {
        if let Ok(num) = u32::from_str_radix(&clean[0..6], 16) {
            return XlsxColor::RGB(num);
        }
    }
    XlsxColor::RGB(0x000000)
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
