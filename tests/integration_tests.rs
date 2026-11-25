use flowpdf::ast::DocumentDefinitionAst;
use flowpdf::c_abi::*;
use flowpdf::pdf_engine::PdfEngine;
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
            "value": "Hello from FlowPDF Rust Core!",
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
    assert!(text.contains("Hello from FlowPDF"), "Extracted text should contain our string: {}", text);
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
                { "desc": "Licencia FlowPDF", "qty": "1", "price": "$999.00", "total": "$999.00" },
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
                "value": "https://github.com/codepro47rd/flowpdf",
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
    let version_ptr = flowpdf_version();
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
    let result = unsafe { flowpdf_render_pdf(c_json.as_ptr(), std::ptr::null()) };

    assert!(result.success, "C-ABI should succeed");
    assert!(!result.data.is_null(), "Data pointer must not be null");
    assert!(result.length > 0, "PDF length must be greater than 0");

    let slice = unsafe { std::slice::from_raw_parts(result.data, result.length) };
    assert!(slice.starts_with(b"%PDF-"));

    // Cleanup
    unsafe { flowpdf_free_result(result) };
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
    let render_res = unsafe { flowpdf_render_pdf(c_json.as_ptr(), std::ptr::null()) };
    assert!(render_res.success);

    // Call extraction
    let extract_res = unsafe { flowpdf_extract_text(render_res.data, render_res.length) };
    assert!(extract_res.success, "Extraction should succeed");
    assert!(!extract_res.data.is_null());

    let extracted_slice = unsafe { std::slice::from_raw_parts(extract_res.data, extract_res.length) };
    let extracted_str = std::str::from_utf8(extracted_slice).expect("Valid UTF-8 extracted text");
    assert!(extracted_str.contains("Texto Extraído con Éxito"));

    unsafe {
        flowpdf_free_result(extract_res);
        flowpdf_free_result(render_res);
    }
}

#[test]
fn test_c_abi_extract_json() {
    let json_input = r#"{
        "page": { "size": "A4", "margin": 30.0 },
        "content": { "type": "text", "value": "Extracción de Metadatos y Estructura" }
    }"#;

    let c_json = CString::new(json_input).unwrap();
    let render_res = unsafe { flowpdf_render_pdf(c_json.as_ptr(), std::ptr::null()) };
    assert!(render_res.success);

    let extract_res = unsafe { flowpdf_extract_json(render_res.data, render_res.length, std::ptr::null()) };
    assert!(extract_res.success, "JSON Extraction should succeed");

    let slice = unsafe { std::slice::from_raw_parts(extract_res.data, extract_res.length) };
    let json_str = std::str::from_utf8(slice).expect("Valid UTF-8 JSON");
    let val: serde_json::Value = serde_json::from_str(json_str).expect("Valid JSON object");

    assert_eq!(val["page_count"], 1);
    assert!(val["pages"].is_array());
    assert_eq!(val["pages"].as_array().unwrap().len(), 1);

    unsafe {
        flowpdf_free_result(extract_res);
        flowpdf_free_result(render_res);
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
    let reg_code = unsafe { flowpdf_register_font(c_name.as_ptr(), font_bytes.as_ptr(), font_bytes.len()) };
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
    let render_res = unsafe { flowpdf_render_pdf(c_json.as_ptr(), std::ptr::null()) };
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

    unsafe { flowpdf_free_result(render_res) };
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

#[test]
fn test_floating_watermark_in_pdf() {
    let json_input = r##"{
        "page": {
            "size": "A4",
            "margin": 36.0
        },
        "watermark": {
            "text": "CONFIDENCIAL",
            "x": 120.0,
            "y": 350.0,
            "rotation": -45.0,
            "opacity": 0.2,
            "font_size": 48.0,
            "color": "#DC2626"
        },
        "content": [
            {
                "type": "text",
                "value": "Documento con marca de agua flotante",
                "style": "h1"
            }
        ]
    }"##;

    let doc_ast: DocumentDefinitionAst = serde_json::from_str(json_input).expect("Valid JSON AST with Watermark");
    let engine = PdfEngine::new();
    let result = engine.render(&doc_ast, None);
    assert!(result.is_ok(), "Watermark rendering failed: {:?}", result.err());

    let pdf_bytes = result.unwrap();
    assert!(pdf_bytes.starts_with(b"%PDF-"));

    let doc = lopdf::Document::load_mem(&pdf_bytes).expect("Load PDF with watermark");
    let text = doc.extract_text(&[1]).expect("Extract text from watermark page");
    assert!(text.contains("CONFIDENCIAL"), "Extracted text should contain the watermark: {}", text);
    assert!(text.contains("Documento con marca de agua"));
}

