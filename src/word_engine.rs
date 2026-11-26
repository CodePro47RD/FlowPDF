use std::collections::HashMap;
use std::io::Cursor;
use docx_rs::*;
use serde_json::Value;

use crate::ast::*;

enum DocxHeaderFooterItem {
    Paragraph(Paragraph),
    Table(Table),
}

pub struct WordEngine;

impl WordEngine {
    pub fn new() -> Self {
        Self
    }

    pub fn render(&self, doc_ast: &DocumentDefinitionAst, data: Option<&Value>) -> Result<Vec<u8>, String> {
        let mut doc = Docx::new();

        // 1. Configuración de página y márgenes
        let margin_val = (doc_ast.page.margin * 20.0) as i32; // conversión a dxa (twips: 1 pt = 20 dxa)
        let margin_top = doc_ast.page.margin_top.map(|v| (v * 20.0) as i32).unwrap_or(margin_val);
        let margin_bottom = doc_ast.page.margin_bottom.map(|v| (v * 20.0) as i32).unwrap_or(margin_val);
        let margin_left = doc_ast.page.margin_left.map(|v| (v * 20.0) as i32).unwrap_or(margin_val);
        let margin_right = doc_ast.page.margin_right.map(|v| (v * 20.0) as i32).unwrap_or(margin_val);

        let page_margin = PageMargin::new()
            .top(margin_top)
            .bottom(margin_bottom)
            .left(margin_left)
            .right(margin_right);
        doc = doc.page_margin(page_margin);

        // Dimensiones de página según PageSize compartido
        let (w_pt, h_pt) = crate::core::PageSize::from_str(&doc_ast.page.size).dimensions(&doc_ast.page.orientation);
        let w_dxa = (w_pt * 20.0).round() as u32;
        let h_dxa = (h_pt * 20.0).round() as u32;
        doc = doc.page_size(w_dxa, h_dxa);

        let usable_width_dxa = w_dxa.saturating_sub((margin_left + margin_right).max(0) as u32).max(1000);

        // 2. Encabezado de página
        if let Some(header) = &doc_ast.header {
            let mut header_obj = Header::new();
            for item in self.component_to_header_footer_items(header, data, usable_width_dxa)? {
                header_obj = match item {
                    DocxHeaderFooterItem::Paragraph(p) => header_obj.add_paragraph(p),
                    DocxHeaderFooterItem::Table(t) => header_obj.add_table(t),
                };
            }
            doc = doc.header(header_obj);
        }



        // 4. Contenido principal
        match &doc_ast.content {
            ContentAst::Single(comp) => {
                doc = self.render_component(comp, doc, usable_width_dxa, data)?;
            }
            ContentAst::Multiple(items) => {
                for item in items {
                    doc = self.render_component(item, doc, usable_width_dxa, data)?;
                }
            }
        }

        // 5. Pie de página
        if let Some(footer) = &doc_ast.footer {
            let mut footer_obj = Footer::new();
            for item in self.component_to_header_footer_items(footer, data, usable_width_dxa)? {
                footer_obj = match item {
                    DocxHeaderFooterItem::Paragraph(p) => footer_obj.add_paragraph(p),
                    DocxHeaderFooterItem::Table(t) => footer_obj.add_table(t),
                };
            }
            doc = doc.footer(footer_obj);
        }

        let mut buffer = Cursor::new(Vec::new());
        doc.build().pack(&mut buffer).map_err(|e| format!("Word generation error: {:?}", e))?;
        Ok(buffer.into_inner())
    }

