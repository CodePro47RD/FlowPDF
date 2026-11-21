//! Métricas reales de Helvetica en las tablas: columnas `auto`, montos alineados, títulos de grupo y
//! títulos que no quedan solos al final de una página.

use lopdf::Document;
use flowpdf::ast::DocumentDefinitionAst;
use flowpdf::encoding::unicode_to_winansi_hex;
use flowpdf::metrics::helvetica_width;
use flowpdf::pdf_engine::PdfEngine;
use serde_json::json;

fn render(doc: serde_json::Value) -> Vec<u8> {
    let ast: DocumentDefinitionAst = serde_json::from_value(doc).expect("AST válido");
    PdfEngine::new().render(&ast, None).expect("render")
}

fn contenido(doc: &Document, pagina: u32) -> String {
    let id = doc.get_pages()[&pagina];
    String::from_utf8_lossy(&doc.get_page_content(id).unwrap()).into_owned()
}

/// Posición x de cada aparición del texto en la página (operadores `x y Tm <hex> Tj`).
fn posiciones_x(contenido: &str, texto: &str) -> Vec<f32> {
    let hex = unicode_to_winansi_hex(texto);
    contenido
        .match_indices(&format!(" Tm {hex} Tj"))
        .map(|(i, _)| {
            let antes: Vec<&str> = contenido[..i].split_whitespace().collect();
            antes[antes.len() - 2].parse().unwrap()
        })
        .collect()
}

fn texto(doc: &Document, pagina: u32) -> String {
    doc.extract_text(&[pagina]).unwrap_or_default()
}

const MARGEN: f32 = 40.0;
const ANCHO_CARTA: f32 = 612.0;

#[test]
fn la_columna_auto_toma_el_ancho_del_monto_mas_grande_y_lo_alinea_al_borde() {
    let montos = ["RD$5.00", "RD$34,980.00", "RD$1,234,567.89"];
    let filas: Vec<_> = montos.iter().map(|m| json!({ "concepto": "Pago de saldo", "pagado": m })).collect();
    let pdf = render(json!({
        "page": { "size": "Letter", "margin": MARGEN },
        "content": {
            "type": "table",
            "font_size": 9.0,
            "padding_x": 4.0,
            "columns": [
                { "title": "Concepto", "field": "concepto" },
                { "title": "Pagado", "field": "pagado", "auto": true, "align": "right" }
            ],
            "data": filas
        }
    }));

    let doc = Document::load_mem(&pdf).unwrap();
    let c = contenido(&doc, 1);
    let borde = ANCHO_CARTA - MARGEN - 4.0;
    for m in montos {
        let x = posiciones_x(&c, m)[0];
        // Termina justo en el borde derecho de la tabla (menos el relleno), sin pasarse
        assert!((x + helvetica_width(m, 9.0, false) - borde).abs() < 0.05, "{m} termina en {}", x + helvetica_width(m, 9.0, false));
    }
    // El monto más ancho no invade la columna del concepto
    let mas_grande = posiciones_x(&c, "RD$1,234,567.89")[0];
    let concepto = posiciones_x(&c, "Pago de saldo")[0];
    assert!(mas_grande > concepto + helvetica_width("Pago de saldo", 9.0, false));
}

#[test]
fn el_texto_alineado_a_la_derecha_usa_el_ancho_real() {
    // Las mayúsculas son más anchas que el promedio: antes se salían del borde
    let pdf = render(json!({
        "page": { "size": "Letter", "margin": MARGEN },
        "content": { "type": "text", "value": "TOTAL PAGADO", "bold": true, "font_size": 12.0, "alignment": "right" }
    }));
    let doc = Document::load_mem(&pdf).unwrap();
    let x = posiciones_x(&contenido(&doc, 1), "TOTAL PAGADO")[0];
    let fin = x + helvetica_width("TOTAL PAGADO", 12.0, true);
    assert!((fin - (ANCHO_CARTA - MARGEN)).abs() < 0.05, "termina en {fin}");
}

