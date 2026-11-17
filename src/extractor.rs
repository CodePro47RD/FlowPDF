use lopdf::{Document, Object, ObjectId};
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct DocumentMetadata {
    pub title: Option<String>,
    pub author: Option<String>,
    pub subject: Option<String>,
    pub keywords: Option<String>,
    pub creator: Option<String>,
    pub producer: Option<String>,
    pub creation_date: Option<String>,
    pub modification_date: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExtractedPage {
    pub page_number: u32,
    pub width: f32,
    pub height: f32,
    pub text: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExtractedDocument {
    pub page_count: usize,
    pub metadata: DocumentMetadata,
    pub pages: Vec<ExtractedPage>,
    pub full_text: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ExtractOptions {
    pub pages: Option<Vec<u32>>,
}

pub struct PdfExtractor;

impl PdfExtractor {
    pub fn extract_text(pdf_bytes: &[u8]) -> Result<String, String> {
        let doc = Document::load_mem(pdf_bytes).map_err(|e| format!("Failed to parse PDF document: {}", e))?;
        let pages: Vec<u32> = doc.get_pages().keys().cloned().collect();
        if pages.is_empty() {
            return Ok(String::new());
        }

        let mut full_text = String::new();
        for page_num in &pages {
            match doc.extract_text(&[*page_num]) {
                Ok(text) => {
                    let trimmed = text.trim();
                    if !trimmed.is_empty() {
                        if !full_text.is_empty() {
                            full_text.push('\n');
                        }
                        full_text.push_str(trimmed);
                    }
                }
                Err(e) => {
                    eprintln!("Warning: could not extract text from page {}: {}", page_num, e);
                }
            }
        }

        Ok(full_text)
    }

    pub fn extract_document(pdf_bytes: &[u8], options: Option<ExtractOptions>) -> Result<ExtractedDocument, String> {
        let doc = Document::load_mem(pdf_bytes).map_err(|e| format!("Failed to parse PDF document: {}", e))?;
        let all_pages: BTreeMap<u32, ObjectId> = doc.get_pages();
        let total_pages = all_pages.len();

        let metadata = Self::extract_metadata(&doc);

        let target_pages: Vec<u32> = if let Some(opts) = options {
            if let Some(requested) = opts.pages {
                requested.into_iter().filter(|p| all_pages.contains_key(p)).collect()
            } else {
                all_pages.keys().cloned().collect()
            }
        } else {
            all_pages.keys().cloned().collect()
        };

        let mut pages = Vec::with_capacity(target_pages.len());
        let mut full_text = String::new();

        for &page_num in &target_pages {
            let (width, height) = if let Some(&page_id) = all_pages.get(&page_num) {
                Self::get_page_dimensions(&doc, page_id)
            } else {
                (595.28, 841.89)
            };

            let text = doc.extract_text(&[page_num]).unwrap_or_default().trim().to_string();

            if !text.is_empty() {
                if !full_text.is_empty() {
                    full_text.push('\n');
                }
                full_text.push_str(&text);
            }

            pages.push(ExtractedPage {
                page_number: page_num,
                width,
                height,
                text,
            });
        }

        Ok(ExtractedDocument {
            page_count: total_pages,
            metadata,
            pages,
            full_text,
        })
    }

    fn extract_metadata(doc: &Document) -> DocumentMetadata {
        let mut meta = DocumentMetadata::default();
        if let Ok(info_dict) = Self::get_info_dict(doc) {
            meta.title = Self::get_string_field(info_dict, b"Title");
            meta.author = Self::get_string_field(info_dict, b"Author");
            meta.subject = Self::get_string_field(info_dict, b"Subject");
            meta.keywords = Self::get_string_field(info_dict, b"Keywords");
            meta.creator = Self::get_string_field(info_dict, b"Creator");
            meta.producer = Self::get_string_field(info_dict, b"Producer");
            meta.creation_date = Self::get_string_field(info_dict, b"CreationDate");
            meta.modification_date = Self::get_string_field(info_dict, b"ModDate");
        }
        meta
    }

    fn get_info_dict(doc: &Document) -> Result<&lopdf::Dictionary, lopdf::Error> {
        let info_obj = doc.trailer.get(b"Info")?;
        match info_obj {
            Object::Reference(id) => doc.get_dictionary(*id),
            Object::Dictionary(ref dict) => Ok(dict),
            _ => Err(lopdf::Error::Type),
        }
    }

    fn get_string_field(dict: &lopdf::Dictionary, key: &[u8]) -> Option<String> {
        dict.get(key).ok().and_then(|obj| match obj {
            Object::String(bytes, _) => {
                if bytes.len() >= 2 && bytes[0] == 0xFE && bytes[1] == 0xFF {
                    let u16_chars: Vec<u16> = bytes[2..]
                        .chunks_exact(2)
                        .map(|c| ((c[0] as u16) << 8) | (c[1] as u16))
                        .collect();
                    String::from_utf16(&u16_chars).ok()
                } else {
                    Some(String::from_utf8_lossy(bytes).into_owned())
                }
            }
            _ => None,
        })
    }

    fn get_page_dimensions(doc: &Document, page_id: ObjectId) -> (f32, f32) {
        if let Ok(page_dict) = doc.get_dictionary(page_id) {
            let box_obj = page_dict.get(b"MediaBox").or_else(|_| page_dict.get(b"CropBox"));
            if let Ok(Object::Array(arr)) = box_obj {
                if arr.len() >= 4 {
                    let get_num = |obj: &Object| -> Option<f32> {
                        match obj {
                            Object::Real(f) => Some(*f as f32),
                            Object::Integer(i) => Some(*i as f32),
                            _ => None,
                        }
                    };
                    let x0 = get_num(&arr[0]).unwrap_or(0.0);
                    let y0 = get_num(&arr[1]).unwrap_or(0.0);
                    let x1 = get_num(&arr[2]).unwrap_or(595.28);
                    let y1 = get_num(&arr[3]).unwrap_or(841.89);
                    return ((x1 - x0).abs(), (y1 - y0).abs());
                }
            }
        }
        (595.28, 841.89) // Default A4
    }
}