    fn render_component(
        &self,
        comp: &ComponentAst,
        mut doc: Docx,
        usable_width_dxa: u32,
        data: Option<&Value>,
    ) -> Result<Docx, String> {
        match comp {
            ComponentAst::Text { value, style, bold, italic, font_size, color, alignment, .. } => {
                let interpolated = interpolate_string(value, data);
                let is_bold = bold.unwrap_or(style.as_deref() == Some("h1") || style.as_deref() == Some("h2"));
                let sz = font_size.map(|f| (f * 2.0) as usize).unwrap_or_else(|| {
                    match style.as_deref() {
                        Some("h1") => 32, // 16 pt
                        Some("h2") => 26, // 13 pt
                        Some("h3") => 22, // 11 pt
                        _ => 20,          // 10 pt
                    }
                });

                let mut p = Paragraph::new();
                if let Some(align) = alignment {
                    p = match align.as_str() {
                        "center" => p.align(AlignmentType::Center),
                        "right" => p.align(AlignmentType::Right),
                        _ => p.align(AlignmentType::Left),
                    };
                }

                let lines: Vec<&str> = interpolated.split('\n').collect();
                for (l_idx, line) in lines.iter().enumerate() {
                    let mut run = Run::new().add_text(*line);
                    if is_bold {
                        run = run.bold();
                    }
                    if italic.unwrap_or(false) {
                        run = run.italic();
                    }
                    run = run.size(sz);
                    if let Some(c) = color {
                        run = run.color(c.trim_start_matches('#'));
                    }
                    if l_idx + 1 < lines.len() {
                        run = run.add_break(BreakType::TextWrapping);
                    }
                    p = p.add_run(run);
                }

                doc = doc.add_paragraph(p);
            }

            ComponentAst::Spacer { height } => {
                let lines = (height / 15.0).max(1.0) as usize;
                for _ in 0..lines {
                    doc = doc.add_paragraph(Paragraph::new());
                }
            }

            ComponentAst::Divider { thickness, color, .. } => {
                let table = self.render_divider_table(*thickness, color.as_deref(), usable_width_dxa);
                doc = doc.add_table(table);
            }

            ComponentAst::Column { items, .. } => {
                for item in items {
                    doc = self.render_component(item, doc, usable_width_dxa, data)?;
                }
            }

            ComponentAst::Row { items, .. } => {
                let count = items.len();
                if count == 0 {
                    return Ok(doc);
                }
                if count == 1 {
                    let item_comp = match &items[0] {
                        RowItemAst::Detailed { item, .. } => item,
                        RowItemAst::Simple(item) => item,
                    };
                    return self.render_component(item_comp, doc, usable_width_dxa, data);
                }

                let table = self.render_row_to_table(items, data, usable_width_dxa)?;
                doc = doc.add_table(table);
            }

            ComponentAst::Container { child, .. } => {
                if let Some(c) = child {
                    doc = self.render_component(c, doc, usable_width_dxa, data)?;
                }
            }

            ComponentAst::Image { source, width, height, alignment, .. } => {
                let src = interpolate_string(source, data);
                if let Ok(bytes) = crate::image::load_source(&src) {
                    let w = (width.unwrap_or(120.0) * 15.0) as u32;
                    let h = (height.unwrap_or(40.0) * 15.0) as u32;
                    let pic = Pic::new(&bytes).size(w, h);
                    let mut p = Paragraph::new().add_run(Run::new().add_image(pic));
                    if let Some(align) = alignment {
                        p = match align.as_str() {
                            "center" => p.align(AlignmentType::Center),
                            "right" => p.align(AlignmentType::Right),
                            _ => p.align(AlignmentType::Left),
                        };
                    }
                    doc = doc.add_paragraph(p);
                }
            }

            ComponentAst::PageNumber { alignment, .. } => {
                let mut p = Paragraph::new().add_run(Run::new().add_text("Pág. 1 de 1").size(18));
                p = match alignment.as_str() {
                    "center" => p.align(AlignmentType::Center),
                    "right" => p.align(AlignmentType::Right),
                    _ => p.align(AlignmentType::Left),
                };
                doc = doc.add_paragraph(p);
            }

            ComponentAst::Table {
                columns,
                source,
                data: table_data,
                header_background,
                header_color,
                zebra,
                zebra_color,
                group_by,
                ..
            } => {
                let resolved_rows = resolve_table_rows(table_data, source.as_deref(), data);

                // Calcular anchos de columnas proporcionales al ancho útil
                let total_specified_w: f32 = columns.iter().map(|c| c.width.unwrap_or(80.0)).sum();
                let col_widths_dxa: Vec<usize> = columns.iter().map(|c| {
                    let ratio = c.width.unwrap_or(80.0) / total_specified_w.max(1.0);
                    (ratio * usable_width_dxa as f32) as usize
                }).collect();

                let mut table_rows: Vec<TableRow> = Vec::new();

                // 1. Fila de cabecera
                let mut header_cells: Vec<TableCell> = Vec::new();
                for (c_idx, col) in columns.iter().enumerate() {
                    let mut run = Run::new().add_text(&col.title).bold().size(18); // 9 pt
                    if let Some(tc) = header_color {
                        run = run.color(tc.trim_start_matches('#'));
                    } else {
                        run = run.color("FFFFFF");
                    }

                    let mut p = Paragraph::new().add_run(run);
                    if let Some(align) = &col.align {
                        p = match align.as_str() {
                            "center" => p.align(AlignmentType::Center),
                            "right" => p.align(AlignmentType::Right),
                            _ => p.align(AlignmentType::Left),
                        };
                    }

                    let col_w = col_widths_dxa[c_idx];
                    let mut cell = TableCell::new()
                        .width(col_w, WidthType::Dxa)
                        .add_paragraph(p);

                    if let Some(bg) = header_background {
                        cell = cell.shading(Shading::new().fill(bg.trim_start_matches('#')));
                    } else {
                        cell = cell.shading(Shading::new().fill("1E40AF"));
                    }

                    let top_b = TableCellBorder::new(TableCellBorderPosition::Top).size(4).color("CBD5E1").border_type(BorderType::Single);
                    let bot_b = TableCellBorder::new(TableCellBorderPosition::Bottom).size(6).color("94A3B8").border_type(BorderType::Single);
                    cell = cell.set_border(top_b).set_border(bot_b);

                    header_cells.push(cell);
                }
                table_rows.push(TableRow::new(header_cells));

                // 2. Filas de datos
                let mut current_group: Option<String> = None;
                for (r_idx, row_map) in resolved_rows.iter().enumerate() {
                    // Agrupación si aplica
                    if let Some(grp_field) = group_by {
                        let grp_val = row_map.get(grp_field)
                            .map(|v| match v {
                                Value::String(s) => s.clone(),
                                _ => v.to_string(),
                            })
                            .unwrap_or_default();

                        if current_group.as_deref() != Some(&grp_val) {
                            current_group = Some(grp_val.clone());

                            let grp_run = Run::new().add_text(&format!("▶ {}", grp_val)).bold().size(18);
                            let grp_cell = TableCell::new()
                                .add_paragraph(Paragraph::new().add_run(grp_run))
                                .shading(Shading::new().fill("E2E8F0"))
                                .grid_span(columns.len());
                            table_rows.push(TableRow::new(vec![grp_cell]));
                        }
                    }

                    let is_zebra = *zebra && (r_idx % 2 == 1);
                    let mut data_cells: Vec<TableCell> = Vec::new();

                    for (c_idx, col) in columns.iter().enumerate() {
                        let raw_str = format_cell_value(col.field.as_ref().and_then(|f| row_map.get(f)), col.format.as_deref());
                        let val_str = clean_word_text(&raw_str);

                        let mut p = Paragraph::new();
                        if let Some(align) = &col.align {
                            p = match align.as_str() {
                                "center" => p.align(AlignmentType::Center),
                                "right" => p.align(AlignmentType::Right),
                                _ => p.align(AlignmentType::Left),
                            };
                        }

                        // Soporte para texto multilínea con saltos de línea (como en horarios)
                        let lines: Vec<&str> = val_str.split('\n').filter(|l| !l.is_empty()).collect();
                        if lines.is_empty() {
                            p = p.add_run(Run::new().add_text("").size(18));
                        } else {
                            for (l_idx, line) in lines.iter().enumerate() {
                                let mut run = Run::new().add_text(*line).size(18);
                                if l_idx + 1 < lines.len() {
                                    run = run.add_break(BreakType::TextWrapping);
                                }
                                p = p.add_run(run);
                            }
                        }

                        let col_w = col_widths_dxa[c_idx];
                        let mut cell = TableCell::new()
                            .width(col_w, WidthType::Dxa)
                            .add_paragraph(p);

                        if is_zebra {
                            let zc = zebra_color.as_deref().unwrap_or("F8FAFC").trim_start_matches('#');
                            cell = cell.shading(Shading::new().fill(zc));
                        }

                        // Borde inferior sutil para cada celda
                        let cell_bot = TableCellBorder::new(TableCellBorderPosition::Bottom)
                            .size(2)
                            .color("E2E8F0")
                            .border_type(BorderType::Single);
                        cell = cell.set_border(cell_bot);

                        data_cells.push(cell);
                    }
                    table_rows.push(TableRow::new(data_cells));
                }

                let table = Table::new(table_rows)
                    .clear_all_border()
                    .set_grid(col_widths_dxa);
                doc = doc.add_table(table);
            }

            _ => {
                // Otros componentes
            }
        }
        Ok(doc)
    }