#[test]
fn intercala_un_titulo_por_grupo() {
    let filas = vec![
        json!({ "carrera": "Informática", "concepto": "CHU-119 Cálculo I" }),
        json!({ "carrera": "Informática", "concepto": "CHU-120 Física I" }),
        json!({ "carrera": "Otros conceptos", "concepto": "Servicios estudiantiles" }),
    ];
    let pdf = render(json!({
        "page": { "size": "Letter", "margin": MARGEN },
        "content": {
            "type": "table",
            "group_by": "carrera",
            "columns": [{ "title": "Concepto", "field": "concepto" }],
            "data": filas
        }
    }));
    let doc = Document::load_mem(&pdf).unwrap();
    let c = contenido(&doc, 1);
    // Un título por grupo, no uno por fila
    assert_eq!(posiciones_x(&c, "Informática").len(), 1);
    assert_eq!(posiciones_x(&c, "Otros conceptos").len(), 1);
    let t = texto(&doc, 1);
    let orden = ["Informática", "Cálculo", "Física", "Otros conceptos", "Servicios"].map(|p| t.find(p).unwrap());
    assert!(orden.windows(2).all(|w| w[0] < w[1]), "orden: {t}");
}

#[test]
fn el_titulo_de_una_tabla_no_queda_solo_al_final_de_la_pagina() {
    // 51 líneas (688.5 pt de 712) dejan sitio para el título (13.5 pt) pero no para la cabecera y la
    // primera fila (24 + 20 pt): sin la regla, el título quedaría solo al final de la página
    let mut items: Vec<_> = (0..51).map(|i| json!({ "type": "text", "value": format!("Relleno {i}") })).collect();
    items.push(json!({ "type": "text", "value": "Deudas saldadas", "bold": true }));
    items.push(json!({
        "type": "table",
        "columns": [{ "title": "Concepto", "field": "c" }],
        "data": (0..5).map(|i| json!({ "c": format!("Deuda {i}") })).collect::<Vec<_>>()
    }));
    let pdf = render(json!({
        "page": { "size": "Letter", "margin": MARGEN },
        "content": { "type": "column", "items": items }
    }));
    let doc = Document::load_mem(&pdf).unwrap();
    let total = doc.get_pages().len() as u32;
    let pagina_titulo = (1..=total).find(|p| texto(&doc, *p).contains("Deudas saldadas")).unwrap();
    assert!(texto(&doc, pagina_titulo).contains("Deuda 0"), "el título quedó separado de su tabla");
}

#[test]
fn un_contenedor_mas_alto_que_una_pagina_reparte_su_contenido() {
    let filas: Vec<_> = (0..120).map(|i| json!({ "c": format!("Deuda {i}") })).collect();
    let pdf = render(json!({
        "page": { "size": "Letter", "margin": MARGEN },
        "content": {
            "type": "container",
            "child": { "type": "table", "columns": [{ "title": "Concepto", "field": "c" }], "data": filas }
        },
        "footer": { "type": "page_number", "format": "Página {page} de {total}" }
    }));
    let doc = Document::load_mem(&pdf).unwrap();
    let total = doc.get_pages().len() as u32;
    assert!(total > 1);
    let todo: String = (1..=total).map(|p| texto(&doc, p)).collect::<Vec<_>>().join("\n");
    assert!(todo.contains("Deuda 0") && todo.contains("Deuda 119"));
    // Ninguna fila se dibuja por debajo del área útil (sobre el pie)
    for p in 1..=total {
        let c = contenido(&doc, p);
        for i in 0..120 {
            for y in posiciones_y(&c, &format!("Deuda {i}")) {
                assert!(y > MARGEN + 12.0, "Deuda {i} en y={y} de la página {p}: invade el pie");
            }
        }
    }
}

/// Posición y (desde abajo) de cada aparición del texto en la página.
fn posiciones_y(contenido: &str, texto: &str) -> Vec<f32> {
    let hex = unicode_to_winansi_hex(texto);
    contenido
        .match_indices(&format!(" Tm {hex} Tj"))
        .map(|(i, _)| {
            let antes: Vec<&str> = contenido[..i].split_whitespace().collect();
            antes[antes.len() - 1].parse().unwrap()
        })
        .collect()
}
