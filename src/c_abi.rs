use std::ffi::{CStr, CString};
use std::os::raw::c_char;
use std::ptr;

use crate::ast::DocumentDefinitionAst;
use crate::pdf_engine::PdfEngine;

#[repr(C)]
pub struct ReportForgeResult {
    pub data: *mut u8,
    pub length: usize,
    pub success: bool,
    pub error_message: *mut c_char,
}

impl ReportForgeResult {
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
pub unsafe extern "C" fn reportforge_render_pdf(
    doc_json_ptr: *const c_char,
    data_json_ptr: *const c_char,
) -> ReportForgeResult {
    if doc_json_ptr.is_null() {
        return ReportForgeResult::error("document_json pointer is null");
    }

    let doc_str = match CStr::from_ptr(doc_json_ptr).to_str() {
        Ok(s) => s,
        Err(e) => return ReportForgeResult::error(&format!("Invalid UTF-8 in document JSON: {}", e)),
    };

    let doc_ast: DocumentDefinitionAst = match serde_json::from_str(doc_str) {
        Ok(ast) => ast,
        Err(e) => return ReportForgeResult::error(&format!("Failed to parse document AST: {}", e)),
    };

    let data_val = if !data_json_ptr.is_null() {
        match CStr::from_ptr(data_json_ptr).to_str() {
            Ok(s) => match serde_json::from_str::<serde_json::Value>(s) {
                Ok(v) => Some(v),
                Err(e) => return ReportForgeResult::error(&format!("Failed to parse data JSON: {}", e)),
            },
            Err(e) => return ReportForgeResult::error(&format!("Invalid UTF-8 in data JSON: {}", e)),
        }
    } else {
        None
    };

    let engine = PdfEngine::new();
    match engine.render(&doc_ast, data_val.as_ref()) {
        Ok(pdf_bytes) => ReportForgeResult::success(pdf_bytes),
        Err(err) => ReportForgeResult::error(&format!("Render error: {}", err)),
    }
}

#[no_mangle]
pub unsafe extern "C" fn reportforge_free_result(result: ReportForgeResult) {
    if !result.data.is_null() && result.length > 0 {
        let _ = Vec::from_raw_parts(result.data, result.length, result.length);
    }
    if !result.error_message.is_null() {
        let _ = CString::from_raw(result.error_message);
    }
}

#[no_mangle]
pub extern "C" fn reportforge_version() -> *const c_char {
    static VERSION: &[u8] = b"ReportForge Rust Core v2.0.0\0";
    VERSION.as_ptr() as *const c_char
}
