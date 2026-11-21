use reportforge::ast::DocumentDefinitionAst;
use reportforge::c_abi::*;
use reportforge::pdf_engine::PdfEngine;
use std::ffi::{CStr, CString};

#[test]
fn test_render_minimal_document() {
    let json_input = r#"{
        "page": {
            "size": "A4",
            "orientation": "portrait",
            "margin": 36.0
        },
        "content": {
            "type": "text",
            "value": "Hello from ReportForge Rust Core v2.0!",
            "bold": true,
            "font_size": 16.0
        }
    }"#;

    let doc_ast: DocumentDefinitionAst = serde_json::from_str(json_input).expect("Valid JSON AST");
    let engine = PdfEngine::new();
    let result = engine.render(&doc_ast, None);
    assert!(result.is_ok(), "Document rendering should succeed: {:?}", result.err());

    let pdf_bytes = result.unwrap();
    assert!(pdf_bytes.len() > 100, "PDF should have substantial length");
    assert!(pdf_bytes.starts_with(b"%PDF-"), "Output must start with PDF header bytes");

    let doc = lopdf::Document::load_mem(&pdf_bytes).expect("Load PDF from memory");
    let text = doc.extract_text(&[1]).expect("Extract text from page 1");
    assert!(text.contains("Hello from ReportForge"), "Extracted text should contain our string: {}", text);
}

#[test]
fn test_unicode_and_spanish_accents() {
    let json_input = r#"{
        "page": {
            "size": "A4",
            "orientation": "portrait",
            "margin": 40.0
        },
        "content": [
            {
                "type": "text",
                "value": "Factura Electrónica Dominicana - Acentos: á, é, í, ó, ú, ñ, Ñ, ¿, ¡, €",
                "font_size": 14.0,
                "bold": true
            },
            {
                "type": "text",
                "value": "Total a Pagar: € 1,250.99 con ITBIS (18%) incluido.",
                "font_size": 11.0
            }
        ]
    }"#;

    let doc_ast: DocumentDefinitionAst = serde_json::from_str(json_input).expect("Valid JSON AST");
    let engine = PdfEngine::new();
    let result = engine.render(&doc_ast, None);
    assert!(result.is_ok(), "Unicode document rendering failed: {:?}", result.err());

    let pdf_bytes = result.unwrap();
    assert!(pdf_bytes.starts_with(b"%PDF-"));
}

#[test]
fn test_table_rendering() {
    let json_input = r#"{
        "page": {
            "size": "A4",
            "orientation": "portrait",
            "margin": 36.0
        },
        "content": {
            "type": "table",
            "repeat_header": true,
            "columns": [
                { "title": "Descripción", "field": "desc", "width": 200.0 },
                { "title": "Cant.", "field": "qty", "width": 60.0 },
                { "title": "Precio", "field": "price", "width": 100.0 },
                { "title": "Total", "field": "total", "width": 100.0 }
            ],
            "data": [
                { "desc": "Servidor Dedicado Rust", "qty": "2", "price": "$250.00", "total": "$500.00" },
                { "desc": "Licencia ReportForge v2.0", "qty": "1", "price": "$999.00", "total": "$999.00" },
                { "desc": "Soporte 24/7", "qty": "12", "price": "$50.00", "total": "$600.00" }
            ]
        }
    }"#;

    let doc_ast: DocumentDefinitionAst = serde_json::from_str(json_input).expect("Valid JSON AST");
    let engine = PdfEngine::new();
    let result = engine.render(&doc_ast, None);
    assert!(result.is_ok(), "Table rendering failed: {:?}", result.err());

    let pdf_bytes = result.unwrap();
    assert!(pdf_bytes.starts_with(b"%PDF-"));
}

#[test]
fn test_qr_and_barcode_rendering() {
    let json_input = r#"{
        "page": {
            "size": "A4",
            "orientation": "portrait",
            "margin": 36.0
        },
        "content": [
            {
                "type": "qr",
                "value": "https://github.com/reportforge/reportforge",
                "size": 100.0
            },
            {
                "type": "barcode",
                "value": "FAC2026-9901",
                "barcode_type": "CODE128",
                "height": 40.0
            }
        ]
    }"#;

    let doc_ast: DocumentDefinitionAst = serde_json::from_str(json_input).expect("Valid JSON AST");
    let engine = PdfEngine::new();
    let result = engine.render(&doc_ast, None);
    assert!(result.is_ok(), "Barcode/QR rendering failed: {:?}", result.err());

    let pdf_bytes = result.unwrap();
    assert!(pdf_bytes.starts_with(b"%PDF-"));
}

