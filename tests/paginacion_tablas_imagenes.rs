//! Paginación, tablas con celdas de varias líneas e imágenes reales (JPEG y PNG).

use lopdf::{Document, Object};
use reportforge::ast::DocumentDefinitionAst;
use reportforge::pdf_engine::PdfEngine;
use serde_json::json;

fn render(doc: serde_json::Value) -> Vec<u8> {
    let ast: DocumentDefinitionAst = serde_json::from_value(doc).expect("AST válido");
    PdfEngine::new().render(&ast, None).expect("render")
}

fn texto_pagina(doc: &Document, pagina: u32) -> String {
    doc.extract_text(&[pagina]).unwrap_or_default()
}

/// Cantidad de operaciones de texto (Tj) en la página.
fn textos_en_pagina(doc: &Document, pagina: u32) -> usize {
    let id = doc.get_pages()[&pagina];
    let contenido = doc.get_page_content(id).unwrap();
    String::from_utf8_lossy(&contenido).matches(" Tj ").count()
}

#[test]
fn el_contenido_largo_pasa_a_otras_paginas_con_su_pie() {
    let lineas: Vec<_> = (0..150).map(|i| json!({ "type": "text", "value": format!("Línea {i}") })).collect();
    let pdf = render(json!({
        "page": { "size": "Letter", "margin": 40.0 },
        "header": { "type": "text", "value": "Reporte de prueba", "bold": true },
        "content": { "type": "column", "items": lineas },
        "footer": { "type": "page_number", "format": "Página {page} de {total}" }
    }));

    let doc = Document::load_mem(&pdf).unwrap();
    let total = doc.get_pages().len() as u32;
    assert!(total > 1, "150 líneas no caben en una carta: {total} página(s)");

    let todo: String = (1..=total).map(|p| texto_pagina(&doc, p)).collect::<Vec<_>>().join("\n");
    for i in 0..150 {
        assert!(todo.contains(&format!("Línea {i}")), "falta la línea {i}");
    }
    for p in 1..=total {
        let texto = texto_pagina(&doc, p);
        assert!(texto.contains("Reporte de prueba"), "la página {p} no tiene el encabezado");
        assert!(texto.contains(&format!("Página {p} de {total}")), "pie de la página {p}: {texto}");
    }
}

#[test]
fn la_tabla_se_reparte_entre_paginas_y_repite_la_cabecera() {
    let filas: Vec<_> = (0..90).map(|i| json!({ "desc": format!("Fila {i}"), "monto": "RD$150.00" })).collect();
    let pdf = render(json!({
        "page": { "size": "Letter", "margin": 40.0 },
        "content": {
            "type": "table",
            "repeat_header": true,
            "columns": [
                { "title": "Descripción", "field": "desc" },
                { "title": "Monto", "field": "monto", "width": 90.0, "align": "right" }
            ],
            "data": filas
        }
    }));

    let doc = Document::load_mem(&pdf).unwrap();
    let total = doc.get_pages().len() as u32;
    assert!(total > 1, "90 filas no caben en una carta: {total} página(s)");
    for p in 1..=total {
        assert!(texto_pagina(&doc, p).contains("Descripción"), "la página {p} no repite la cabecera");
    }
    let todo: String = (1..=total).map(|p| texto_pagina(&doc, p)).collect::<Vec<_>>().join("\n");
    assert!(todo.contains("Fila 0") && todo.contains("Fila 89"));
}

#[test]
fn la_celda_larga_parte_su_texto_en_varias_lineas() {
    let tabla = |desc: &str| {
        render(json!({
            "content": {
                "type": "table",
                "columns": [
                    { "title": "Concepto", "field": "desc", "width": 120.0 },
                    { "title": "Monto", "field": "monto", "width": 80.0 }
                ],
                "data": [ { "desc": desc, "monto": "RD$600.00" } ]
            }
        }))
    };

    let corta = Document::load_mem(&tabla("Algebra")).unwrap();
    let larga = Document::load_mem(&tabla("ESPECIAL CHU-121-01 ALGEBRA MATRICIAL Y GEOMETRIA ANALITICA")).unwrap();
    assert!(
        textos_en_pagina(&larga, 1) >= textos_en_pagina(&corta, 1) + 2,
        "el concepto largo debería ocupar varias líneas"
    );
    let texto = texto_pagina(&larga, 1);
    for palabra in ["ESPECIAL", "MATRICIAL", "ANALITICA", "RD$600.00"] {
        assert!(texto.contains(palabra), "falta '{palabra}' en: {texto}");
    }
}

