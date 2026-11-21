use std::ffi::{CStr, CString};
use std::os::raw::c_char;
use std::ptr;

use crate::ast::DocumentDefinitionAst;
use crate::pdf_engine::PdfEngine;

#[repr(C)]
pub struct FlowPdfResult {
    pub data: *mut u8,
    pub length: usize,
    pub success: bool,
    pub error_message: *mut c_char,
}

impl FlowPdfResult {
    fn success(bytes: Vec<u8>) -> Self {
        let mut boxed_slice = bytes.into_boxed_slice();
        let length = boxed_slice.len();
        let data = boxed_slice.as_mut_ptr();
        std::mem::forget(boxed_slice);

        Self {
            data,
            length,
            success: true,
            error_message: ptr::null_mut(),
        }
    }

    fn error(msg: &str) -> Self {
        let c_str = CString::new(msg).unwrap_or_else(|_| CString::new("Unknown error").unwrap());
        Self {
            data: ptr::null_mut(),
            length: 0,
            success: false,
            error_message: c_str.into_raw(),
        }
    }
}

#[no_mangle]
pub unsafe extern "C" fn flowpdf_render_pdf(
    doc_json_ptr: *const c_char,
    data_json_ptr: *const c_char,
) -> FlowPdfResult {
    if doc_json_ptr.is_null() {
        return FlowPdfResult::error("document_json pointer is null");
    }

    let doc_str = match CStr::from_ptr(doc_json_ptr).to_str() {
        Ok(s) => s,
        Err(e) => return FlowPdfResult::error(&format!("Invalid UTF-8 in document JSON: {}", e)),
    };

    let doc_ast: DocumentDefinitionAst = match serde_json::from_str(doc_str) {
        Ok(ast) => ast,
        Err(e) => return FlowPdfResult::error(&format!("Failed to parse document AST: {}", e)),
    };

    let data_val = if !data_json_ptr.is_null() {
        match CStr::from_ptr(data_json_ptr).to_str() {
            Ok(s) => match serde_json::from_str::<serde_json::Value>(s) {
                Ok(v) => Some(v),
                Err(e) => return FlowPdfResult::error(&format!("Failed to parse data JSON: {}", e)),
            },
            Err(e) => return FlowPdfResult::error(&format!("Invalid UTF-8 in data JSON: {}", e)),
        }
    } else {
        None
    };

    let engine = PdfEngine::new();
    match engine.render(&doc_ast, data_val.as_ref()) {
        Ok(pdf_bytes) => FlowPdfResult::success(pdf_bytes),
        Err(err) => FlowPdfResult::error(&format!("Render error: {}", err)),
    }
}

#[no_mangle]
pub unsafe extern "C" fn flowpdf_extract_text(
    pdf_data: *const u8,
    pdf_len: usize,
) -> FlowPdfResult {
    if pdf_data.is_null() || pdf_len == 0 {
        return FlowPdfResult::error("pdf_data pointer is null or length is 0");
    }

    let slice = std::slice::from_raw_parts(pdf_data, pdf_len);
    match crate::extractor::PdfExtractor::extract_text(slice) {
        Ok(text) => FlowPdfResult::success(text.into_bytes()),
        Err(err) => FlowPdfResult::error(&err),
    }
}

#[no_mangle]
pub unsafe extern "C" fn flowpdf_extract_json(
    pdf_data: *const u8,
    pdf_len: usize,
    options_json_ptr: *const c_char,
) -> FlowPdfResult {
    if pdf_data.is_null() || pdf_len == 0 {
        return FlowPdfResult::error("pdf_data pointer is null or length is 0");
    }

    let slice = std::slice::from_raw_parts(pdf_data, pdf_len);
    let options: Option<crate::extractor::ExtractOptions> = if !options_json_ptr.is_null() {
        match CStr::from_ptr(options_json_ptr).to_str() {
            Ok(s) => match serde_json::from_str(s) {
                Ok(opt) => Some(opt),
                Err(e) => return FlowPdfResult::error(&format!("Invalid options JSON: {}", e)),
            },
            Err(e) => return FlowPdfResult::error(&format!("Invalid UTF-8 in options JSON: {}", e)),
        }
    } else {
        None
    };

    match crate::extractor::PdfExtractor::extract_document(slice, options) {
        Ok(extracted) => match serde_json::to_vec(&extracted) {
            Ok(json_bytes) => FlowPdfResult::success(json_bytes),
            Err(e) => FlowPdfResult::error(&format!("Serialization error: {}", e)),
        },
        Err(err) => FlowPdfResult::error(&err),
    }
}

#[no_mangle]
pub unsafe extern "C" fn flowpdf_register_font(
    font_name: *const c_char,
    font_bytes: *const u8,
    font_len: usize,
) -> i32 {
    if font_name.is_null() || font_bytes.is_null() || font_len == 0 {
        return -1;
    }
    let c_str = match CStr::from_ptr(font_name).to_str() {
        Ok(s) => s,
        Err(_) => return -2,
    };
    let slice = std::slice::from_raw_parts(font_bytes, font_len);
    match crate::font::register_global_font(c_str, slice) {
        Ok(_) => 0,
        Err(_) => -3,
    }
}

#[no_mangle]
pub unsafe extern "C" fn flowpdf_free_result(result: FlowPdfResult) {
    if !result.data.is_null() && result.length > 0 {
        let _ = Vec::from_raw_parts(result.data, result.length, result.length);
    }
    if !result.error_message.is_null() {
        let _ = CString::from_raw(result.error_message);
    }
}

#[no_mangle]
pub extern "C" fn flowpdf_version() -> *const c_char {
    // La versión sale de Cargo.toml (en CI, la del tag del release)
    static VERSION: &str = concat!("FlowPDF Rust Core v", env!("CARGO_PKG_VERSION"), "\0");
    VERSION.as_ptr() as *const c_char
}