#[test]
fn test_c_abi_version() {
    let version_ptr = reportforge_version();
    assert!(!version_ptr.is_null());
    let version_str = unsafe { CStr::from_ptr(version_ptr).to_str().unwrap() };
    let expected = format!("v{}", env!("CARGO_PKG_VERSION"));
    assert!(version_str.ends_with(&expected), "Version must end with {}, got: {}", expected, version_str);
}

#[test]
fn test_c_abi_render_pdf() {
    let json_input = r#"{
        "page": { "size": "A4", "orientation": "portrait", "margin": 30.0 },
        "content": { "type": "text", "value": "Testing C-ABI FFI in Rust" }
    }"#;

    let c_json = CString::new(json_input).unwrap();
    let result = unsafe { reportforge_render_pdf(c_json.as_ptr(), std::ptr::null()) };

    assert!(result.success, "C-ABI should succeed");
    assert!(!result.data.is_null(), "Data pointer must not be null");
    assert!(result.length > 0, "PDF length must be greater than 0");

    let slice = unsafe { std::slice::from_raw_parts(result.data, result.length) };
    assert!(slice.starts_with(b"%PDF-"));

    // Cleanup
    unsafe { reportforge_free_result(result) };
}

#[test]
fn test_c_abi_extract_text() {
    let json_input = r#"{
        "page": { "size": "A4", "margin": 30.0 },
        "content": [
            { "type": "text", "value": "Texto Extraído con Éxito", "bold": true },
            { "type": "text", "value": "Segunda línea de prueba." }
        ]
    }"#;

    let c_json = CString::new(json_input).unwrap();
    let render_res = unsafe { reportforge_render_pdf(c_json.as_ptr(), std::ptr::null()) };
    assert!(render_res.success);

    // Call extraction
    let extract_res = unsafe { reportforge_extract_text(render_res.data, render_res.length) };
    assert!(extract_res.success, "Extraction should succeed");
    assert!(!extract_res.data.is_null());

    let extracted_slice = unsafe { std::slice::from_raw_parts(extract_res.data, extract_res.length) };
    let extracted_str = std::str::from_utf8(extracted_slice).expect("Valid UTF-8 extracted text");
    assert!(extracted_str.contains("Texto Extraído con Éxito"));

    unsafe {
        reportforge_free_result(extract_res);
        reportforge_free_result(render_res);
    }
}

#[test]
fn test_c_abi_extract_json() {
    let json_input = r#"{
        "page": { "size": "A4", "margin": 30.0 },
        "content": { "type": "text", "value": "Extracción de Metadatos y Estructura" }
    }"#;

    let c_json = CString::new(json_input).unwrap();
    let render_res = unsafe { reportforge_render_pdf(c_json.as_ptr(), std::ptr::null()) };
    assert!(render_res.success);

    let extract_res = unsafe { reportforge_extract_json(render_res.data, render_res.length, std::ptr::null()) };
    assert!(extract_res.success, "JSON Extraction should succeed");

    let slice = unsafe { std::slice::from_raw_parts(extract_res.data, extract_res.length) };
    let json_str = std::str::from_utf8(slice).expect("Valid UTF-8 JSON");
    let val: serde_json::Value = serde_json::from_str(json_str).expect("Valid JSON object");

    assert_eq!(val["page_count"], 1);
    assert!(val["pages"].is_array());
    assert_eq!(val["pages"].as_array().unwrap().len(), 1);

    unsafe {
        reportforge_free_result(extract_res);
        reportforge_free_result(render_res);
    }
}