#[test]
fn el_encabezado_acepta_una_columna() {
    let pdf = render(json!({
        "header": { "type": "column", "items": [
            { "type": "text", "value": "UTECO", "bold": true },
            { "type": "divider" }
        ]},
        "content": { "type": "text", "value": "Cuerpo" }
    }));
    let doc = Document::load_mem(&pdf).unwrap();
    assert!(texto_pagina(&doc, 1).contains("UTECO"));
}

/// PNG RGBA de 4x4 con la mitad transparente.
fn png_con_transparencia() -> Vec<u8> {
    let mut bytes = Vec::new();
    {
        let mut enc = png::Encoder::new(&mut bytes, 4, 4);
        enc.set_color(png::ColorType::Rgba);
        enc.set_depth(png::BitDepth::Eight);
        let mut w = enc.write_header().unwrap();
        let pixels: Vec<u8> = (0..16).flat_map(|i| [28, 142, 63, if i < 8 { 255 } else { 0 }]).collect();
        w.write_image_data(&pixels).unwrap();
    }
    bytes
}

fn imagenes_del_pdf(doc: &Document) -> Vec<lopdf::Dictionary> {
    doc.objects
        .values()
        .filter_map(|o| match o {
            Object::Stream(s) if s.dict.get(b"Subtype").and_then(|v| v.as_name()).ok() == Some(b"Image") => Some(s.dict.clone()),
            _ => None,
        })
        .collect()
}

#[test]
fn incrusta_png_con_su_mascara_de_transparencia() {
    use base64::Engine;
    let uri = format!("data:image/png;base64,{}", base64::engine::general_purpose::STANDARD.encode(png_con_transparencia()));
    let pdf = render(json!({ "content": { "type": "image", "source": uri, "width": 60.0, "height": 60.0 } }));

    let doc = Document::load_mem(&pdf).unwrap();
    let imagenes = imagenes_del_pdf(&doc);
    assert!(imagenes.iter().any(|d| d.get(b"SMask").is_ok()), "el PNG debe llevar su SMask");
    let contenido = String::from_utf8_lossy(&doc.get_page_content(doc.get_pages()[&1]).unwrap()).to_string();
    assert!(contenido.contains("/Im1 Do"), "la imagen debe dibujarse: {contenido}");
    assert!(!texto_pagina(&doc, 1).contains("[Image]"));
}

#[test]
fn incrusta_jpeg_sin_recomprimir() {
    use base64::Engine;
    let jpeg = [
        0xFF, 0xD8, 0xFF, 0xC0, 0x00, 0x11, 0x08, 0x00, 0x02, 0x00, 0x03, 0x03, 0x01, 0x22, 0x00, 0x02, 0x11, 0x01, 0x03,
        0x11, 0x01, 0xFF, 0xD9,
    ];
    let b64 = base64::engine::general_purpose::STANDARD.encode(jpeg);
    let pdf = render(json!({ "content": { "type": "image", "source": b64, "width": 30.0, "fit": "cover", "alignment": "left" } }));

    let doc = Document::load_mem(&pdf).unwrap();
    let imagenes = imagenes_del_pdf(&doc);
    assert_eq!(imagenes.len(), 1);
    assert_eq!(imagenes[0].get(b"Filter").unwrap().as_name().unwrap(), b"DCTDecode");
}

#[test]
fn una_imagen_ilegible_deja_el_marcador() {
    let pdf = render(json!({ "content": { "type": "image", "source": "no-existe.png", "width": 60.0, "height": 20.0 } }));
    let doc = Document::load_mem(&pdf).unwrap();
    assert!(texto_pagina(&doc, 1).contains("[Image]"));
}