    fn render_divider_table(&self, thickness: f32, color: Option<&str>, usable_width_dxa: u32) -> Table {
        let sz = (thickness * 8.0).max(4.0) as usize;
        let c = color.unwrap_or("CBD5E1").trim_start_matches('#');
        let tcb = TableCellBorder::new(TableCellBorderPosition::Bottom)
            .size(sz)
            .color(c)
            .border_type(BorderType::Single);

        let cell = TableCell::new()
            .width(usable_width_dxa as usize, WidthType::Dxa)
            .clear_all_border()
            .set_border(tcb)
            .add_paragraph(Paragraph::new());

        let row = TableRow::new(vec![cell]);
        Table::new(vec![row])
            .clear_all_border()
            .set_grid(vec![usable_width_dxa as usize])
    }

    fn render_row_to_table(&self, items: &[RowItemAst], data: Option<&Value>, usable_width_dxa: u32) -> Result<Table, String> {
        let count = items.len();
        let total_flex: f32 = items.iter().map(|it| match it {
            RowItemAst::Detailed { flex, .. } => flex.unwrap_or(1.0),
            RowItemAst::Simple(_) => 1.0,
        }).sum();

        let mut col_widths_dxa: Vec<usize> = Vec::new();
        for it in items {
            let f = match it {
                RowItemAst::Detailed { flex, width, .. } => {
                    if let Some(w) = width {
                        (*w * 20.0) as usize
                    } else {
                        (flex.unwrap_or(1.0) / total_flex.max(1.0) * usable_width_dxa as f32) as usize
                    }
                }
                RowItemAst::Simple(_) => (usable_width_dxa as f32 / count as f32) as usize,
            };
            col_widths_dxa.push(f.max(500));
        }

        let mut cells: Vec<TableCell> = Vec::new();
        for (idx, row_item) in items.iter().enumerate() {
            let item_comp = match row_item {
                RowItemAst::Detailed { item, .. } => item,
                RowItemAst::Simple(item) => item,
            };

            let w_dxa = col_widths_dxa[idx];
            let mut cell = TableCell::new()
                .width(w_dxa, WidthType::Dxa)
                .clear_all_border();

            let paras = self.component_to_paragraphs(item_comp, data, w_dxa as u32)?;
            if paras.is_empty() {
                cell = cell.add_paragraph(Paragraph::new());
            } else {
                for p in paras {
                    cell = cell.add_paragraph(p);
                }
            }
            cells.push(cell);
        }

        let row_obj = TableRow::new(cells);
        Ok(Table::new(vec![row_obj])
            .clear_all_border()
            .set_grid(col_widths_dxa))
    }