#[test]
fn test_custom_ttf_font_registration_and_rendering() {
    let font_path = "C:\\Windows\\Fonts\\arial.ttf";
    if !std::path::Path::new(font_path).exists() {
        println!("Skipping TTF test: arial.ttf not found");
        return;
    }

    let font_bytes = std::fs::read(font_path).expect("Read arial.ttf");
    let c_name = CString::new("Arial").unwrap();

    // 1. Registrar fuente vía C-ABI
    let reg_code = unsafe { reportforge_register_font(c_name.as_ptr(), font_bytes.as_ptr(), font_bytes.len()) };
    assert_eq!(reg_code, 0, "Font registration must return 0 (success)");

    // 2. Renderizar documento usando la fuente personalizada "Arial"
    let json_input = r#"{
        "page": { "size": "A4", "margin": 30.0 },
        "content": [
            {
                "type": "text",
                "value": "Documento con fuente personalizada Arial TTF embebida",
                "font": "Arial",
                "font_size": 14.0
            },
            {
                "type": "text",
                "value": "Acentos en fuente TTF: á é í ó ú ñ €",
                "font": "Arial",
                "font_size": 11.0
            }
        ]
    }"#;

    let c_json = CString::new(json_input).unwrap();
    let render_res = unsafe { reportforge_render_pdf(c_json.as_ptr(), std::ptr::null()) };
    assert!(render_res.success, "Rendering with TTF font should succeed");

    let pdf_slice = unsafe { std::slice::from_raw_parts(render_res.data, render_res.length) };
    assert!(pdf_slice.starts_with(b"%PDF-"));

    // Verificar que el PDF contiene el objeto FontDescriptor
    let doc = lopdf::Document::load_mem(pdf_slice).expect("Load PDF with embedded TTF");
    let mut found_font_descriptor = false;
    for (_id, obj) in &doc.objects {
        if let lopdf::Object::Dictionary(dict) = obj {
            if let Ok(type_obj) = dict.get(b"Type") {
                if let lopdf::Object::Name(name_bytes) = type_obj {
                    if name_bytes == b"FontDescriptor" {
                        found_font_descriptor = true;
                        break;
                    }
                }
            }
        }
    }
    assert!(found_font_descriptor, "PDF must contain embedded FontDescriptor");

    unsafe { reportforge_free_result(render_res) };
}

#[test]
fn test_vector_charts_rendering() {
    let json_input = r##"{
        "page": { "size": "A4", "margin": 30.0 },
        "content": [
            {
                "type": "chart",
                "chart_type": "bar",
                "title": "Ventas Trimestrales (Tema Light)",
                "height": 140.0,
                "categories": ["Q1", "Q2", "Q3", "Q4"],
                "series": [
                    { "name": "Servicios", "values": [120.0, 150.0, 190.0, 240.0], "color": "#0066FF" },
                    { "name": "Licencias", "values": [80.0, 110.0, 140.0, 180.0], "color": "#10B981" }
                ],
                "theme": "light"
            },
            {
                "type": "spacer",
                "height": 15.0
            },
            {
                "type": "chart",
                "chart_type": "line",
                "title": "Tendencia de Usuarios (Tema Dark)",
                "height": 140.0,
                "categories": ["Ene", "Feb", "Mar", "Abr"],
                "series": [
                    { "name": "Usuarios Activos", "values": [1200.0, 1850.0, 2400.0, 3100.0], "color": "#F59E0B" }
                ],
                "theme": "dark"
            },
            {
                "type": "spacer",
                "height": 15.0
            },
            {
                "type": "chart",
                "chart_type": "donut",
                "title": "Distribución por Categoría",
                "height": 140.0,
                "series": [
                    { "name": "Cloud", "values": [45.0], "color": "#0066FF" },
                    { "name": "Soporte", "values": [30.0], "color": "#10B981" },
                    { "name": "Consultoría", "values": [25.0], "color": "#8B5CF6" }
                ],
                "theme": "light"
            }
        ]
    }"##;

    let doc_ast: DocumentDefinitionAst = serde_json::from_str(json_input).expect("Valid JSON AST with Charts");
    let engine = PdfEngine::new();
    let result = engine.render(&doc_ast, None);
    assert!(result.is_ok(), "Charts rendering failed: {:?}", result.err());

    let pdf_bytes = result.unwrap();
    assert!(pdf_bytes.starts_with(b"%PDF-"));

    let doc = lopdf::Document::load_mem(&pdf_bytes).expect("Load PDF with charts");
    let text = doc.extract_text(&[1]).expect("Extract text from charts page");
    assert!(text.contains("Ventas Trimestrales"));
    assert!(text.contains("Tendencia de Usuarios"));
}
