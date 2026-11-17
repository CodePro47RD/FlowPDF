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
    assert!(version_str.contains("v2.0.0"), "Version must contain v2.0.0, got: {}", version_str);
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