    fn component_to_header_footer_items(
        &self,
        comp: &ComponentAst,
        data: Option<&Value>,
        available_width_dxa: u32,
    ) -> Result<Vec<DocxHeaderFooterItem>, String> {
        match comp {
            ComponentAst::Row { items, .. } if items.len() > 1 => {
                let table = self.render_row_to_table(items, data, available_width_dxa)?;
                Ok(vec![DocxHeaderFooterItem::Table(table)])
            }
            ComponentAst::Divider { thickness, color, .. } => {
                let table = self.render_divider_table(*thickness, color.as_deref(), available_width_dxa);
                Ok(vec![DocxHeaderFooterItem::Table(table)])
            }
            ComponentAst::Column { items, .. } => {
                let mut res = Vec::new();
                for item in items {
                    res.extend(self.component_to_header_footer_items(item, data, available_width_dxa)?);
                }
                Ok(res)
            }
            ComponentAst::Container { child, .. } => {
                if let Some(c) = child {
                    self.component_to_header_footer_items(c, data, available_width_dxa)
                } else {
                    Ok(vec![])
                }
            }
            _ => {
                let paras = self.component_to_paragraphs(comp, data, available_width_dxa)?;
                Ok(paras.into_iter().map(DocxHeaderFooterItem::Paragraph).collect())
            }
        }
    }

