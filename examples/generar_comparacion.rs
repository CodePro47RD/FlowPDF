use flowpdf::ast::DocumentDefinitionAst;
use flowpdf::excel_engine::ExcelEngine;
use flowpdf::pdf_engine::PdfEngine;
use flowpdf::word_engine::WordEngine;
use std::fs;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("============================================================");
    println!("  FlowPDF - Generación Comparativa de Paridad Visual        ");
    println!("============================================================");

    let json_template = r##"{
        "page": { "size": "A4", "orientation": "portrait", "margin": 25.0 },
        "watermark": {
            "text": "COPIA OFICIAL",
            "position": "center",
            "font_size": 36.0,
            "opacity": 0.12,
            "color": "#64748B"
        },
        "header": {
            "type": "column",
            "spacing": 3.0,
            "items": [
                {
                    "type": "text",
                    "value": "Universidad Tecnológica del Cibao Oriental",
                    "style": "h2",
                    "alignment": "center",
                    "bold": true,
                    "color": "#0F172A"
                },
                {
                    "type": "text",
                    "value": "Av. Universitaria No. 100, Cotuí, provincia Sánchez Ramírez, República Dominicana, 43000",
                    "alignment": "center",
                    "font_size": 8.5,
                    "color": "#475569"
                },
                {
                    "type": "text",
                    "value": "DIVISIÓN ADMISIONES Y REGISTRO",
                    "alignment": "center",
                    "bold": true,
                    "font_size": 11.0,
                    "color": "#1E3A8A"
                },
                {
                    "type": "row",
                    "items": [
                        { "type": "text", "value": "" },
                        { "type": "text", "value": "Etapa: Inscripción", "alignment": "right", "bold": true, "color": "#0F172A" }
                    ]
                },
                {
                    "type": "divider",
                    "thickness": 1.0,
                    "color": "#94A3B8"
                }
            ]
        },
        "content": [
            {
                "type": "row",
                "items": [
                    {
                        "type": "column",
                        "spacing": 2.0,
                        "items": [
                            { "type": "text", "value": "MATRÍCULA : 2021-1022", "bold": true },
                            { "type": "text", "value": "PENSUM : 046-2014 (PRIMARIO)", "color": "#334155" }
                        ]
                    },
                    {
                        "type": "column",
                        "spacing": 2.0,
                        "items": [
                            { "type": "text", "value": "ESTUDIANTE : LUIS ANGEL FERNÁNDEZ JORGE", "bold": true },
                            { "type": "text", "value": "CARRERA : 0015 Licenciatura en Informática", "color": "#334155" }
                        ]
                    }
                ]
            },
            {
                "type": "spacer",
                "height": 10.0
            },
            {
                "type": "table",
                "header_background": "#8FAADC",
                "header_color": "#0F172A",
                "zebra": true,
                "zebra_color": "#F1F5F9",
                "columns": [
                    { "title": "Código", "field": "codigo", "width": 80.0 },
                    { "title": "Asignatura", "field": "asignatura", "width": 160.0 },
                    { "title": "Cr", "field": "cr", "width": 35.0, "align": "center" },
                    { "title": "Horario", "field": "horario", "width": 140.0 },
                    { "title": "Profesor", "field": "profesor", "width": 130.0 },
                    { "title": "Estado", "field": "estado", "width": 50.0, "align": "center" },
                    { "title": "Trim", "field": "trim", "width": 40.0, "align": "center" }
                ],
                "data": [
                    {
                        "codigo": "CHU-120-02",
                        "asignatura": "Cálculo II",
                        "cr": 4,
                        "horario": "MI 18:00 - 20:00 (L310)\nJ 19:00 - 22:00 (K-203)",
                        "profesor": "Miguel Angel Hernández",
                        "estado": "AP",
                        "trim": 12
                    },
                    {
                        "codigo": "CHU-121-01",
                        "asignatura": "ÁLGEBRA MATRICIAL",
                        "cr": 4,
                        "horario": "L 16:00 - 18:00 (Virtual-05)\nJ 16:00 - 18:00 (Virtual-02)",
                        "profesor": "LEWIS BIENVENIDO SANTOS",
                        "estado": "AP",
                        "trim": 9
                    },
                    {
                        "codigo": "IRI-122-01",
                        "asignatura": "Introducción a los Circuitos Lógicos",
                        "cr": 3,
                        "horario": "M 19:00 - 22:00 (L310)\nD 18:00 - 20:00 (Virtual-06)",
                        "profesor": "Sucre Orlando Gómez",
                        "estado": "AP",
                        "trim": 11
                    },
                    {
                        "codigo": "IRI-128-01",
                        "asignatura": "Auditoría de Informática",
                        "cr": 3,
                        "horario": "L 19:00 - 22:00 (J-204)\nS 12:00 - 14:00 (Virtual-02)",
                        "profesor": "Rafael Eugenio Robles",
                        "estado": "AP",
                        "trim": 13
                    }
                ]
            },
            {
                "type": "divider",
                "thickness": 1.0,
                "color": "#94A3B8"
            },
            {
                "type": "row",
                "items": [
                    { "type": "text", "value": "Total Cr: 14", "bold": true, "alignment": "left" }
                ]
            }
        ],
        "footer": {
            "type": "column",
            "spacing": 2.0,
            "items": [
                {
                    "type": "text",
                    "value": "Cotuí, República Dominicana",
                    "alignment": "center",
                    "font_size": 8.0,
                    "color": "#64748B"
                },
                {
                    "type": "row",
                    "items": [
                        { "type": "text", "value": "Teléfono: +1 809-585-2291", "font_size": 8.0, "color": "#64748B" },
                        { "type": "text", "value": "informacion@uteco.edu.do", "font_size": 8.0, "color": "#64748B", "alignment": "center" },
                        { "type": "text", "value": "www.uteco.edu.do", "font_size": 8.0, "color": "#64748B", "alignment": "right" }
                    ]
                },
                {
                    "type": "row",
                    "items": [
                        { "type": "text", "value": "UTECO\\2021-1022", "font_size": 8.0, "color": "#94A3B8" },
                        { "type": "text", "value": "26/11/2026 1:08 p. m.", "font_size": 8.0, "color": "#94A3B8", "alignment": "center" },
                        { "type": "page_number", "alignment": "right" }
                    ]
                }
            ]
        }
    }"##;

    let doc_ast: DocumentDefinitionAst = serde_json::from_str(json_template)?;

    // 1. PDF
    let pdf_engine = PdfEngine::new();
    let pdf_bytes = pdf_engine.render(&doc_ast, None)?;
    let pdf_path = "resultado_academico.pdf";
    fs::write(pdf_path, &pdf_bytes)?;
    println!("[✓] PDF generado con éxito: {} ({} bytes)", pdf_path, pdf_bytes.len());

    // 2. Excel (XLSX)
    let excel_engine = ExcelEngine::new();
    let xlsx_bytes = excel_engine.render(&doc_ast, None)?;
    let xlsx_path = match fs::write("resultado_academico.xlsx", &xlsx_bytes) {
        Ok(_) => "resultado_academico.xlsx".to_string(),
        Err(_) => {
            let alt = "resultado_academico_nuevo.xlsx".to_string();
            let _ = fs::write(&alt, &xlsx_bytes);
            println!("[!] Nota: 'resultado_academico.xlsx' está abierto en Excel. Se guardó como '{}'", alt);
            alt
        }
    };
    println!("[✓] Excel (.xlsx) generado con éxito: {} ({} bytes)", xlsx_path, xlsx_bytes.len());

    // 3. Word (DOCX)
    let word_engine = WordEngine::new();
    let docx_bytes = word_engine.render(&doc_ast, None)?;
    let docx_path = match fs::write("resultado_academico.docx", &docx_bytes) {
        Ok(_) => "resultado_academico.docx".to_string(),
        Err(_) => {
            let alt = "resultado_academico_nuevo.docx".to_string();
            let _ = fs::write(&alt, &docx_bytes);
            println!("[!] Nota: 'resultado_academico.docx' está abierto en Word. Se guardó como '{}'", alt);
            alt
        }
    };
    println!("[✓] Word (.docx) generado con éxito: {} ({} bytes)", docx_path, docx_bytes.len());

    println!("============================================================");
    println!("  ¡Generación completada para los 3 formatos!               ");
    println!("============================================================");

    Ok(())
}