#[test]
fn test_render_excel_xlsx() {
    let json_input = r#"{
        "page": { "size": "A4" },
        "watermark": {
            "text": "BORRADOR",
            "opacity": 0.15
        },
        "header": {
            "type": "text",
            "value": "REPORTE DE VENTAS EN EXCEL",
            "style": "h1"
        },
        "content": {
            "type": "table",
            "columns": [
                { "title": "Código", "field": "code", "width": 80.0 },
                { "title": "Producto", "field": "name", "width": 180.0 },
                { "title": "Precio", "field": "price", "format": "currency", "align": "right" },
                { "title": "Cantidad", "field": "qty", "format": "number", "align": "center" }
            ],
            "data": [
                { "code": "SRV-01", "name": "Servidor Cloud 4C/8G", "price": 120.50, "qty": 3 },
                { "code": "LIC-02", "name": "Licencia Enterprise", "price": 450.00, "qty": 1 }
            ]
        }
    }"#;

    let doc_ast: DocumentDefinitionAst = serde_json::from_str(json_input).expect("Valid JSON AST");
    let excel_engine = flowpdf::excel_engine::ExcelEngine::new();
    let result = excel_engine.render(&doc_ast, None);
    assert!(result.is_ok(), "Excel rendering failed: {:?}", result.err());

    let xlsx_bytes = result.unwrap();
    // Los archivos .xlsx son archivos ZIP que comienzan con el encabezado [0x50, 0x4B, 0x03, 0x04] ("PK..")
    assert!(xlsx_bytes.len() > 500, "Excel file should have substantial size");
    assert_eq!(&xlsx_bytes[0..4], &[0x50, 0x4B, 0x03, 0x04], "Excel must start with ZIP magic bytes PK\x03\x04");

    // Verificar también a través de C-ABI
    let c_doc = CString::new(json_input).unwrap();
    unsafe {
        let res = flowpdf_render_xlsx(c_doc.as_ptr(), std::ptr::null());
        assert!(res.success, "C-ABI flowpdf_render_xlsx failed");
        assert!(res.length > 500);
        assert_eq!(std::slice::from_raw_parts(res.data, 4), &[0x50, 0x4B, 0x03, 0x04]);
        flowpdf_free_result(res);
    }
}

#[test]
fn test_render_word_docx() {
    let json_input = r#"{
        "page": { "size": "A4", "margin": 30.0 },
        "watermark": {
            "text": "CONFIDENCIAL",
            "position": "center"
        },
        "content": [
            {
                "type": "text",
                "value": "Contrato Comercial Word (.docx)",
                "style": "h1"
            },
            {
                "type": "text",
                "value": "Este documento ha sido exportado directamente a Microsoft Word utilizando FlowPDF."
            },
            {
                "type": "divider"
            },
            {
                "type": "table",
                "columns": [
                    { "title": "Cláusula", "field": "clause" },
                    { "title": "Detalle", "field": "detail" }
                ],
                "data": [
                    { "clause": "1. Objeto", "detail": "Prestación de servicios de software." },
                    { "clause": "2. Duración", "detail": "12 meses renovables." }
                ]
            }
        ]
    }"#;

    let doc_ast: DocumentDefinitionAst = serde_json::from_str(json_input).expect("Valid JSON AST");
    let word_engine = flowpdf::word_engine::WordEngine::new();
    let result = word_engine.render(&doc_ast, None);
    assert!(result.is_ok(), "Word rendering failed: {:?}", result.err());

    let docx_bytes = result.unwrap();
    // Los archivos .docx también son archivos ZIP que comienzan con [0x50, 0x4B, 0x03, 0x04]
    assert!(docx_bytes.len() > 500, "Word file should have substantial size");
    assert_eq!(&docx_bytes[0..4], &[0x50, 0x4B, 0x03, 0x04], "Word must start with ZIP magic bytes PK\x03\x04");

    // Verificar también a través de C-ABI
    let c_doc = CString::new(json_input).unwrap();
    unsafe {
        let res = flowpdf_render_docx(c_doc.as_ptr(), std::ptr::null());
        assert!(res.success, "C-ABI flowpdf_render_docx failed");
        assert!(res.length > 500);
        assert_eq!(std::slice::from_raw_parts(res.data, 4), &[0x50, 0x4B, 0x03, 0x04]);
        flowpdf_free_result(res);
    }
}

#[test]
fn test_c_abi_render_document_multi_format() {
    let json_input = r#"{
        "content": {
            "type": "text",
            "value": "Prueba Multi-Formato"
        }
    }"#;

    let c_doc = CString::new(json_input).unwrap();

    unsafe {
        // 1. PDF
        let c_fmt_pdf = CString::new("pdf").unwrap();
        let res_pdf = flowpdf_render_document(c_doc.as_ptr(), std::ptr::null(), c_fmt_pdf.as_ptr());
        assert!(res_pdf.success, "Render document PDF failed");
        assert_eq!(std::slice::from_raw_parts(res_pdf.data, 5), b"%PDF-");
        flowpdf_free_result(res_pdf);

        // 2. Excel (xlsx)
        let c_fmt_xlsx = CString::new("xlsx").unwrap();
        let res_xlsx = flowpdf_render_document(c_doc.as_ptr(), std::ptr::null(), c_fmt_xlsx.as_ptr());
        assert!(res_xlsx.success, "Render document XLSX failed");
        assert_eq!(std::slice::from_raw_parts(res_xlsx.data, 4), &[0x50, 0x4B, 0x03, 0x04]);
        flowpdf_free_result(res_xlsx);

        // 3. Word (docx)
        let c_fmt_docx = CString::new("docx").unwrap();
        let res_docx = flowpdf_render_document(c_doc.as_ptr(), std::ptr::null(), c_fmt_docx.as_ptr());
        assert!(res_docx.success, "Render document DOCX failed");
        assert_eq!(std::slice::from_raw_parts(res_docx.data, 4), &[0x50, 0x4B, 0x03, 0x04]);
        flowpdf_free_result(res_docx);
    }
}
