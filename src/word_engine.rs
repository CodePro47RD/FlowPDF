use std::collections::HashMap;
use std::io::Cursor;
use docx_rs::*;
use serde_json::Value;

use crate::ast::*;

pub struct WordEngine;

impl WordEngine {
    pub fn new() -> Self {
        Self
    }

    pub fn render(&self, doc_ast: &DocumentDefinitionAst, data: Option<&Value>) -> Result<Vec<u8>, String> {
        let mut doc = Docx::new();

        // 1. Configuración de página y márgenes
        let margin_val = (doc_ast.page.margin * 20.0) as i32; // conversión a dxa (twips: 1 pt = 20 dxa)
        let page_margin = PageMargin::new()
            .top(doc_ast.page.margin_top.map(|v| (v * 20.0) as i32).unwrap_or(margin_val))
            .bottom(doc_ast.page.margin_bottom.map(|v| (v * 20.0) as i32).unwrap_or(margin_val))
            .left(doc_ast.page.margin_left.map(|v| (v * 20.0) as i32).unwrap_or(margin_val))
            .right(doc_ast.page.margin_right.map(|v| (v * 20.0) as i32).unwrap_or(margin_val));
        doc = doc.page_margin(page_margin);

        // Dimensiones de página
        let (w_pt, h_pt) = match doc_ast.page.size.to_uppercase().as_str() {
            "LETTER" => (612.0, 792.0),
            "LEGAL" => (612.0, 1008.0),
            _ => (595.28, 841.89), // A4
        };
        let (w_dxa, h_dxa) = if doc_ast.page.orientation.to_lowercase() == "landscape" {
            ((h_pt * 20.0) as u32, (w_pt * 20.0) as u32)
        } else {
            ((w_pt * 20.0) as u32, (h_pt * 20.0) as u32)
        };
        doc = doc.page_size(w_dxa, h_dxa);

        // 2. Encabezado de página
        if let Some(header) = &doc_ast.header {
            let mut header_obj = Header::new();
            for p in self.component_to_paragraphs(header, data)? {
                header_obj = header_obj.add_paragraph(p);
            }
            doc = doc.header(header_obj);
        }

        // 3. Marcas de agua flotantes
        let watermarks = doc_ast.all_watermarks();
        for wm in &watermarks {
            let text = interpolate_string(&wm.text, data);
            if !text.is_empty() {
                let color_hex = wm.color.as_deref().unwrap_or("CCCCCC").trim_start_matches('#');
                // En Word, una marca de agua se presenta destacada como párrafo con estilo translúcido o cabecera
                let wm_run = Run::new()
                    .add_text(&text)
                    .bold()
                    .size((wm.font_size * 2.0) as usize)
                    .color(color_hex);

                let mut wm_p = Paragraph::new().add_run(wm_run);
                wm_p = match wm.position.as_deref() {
                    Some("top-left") | Some("bottom-left") => wm_p.align(AlignmentType::Left),
                    Some("top-right") | Some("bottom-right") => wm_p.align(AlignmentType::Right),
                    _ => wm_p.align(AlignmentType::Center),
                };
                doc = doc.add_paragraph(wm_p);
            }
        }

        // 4. Contenido
        match &doc_ast.content {
            ContentAst::Single(comp) => {
                doc = self.render_component(comp, doc, data)?;
            }
            ContentAst::Multiple(items) => {
                for item in items {
                    doc = self.render_component(item, doc, data)?;
                }
            }
        }

        // 5. Pie de página
        if let Some(footer) = &doc_ast.footer {
            let mut footer_obj = Footer::new();
            for p in self.component_to_paragraphs(footer, data)? {
                footer_obj = footer_obj.add_paragraph(p);
            }
            doc = doc.footer(footer_obj);
        }

        let mut buffer = Cursor::new(Vec::new());
        doc.build().pack(&mut buffer).map_err(|e| format!("Word generation error: {:?}", e))?;
        Ok(buffer.into_inner())
    }

