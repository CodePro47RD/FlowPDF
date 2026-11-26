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

        // 1. Configuración de página y márgenes según el AST
        if doc_ast.page.orientation.to_lowercase() == "landscape" {
            worksheet.set_landscape();
        } else {
            worksheet.set_portrait();
        }

        match doc_ast.page.size.to_uppercase().as_str() {
            "LETTER" => { worksheet.set_paper_size(1); }
            "LEGAL" => { worksheet.set_paper_size(5); }
            _ => { worksheet.set_paper_size(9); } // A4 por defecto
        };

        let margin_top_in = (doc_ast.page.margin_top.unwrap_or(doc_ast.page.margin) / 72.0) as f64;
        let margin_bottom_in = (doc_ast.page.margin_bottom.unwrap_or(doc_ast.page.margin) / 72.0) as f64;
        let margin_left_in = (doc_ast.page.margin_left.unwrap_or(doc_ast.page.margin) / 72.0) as f64;
        let margin_right_in = (doc_ast.page.margin_right.unwrap_or(doc_ast.page.margin) / 72.0) as f64;
        worksheet.set_margins(margin_left_in, margin_right_in, margin_top_in, margin_bottom_in, 0.3, 0.3);
        worksheet.set_screen_gridlines(true);

        // Estilos base
        let title_format = Format::new()
            .set_bold()
            .set_font_size(14.0)
            .set_font_color(XlsxColor::RGB(0x1E40AF));

        let regular_format = Format::new()
            .set_font_size(10.0)
            .set_font_color(XlsxColor::RGB(0x111827));

        // Determinar número de columnas estimado para cuadrícula armónica
        let estimated_cols = self.estimate_grid_cols(doc_ast);

        let mut current_row: u32 = 0;

        // 2. Encabezado del documento
        if let Some(header) = &doc_ast.header {
            current_row = self.render_component(header, worksheet, current_row, 0, estimated_cols, data, &title_format, &regular_format)?;
        }

        // 3. Contenido principal
        match &doc_ast.content {
            ContentAst::Single(comp) => {
                current_row = self.render_component(comp, worksheet, current_row, 0, estimated_cols, data, &title_format, &regular_format)?;
            }
            ContentAst::Multiple(items) => {
                for item in items {
                    current_row = self.render_component(item, worksheet, current_row, 0, estimated_cols, data, &title_format, &regular_format)?;
                }
            }
        }

        // 4. Pie de página del documento
        if let Some(footer) = &doc_ast.footer {
            let _ = self.render_component(footer, worksheet, current_row, 0, estimated_cols, data, &regular_format, &regular_format)?;
        }

        // 5. Marcas de agua flotantes
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

    fn estimate_grid_cols(&self, doc_ast: &DocumentDefinitionAst) -> u16 {
        let mut max_cols: u16 = 6;

        fn scan_comp(c: &ComponentAst, max_cols: &mut u16) {
            match c {
                ComponentAst::Table { columns, .. } => {
                    if columns.len() as u16 > *max_cols {
                        *max_cols = columns.len() as u16;
                    }
                }
                ComponentAst::Column { items, .. } => {
                    for it in items {
                        scan_comp(it, max_cols);
                    }
                }
                ComponentAst::Row { items, .. } => {
                    if items.len() as u16 > *max_cols {
                        *max_cols = items.len() as u16;
                    }
                    for it in items {
                        let c_inner = match it {
                            RowItemAst::Detailed { item, .. } => item,
                            RowItemAst::Simple(item) => item,
                        };
                        scan_comp(c_inner, max_cols);
                    }
                }
                ComponentAst::Container { child, .. } => {
                    if let Some(ch) = child {
                        scan_comp(ch, max_cols);
                    }
                }
                _ => {}
            }
        }

        if let Some(h) = &doc_ast.header {
            scan_comp(h, &mut max_cols);
        }
        match &doc_ast.content {
            ContentAst::Single(c) => scan_comp(c, &mut max_cols),
            ContentAst::Multiple(items) => {
                for it in items {
                    scan_comp(it, &mut max_cols);
                }
            }
        }
        if let Some(f) = &doc_ast.footer {
            scan_comp(f, &mut max_cols);
        }
        max_cols
    }

    fn render_component(
        &self,
        comp: &ComponentAst,
        worksheet: &mut Worksheet,
        mut row: u32,
        col: u16,
        max_cols: u16,
        data: Option<&Value>,
        title_format: &Format,
        regular_format: &Format,
    ) -> Result<u32, String> {
        match comp {
            ComponentAst::Text { value, style, bold, italic, font_size, color, alignment, .. } => {
                let interpolated = clean_cell_text(&interpolate_string(value, data));
                let mut fmt = Format::new();

                let is_bold = bold.unwrap_or(style.as_deref() == Some("h1") || style.as_deref() == Some("h2"));
                if is_bold {
                    fmt = fmt.set_bold();
                }
                if italic.unwrap_or(false) {
                    fmt = fmt.set_italic();
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

                if interpolated.contains('\n') {
                    fmt = fmt.set_text_wrap();
                }

                let align_str = alignment.as_deref().unwrap_or("left");
                match align_str {
                    "center" => {
                        fmt = fmt.set_align(FormatAlign::Center);
                        if max_cols > 1 {
                            worksheet.merge_range(row, col, row, col + max_cols - 1, &interpolated, &fmt)
                                .map_err(|e| e.to_string())?;
                        } else {
                            worksheet.write_string_with_format(row, col, &interpolated, &fmt)
                                .map_err(|e| e.to_string())?;
                        }
                    }
                    "right" => {
                        fmt = fmt.set_align(FormatAlign::Right);
                        let target_col = if max_cols > 1 { col + max_cols - 1 } else { col };
                        worksheet.write_string_with_format(row, target_col, &interpolated, &fmt)
                            .map_err(|e| e.to_string())?;
                    }
                    _ => {
                        fmt = fmt.set_align(FormatAlign::Left);
                        worksheet.write_string_with_format(row, col, &interpolated, &fmt)
                            .map_err(|e| e.to_string())?;
                    }
                }
                row += 1;
            }

            ComponentAst::Spacer { height } => {
                let h_pt = (*height as f64).max(2.0);
                let _ = worksheet.set_row_height(row, h_pt);
                row += 1;
            }

            ComponentAst::Divider { thickness, color, .. } => {
                let mut div_fmt = Format::new()
                    .set_border_bottom(if *thickness > 1.2 { FormatBorder::Medium } else { FormatBorder::Thin });
                if let Some(c) = color {
                    div_fmt = div_fmt.set_border_bottom_color(parse_xlsx_color(c));
                }

                let _ = worksheet.set_row_height(row, 4.0);
                let span = max_cols.max(1);
                for c in col..(col + span) {
                    let _ = worksheet.write_blank(row, c, &div_fmt);
                }
                row += 1;
            }

            ComponentAst::Column { items, .. } => {
                for item in items {
                    row = self.render_component(item, worksheet, row, col, max_cols, data, title_format, regular_format)?;
                }
            }

            ComponentAst::Row { items, .. } => {
                let count = items.len();
                if count == 0 {
                    return Ok(row);
                }
                if count == 1 {
                    let item_comp = match &items[0] {
                        RowItemAst::Detailed { item, .. } => item,
                        RowItemAst::Simple(item) => item,
                    };
                    return self.render_component(item_comp, worksheet, row, col, max_cols, data, title_format, regular_format);
                }

                let total_cols = max_cols.max(count as u16);
                let total_flex: f32 = items.iter().map(|it| match it {
                    RowItemAst::Detailed { flex, .. } => flex.unwrap_or(1.0),
                    RowItemAst::Simple(_) => 1.0,
                }).sum();

                let mut max_end_row = row;
                let mut current_col = col;

                for (idx, row_item) in items.iter().enumerate() {
                    let item_comp = match row_item {
                        RowItemAst::Detailed { item, .. } => item,
                        RowItemAst::Simple(item) => item,
                    };

                    let flex = match row_item {
                        RowItemAst::Detailed { flex, .. } => flex.unwrap_or(1.0),
                        RowItemAst::Simple(_) => 1.0,
                    };

                    let item_cols = if idx + 1 == count {
                        (col + total_cols).saturating_sub(current_col).max(1)
                    } else {
                        ((flex / total_flex.max(1.0)) * total_cols as f32).round().max(1.0) as u16
                    };

                    let end_row = self.render_component(item_comp, worksheet, row, current_col, item_cols, data, title_format, regular_format)?;
                    if end_row > max_end_row {
                        max_end_row = end_row;
                    }
                    current_col += item_cols;
                }
                row = max_end_row;
            }

            ComponentAst::Container { child, .. } => {
                if let Some(c) = child {
                    row = self.render_component(c, worksheet, row, col, max_cols, data, title_format, regular_format)?;
                }
            }

            ComponentAst::Image { source, width, height, .. } => {
                let interpolated_src = interpolate_string(source, data);
                if let Ok(bytes) = crate::image::load_source(&interpolated_src) {
                    if let Ok(mut img) = rust_xlsxwriter::Image::new_from_buffer(&bytes) {
                        if let Some(w) = width {
                            let img_w = (img.width() as f64).max(1.0);
                            let img_h = (img.height() as f64).max(1.0);
                            let scale_x = (*w as f64 * 1.33) / img_w;
                            let scale_y = (height.unwrap_or(*w) as f64 * 1.33) / img_h;
                            img = img.set_scale_width(scale_x).set_scale_height(scale_y);
                        }
                        let _ = worksheet.insert_image(row, col, &img);
                        let consumed_rows = (height.unwrap_or(40.0) / 20.0).max(1.0) as u32;
                        row += consumed_rows;
                    }
                }
            }

            ComponentAst::PageNumber { alignment, .. } => {
                let mut fmt = regular_format.clone();
                match alignment.as_str() {
                    "center" => { fmt = fmt.set_align(FormatAlign::Center); }
                    "right" => { fmt = fmt.set_align(FormatAlign::Right); }
                    _ => { fmt = fmt.set_align(FormatAlign::Left); }
                }
                let _ = worksheet.write_string_with_format(row, col, "Pág. 1 de 1", &fmt);
                row += 1;
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
                    .set_border(FormatBorder::Thin)
                    .set_text_wrap();

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
                for (col_idx, table_col) in columns.iter().enumerate() {
                    let col_u16 = col + (col_idx as u16);
                    let mut col_header_fmt = header_fmt.clone();
                    if let Some(align) = &table_col.align {
                        match align.as_str() {
                            "center" => { col_header_fmt = col_header_fmt.set_align(FormatAlign::Center); }
                            "right" => { col_header_fmt = col_header_fmt.set_align(FormatAlign::Right); }
                            _ => { col_header_fmt = col_header_fmt.set_align(FormatAlign::Left); }
                        }
                    }

                    worksheet.write_string_with_format(row, col_u16, &table_col.title, &col_header_fmt)
                        .map_err(|e| e.to_string())?;

                    if let Some(w) = table_col.width {
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

                            worksheet.write_string_with_format(row, col, &format!("▶ {}", grp_val), &grp_fmt)
                                .map_err(|e| e.to_string())?;

                            for c_i in 1..columns.len() {
                                let _ = worksheet.write_string_with_format(row, col + (c_i as u16), "", &grp_fmt);
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

                    for (col_idx, table_col) in columns.iter().enumerate() {
                        let col_u16 = col + (col_idx as u16);
                        let field_val = table_col.field.as_ref().and_then(|f| row_map.get(f));

                        let mut cell_fmt = base_cell_fmt.clone();
                        if let Some(align) = &table_col.align {
                            match align.as_str() {
                                "center" => { cell_fmt = cell_fmt.set_align(FormatAlign::Center); }
                                "right" => { cell_fmt = cell_fmt.set_align(FormatAlign::Right); }
                                _ => { cell_fmt = cell_fmt.set_align(FormatAlign::Left); }
                            }
                        }

                        // Multilínea automática con set_text_wrap
                        cell_fmt = cell_fmt.set_text_wrap();

                        match table_col.format.as_deref() {
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
                                let clean_val = clean_cell_text(&str_val);

                                worksheet.write_string_with_format(row, col_u16, &clean_val, &cell_fmt)
                                    .map_err(|e| e.to_string())?;
                            }
                        }
                    }
                    row += 1;
                }
            }

            _ => {
                // Componentes decorativos / gráficos opcionales
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

fn clean_cell_text(s: &str) -> String {
    s.replace('\t', " ")
     .lines()
     .map(|line| line.trim())
     .collect::<Vec<_>>()
     .join("\n")
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