    fn component_to_paragraphs(&self, comp: &ComponentAst, data: Option<&Value>, available_width_dxa: u32) -> Result<Vec<Paragraph>, String> {
        match comp {
            ComponentAst::Text { value, style, bold, italic, font_size, color, alignment, .. } => {
                let interpolated = clean_word_text(&interpolate_string(value, data));
                let is_bold = bold.unwrap_or(style.as_deref() == Some("h1") || style.as_deref() == Some("h2"));
                let sz = font_size.map(|f| (f * 2.0) as usize).unwrap_or(20);

                let mut p = Paragraph::new();
                if let Some(align) = alignment {
                    p = match align.as_str() {
                        "center" => p.align(AlignmentType::Center),
                        "right" => p.align(AlignmentType::Right),
                        _ => p.align(AlignmentType::Left),
                    };
                }

                let lines: Vec<&str> = interpolated.split('\n').collect();
                for (l_idx, line) in lines.iter().enumerate() {
                    let mut run = Run::new().add_text(*line);
                    if is_bold {
                        run = run.bold();
                    }
                    if italic.unwrap_or(false) {
                        run = run.italic();
                    }
                    run = run.size(sz);
                    if let Some(c) = color {
                        run = run.color(c.trim_start_matches('#'));
                    }
                    if l_idx + 1 < lines.len() {
                        run = run.add_break(BreakType::TextWrapping);
                    }
                    p = p.add_run(run);
                }

                Ok(vec![p])
            }

            ComponentAst::Image { source, width, height, alignment, .. } => {
                let src = interpolate_string(source, data);
                if let Ok(bytes) = crate::image::load_source(&src) {
                    let w = (width.unwrap_or(120.0) * 15.0) as u32;
                    let h = (height.unwrap_or(40.0) * 15.0) as u32;
                    let pic = Pic::new(&bytes).size(w, h);
                    let mut p = Paragraph::new().add_run(Run::new().add_image(pic));
                    if let Some(align) = alignment {
                        p = match align.as_str() {
                            "center" => p.align(AlignmentType::Center),
                            "right" => p.align(AlignmentType::Right),
                            _ => p.align(AlignmentType::Left),
                        };
                    }
                    return Ok(vec![p]);
                }
                Ok(vec![])
            }

            ComponentAst::Column { items, .. } => {
                let mut res = Vec::new();
                for item in items {
                    res.extend(self.component_to_paragraphs(item, data, available_width_dxa)?);
                }
                Ok(res)
            }

            ComponentAst::Row { items, .. } => {
                let mut res = Vec::new();
                for item in items {
                    let c = match item {
                        RowItemAst::Detailed { item, .. } => item,
                        RowItemAst::Simple(item) => item,
                    };
                    res.extend(self.component_to_paragraphs(c, data, available_width_dxa)?);
                }
                Ok(res)
            }

            ComponentAst::Container { child, .. } => {
                if let Some(c) = child {
                    self.component_to_paragraphs(c, data, available_width_dxa)
                } else {
                    Ok(vec![])
                }
            }

            ComponentAst::Divider { thickness: _, color: _, .. } => {
                Ok(vec![Paragraph::new()])
            }

            ComponentAst::Spacer { height: _ } => {
                Ok(vec![Paragraph::new()])
            }

            ComponentAst::PageNumber { alignment, .. } => {
                let mut p = Paragraph::new().add_run(Run::new().add_text("Pág. 1 de 1").size(18));
                p = match alignment.as_str() {
                    "center" => p.align(AlignmentType::Center),
                    "right" => p.align(AlignmentType::Right),
                    _ => p.align(AlignmentType::Left),
                };
                Ok(vec![p])
            }

            _ => Ok(vec![]),
        }
    }
}

impl Default for WordEngine {
    fn default() -> Self {
        Self::new()
    }
}

fn resolve_table_rows(
    table_data: &Option<Vec<HashMap<String, Value>>>,
    source: Option<&str>,
    data: Option<&Value>,
) -> Vec<HashMap<String, Value>> {
    if let Some(td) = table_data {
        if !td.is_empty() {
            return td.clone();
        }
    }
    if let Some(src) = source {
        if let Some(val) = data {
            if let Some(arr) = val.get(src).and_then(|v| v.as_array()) {
                return arr.iter().filter_map(|item| {
                    if let Some(obj) = item.as_object() {
                        Some(obj.iter().map(|(k, v)| (k.clone(), v.clone())).collect())
                    } else {
                        None
                    }
                }).collect();
            }
        }
    }
    Vec::new()
}

fn format_cell_value(val: Option<&Value>, format: Option<&str>) -> String {
    match format {
        Some("currency") => {
            if let Some(n) = val.and_then(|v| v.as_f64().or_else(|| v.as_str().and_then(|s| s.trim_start_matches('$').trim().parse::<f64>().ok()))) {
                format!("${:.2}", n)
            } else {
                val.map(|v| v.to_string()).unwrap_or_default()
            }
        }
        Some("number") => {
            if let Some(n) = val.and_then(|v| v.as_f64().or_else(|| v.as_str().and_then(|s| s.parse::<f64>().ok()))) {
                format!("{:.2}", n)
            } else {
                val.map(|v| v.to_string()).unwrap_or_default()
            }
        }
        Some("percentage") => {
            if let Some(n) = val.and_then(|v| v.as_f64()) {
                format!("{:.1}%", n)
            } else {
                val.map(|v| v.to_string()).unwrap_or_default()
            }
        }
        _ => {
            val.map(|v| match v {
                Value::String(s) => s.clone(),
                _ => v.to_string(),
            }).unwrap_or_default()
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

fn clean_word_text(s: &str) -> String {
    s.replace('\t', " ")
     .lines()
     .map(|l| l.trim())
     .collect::<Vec<_>>()
     .join("\n")
}