    fn render_component(&self, comp: &ComponentAst, mut doc: Docx, data: Option<&Value>) -> Result<Docx, String> {
        match comp {
            ComponentAst::Text { value, style, bold, italic, font_size, color, alignment, .. } => {
                let interpolated = interpolate_string(value, data);
                let mut run = Run::new().add_text(&interpolated);

                let is_bold = bold.unwrap_or(style.as_deref() == Some("h1") || style.as_deref() == Some("h2"));
                if is_bold {
                    run = run.bold();
                }
                if italic.unwrap_or(false) {
                    run = run.italic();
                }

                let sz = font_size.map(|f| (f * 2.0) as usize).unwrap_or_else(|| {
                    match style.as_deref() {
                        Some("h1") => 32, // 16 pt
                        Some("h2") => 26, // 13 pt
                        Some("h3") => 22, // 11 pt
                        _ => 20,          // 10 pt
                    }
                });
                run = run.size(sz);

                if let Some(c) = color {
                    run = run.color(c.trim_start_matches('#'));
                }

                let mut p = Paragraph::new().add_run(run);
                if let Some(align) = alignment {
                    p = match align.as_str() {
                        "center" => p.align(AlignmentType::Center),
                        "right" => p.align(AlignmentType::Right),
                        _ => p.align(AlignmentType::Left),
                    };
                }

                doc = doc.add_paragraph(p);
            }

            ComponentAst::Spacer { .. } => {
                doc = doc.add_paragraph(Paragraph::new());
            }

            ComponentAst::Divider { .. } => {
                // Separador horizontal
                let run = Run::new().add_text("____________________________________________________________")
                    .color("CBD5E1")
                    .size(16);
                doc = doc.add_paragraph(Paragraph::new().add_run(run));
            }

            ComponentAst::Column { items, .. } => {
                for item in items {
                    doc = self.render_component(item, doc, data)?;
                }
            }

            ComponentAst::Row { items, .. } => {
                // Representamos fila como párrafos o celdas
                for item in items {
                    let c = match item {
                        RowItemAst::Detailed { item, .. } => item,
                        RowItemAst::Simple(item) => item,
                    };
                    doc = self.render_component(c, doc, data)?;
                }
            }

            ComponentAst::Container { child, .. } => {
                if let Some(c) = child {
                    doc = self.render_component(c, doc, data)?;
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
                group_by,
                ..
            } => {
                let resolved_rows = resolve_table_rows(table_data, source.as_deref(), data);

                let mut table_rows: Vec<TableRow> = Vec::new();

                // Fila de cabecera
                let mut header_cells: Vec<TableCell> = Vec::new();
                for col in columns {
                    let mut run = Run::new().add_text(&col.title).bold().size(18); // 9 pt
                    if let Some(tc) = header_color {
                        run = run.color(tc.trim_start_matches('#'));
                    } else {
                        run = run.color("FFFFFF");
                    }

                    let p = Paragraph::new().add_run(run);
                    let mut cell = TableCell::new().add_paragraph(p);

                    if let Some(bg) = header_background {
                        cell = cell.shading(Shading::new().fill(bg.trim_start_matches('#')));
                    } else {
                        cell = cell.shading(Shading::new().fill("1E40AF"));
                    }
                    header_cells.push(cell);
                }
                table_rows.push(TableRow::new(header_cells));

                // Filas de datos
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

                    for col in columns {
                        let val_str = format_cell_value(col.field.as_ref().and_then(|f| row_map.get(f)), col.format.as_deref());
                        let run = Run::new().add_text(&val_str).size(18);

                        let mut p = Paragraph::new().add_run(run);
                        if let Some(align) = &col.align {
                            p = match align.as_str() {
                                "center" => p.align(AlignmentType::Center),
                                "right" => p.align(AlignmentType::Right),
                                _ => p.align(AlignmentType::Left),
                            };
                        }

                        let mut cell = TableCell::new().add_paragraph(p);
                        if is_zebra {
                            let zc = zebra_color.as_deref().unwrap_or("F8FAFC").trim_start_matches('#');
                            cell = cell.shading(Shading::new().fill(zc));
                        }
                        data_cells.push(cell);
                    }
                    table_rows.push(TableRow::new(data_cells));
                }

                let table = Table::new(table_rows);
                doc = doc.add_table(table);
                doc = doc.add_paragraph(Paragraph::new()); // Espacio tras la tabla
            }

            _ => {
                // Otros componentes
            }
        }
        Ok(doc)
    }

    fn component_to_paragraphs(&self, comp: &ComponentAst, data: Option<&Value>) -> Result<Vec<Paragraph>, String> {
        match comp {
            ComponentAst::Text { value, style, bold, font_size, color, alignment, .. } => {
                let interpolated = interpolate_string(value, data);
                let mut run = Run::new().add_text(&interpolated);
                if bold.unwrap_or(style.as_deref() == Some("h1") || style.as_deref() == Some("h2")) {
                    run = run.bold();
                }
                let sz = font_size.map(|f| (f * 2.0) as usize).unwrap_or(20);
                run = run.size(sz);
                if let Some(c) = color {
                    run = run.color(c.trim_start_matches('#'));
                }
                let mut p = Paragraph::new().add_run(run);
                if let Some(align) = alignment {
                    p = match align.as_str() {
                        "center" => p.align(AlignmentType::Center),
                        "right" => p.align(AlignmentType::Right),
                        _ => p.align(AlignmentType::Left),
                    };
                }
                Ok(vec![p])
            }
            ComponentAst::Column { items, .. } => {
                let mut res = Vec::new();
                for item in items {
                    res.extend(self.component_to_paragraphs(item, data)?);
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
                    res.extend(self.component_to_paragraphs(c, data)?);
                }
                Ok(res)
            }
            _ => Ok(Vec::new()),
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
        td.clone()
    } else if let Some(src) = source {
        if let Some(val) = data {
            if let Some(arr) = val.get(src).and_then(|v| v.as_array()) {
                arr.iter().filter_map(|item| {
                    item.as_object().map(|obj| obj.iter().map(|(k, v)| (k.clone(), v.clone())).collect())
                }).collect()
            } else {
                Vec::new()
            }
        } else {
            Vec::new()
        }
    } else {
        Vec::new()
    }
}

fn format_cell_value(val: Option<&Value>, format: Option<&str>) -> String {
    let Some(v) = val else { return String::new(); };
    match format {
        Some("currency") => {
            if let Some(n) = v.as_f64() {
                format!("${:.2}", n)
            } else if let Some(s) = v.as_str() {
                s.to_string()
            } else {
                v.to_string()
            }
        }
        Some("number") => {
            if let Some(n) = v.as_f64() {
                format!("{:.2}", n)
            } else {
                v.to_string()
            }
        }
        Some("percentage") => {
            if let Some(n) = v.as_f64() {
                format!("{:.1}%", n)
            } else {
                v.to_string()
            }
        }
        _ => match v {
            Value::String(s) => s.clone(),
            _ => v.to_string(),
        },
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
