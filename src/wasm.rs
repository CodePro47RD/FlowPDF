use crate::ast::DocumentDefinitionAst;
use crate::pdf_engine::PdfEngine;
use std::slice;

#[no_mangle]
pub extern "C" fn flowpdf_wasm_alloc(size: usize) -> *mut u8 {
    let mut buf = Vec::with_capacity(size);
    let ptr = buf.as_mut_ptr();
    std::mem::forget(buf);
    ptr
}

#[no_mangle]
pub unsafe extern "C" fn flowpdf_wasm_dealloc(ptr: *mut u8, size: usize) {
    if !ptr.is_null() && size > 0 {
        let _ = Vec::from_raw_parts(ptr, size, size);
    }
}

/// Renderiza un JSON a PDF en WebAssembly.
/// Retorna un u64 empaquetado: (out_ptr << 32) | out_len.
/// Si ocurre un error, retorna 0.
#[no_mangle]
pub unsafe extern "C" fn flowpdf_wasm_render(json_ptr: *const u8, json_len: usize) -> u64 {
    if json_ptr.is_null() || json_len == 0 {
        return 0;
    }

    let json_slice = slice::from_raw_parts(json_ptr, json_len);
    let json_str = match std::str::from_utf8(json_slice) {
        Ok(s) => s,
        Err(_) => return 0,
    };

    let doc_ast: DocumentDefinitionAst = match serde_json::from_str(json_str) {
        Ok(ast) => ast,
        Err(_) => return 0,
    };

    let engine = PdfEngine::new();
    match engine.render(&doc_ast, None) {
        Ok(pdf_bytes) => {
            let len = pdf_bytes.len();
            let mut boxed = pdf_bytes.into_boxed_slice();
            let ptr = boxed.as_mut_ptr();
            std::mem::forget(boxed);
            ((ptr as u64) << 32) | (len as u64)
        }
        Err(_) => 0,
    }
}

/// Extrae texto plano de un PDF en WebAssembly.
/// Retorna un u64 empaquetado: (out_ptr << 32) | out_len (UTF-8).
#[no_mangle]
pub unsafe extern "C" fn flowpdf_wasm_extract_text(pdf_ptr: *const u8, pdf_len: usize) -> u64 {
    if pdf_ptr.is_null() || pdf_len == 0 {
        return 0;
    }

    let pdf_slice = slice::from_raw_parts(pdf_ptr, pdf_len);
    match crate::extractor::PdfExtractor::extract_text(pdf_slice) {
        Ok(text) => {
            let bytes = text.into_bytes();
            let len = bytes.len();
            let mut boxed = bytes.into_boxed_slice();
            let ptr = boxed.as_mut_ptr();
            std::mem::forget(boxed);
            ((ptr as u64) << 32) | (len as u64)
        }
        Err(_) => 0,
    }
}

/// Registra una fuente TTF global en WebAssembly.
/// Retorna 0 en éxito, -1 en error.
#[no_mangle]
pub unsafe extern "C" fn flowpdf_wasm_register_font(
    name_ptr: *const u8,
    name_len: usize,
    font_ptr: *const u8,
    font_len: usize,
) -> i32 {
    if name_ptr.is_null() || name_len == 0 || font_ptr.is_null() || font_len == 0 {
        return -1;
    }

    let name_slice = slice::from_raw_parts(name_ptr, name_len);
    let name_str = match std::str::from_utf8(name_slice) {
        Ok(s) => s,
        Err(_) => return -2,
    };

    let font_slice = slice::from_raw_parts(font_ptr, font_len);
    match crate::font::register_global_font(name_str, font_slice) {
        Ok(_) => 0,
        Err(_) => -3,
    }
}
