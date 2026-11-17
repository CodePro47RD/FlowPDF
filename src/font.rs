use std::collections::HashMap;
use std::sync::{Arc, Mutex, OnceLock};
use lopdf::{dictionary, Document, Object, ObjectId, Stream};
use crate::encoding::char_to_winansi;

pub fn winansi_to_char(b: u8) -> char {
    match b {
        0x00..=0x7F => b as char,
        0xA0..=0xFF => char::from_u32(b as u32).unwrap_or('?'),
        0x80 => '€',
        0x82 => '‚',
        0x83 => 'ƒ',
        0x84 => '„',
        0x85 => '…',
        0x86 => '†',
        0x87 => '‡',
        0x88 => 'ˆ',
        0x89 => '‰',
        0x8A => 'Š',
        0x8B => '‹',
        0x8C => 'Œ',
        0x8E => 'Ž',
        0x91 => '‘',
        0x92 => '’',
        0x93 => '“',
        0x94 => '”',
        0x95 => '•',
        0x96 => '–',
        0x97 => '—',
        0x98 => '˜',
        0x99 => '™',
        0x9A => 'š',
        0x9B => '›',
        0x9C => 'œ',
        0x9E => 'ž',
        0x9F => 'Ÿ',
        _ => '?',
    }
}

#[derive(Debug, Clone)]
pub struct CustomFont {
    pub name: String,
    pub postscript_name: String,
    pub ttf_bytes: Vec<u8>,
    pub units_per_em: u16,
    pub ascender: i16,
    pub descender: i16,
    pub cap_height: i16,
    pub italic_angle: f32,
    pub bbox: [i16; 4],
    pub widths: Vec<u16>, // 224 elements for WinAnsi 32..=255
}

impl CustomFont {
    pub fn from_bytes(name: &str, bytes: &[u8]) -> Result<Self, String> {
        let face = ttf_parser::Face::parse(bytes, 0)
            .map_err(|e| format!("Error analizando fuente TTF '{}': {:?}", name, e))?;

        let units_per_em = face.units_per_em();
        let ascender = face.ascender();
        let descender = face.descender();
        let cap_height = face.capital_height().unwrap_or(ascender);
        let italic_angle = face.italic_angle();

        let global_bbox = face.global_bounding_box();
        let bbox = [
            global_bbox.x_min,
            global_bbox.y_min,
            global_bbox.x_max,
            global_bbox.y_max,
        ];

        // Extraer nombre PostScript
        let mut postscript_name = String::new();
        for name_record in face.names() {
            if name_record.name_id == ttf_parser::name_id::POST_SCRIPT_NAME {
                if let Some(s) = name_record.to_string() {
                    postscript_name = s;
                    break;
                }
            }
        }
        if postscript_name.is_empty() {
            postscript_name = name.replace(' ', "-");
        }

        // Calcular ancho normalizado (escala 1000) para cada caracter WinAnsi 32..=255
        let mut widths = Vec::with_capacity(224);
        for byte_code in 32..=255u8 {
            let ch = winansi_to_char(byte_code);
            let width_1000 = if let Some(glyph_id) = face.glyph_index(ch) {
                if let Some(advance) = face.glyph_hor_advance(glyph_id) {
                    ((advance as f64 / units_per_em as f64) * 1000.0).round() as u16
                } else {
                    500
                }
            } else {
                500
            };
            widths.push(width_1000);
        }

        Ok(Self {
            name: name.to_string(),
            postscript_name,
            ttf_bytes: bytes.to_vec(),
            units_per_em,
            ascender,
            descender,
            cap_height,
            italic_angle,
            bbox,
            widths,
        })
    }

    /// Medir el ancho de una cadena en puntos tipográficos para un font_size dado
    pub fn measure_text_width(&self, text: &str, font_size: f32) -> f32 {
        let mut total_width_1000: f32 = 0.0;
        for c in text.chars() {
            let byte_code = char_to_winansi(c);
            let char_width_1000 = if byte_code >= 32 {
                let idx = (byte_code - 32) as usize;
                self.widths.get(idx).copied().unwrap_or(500)
            } else {
                500
            };
            total_width_1000 += char_width_1000 as f32;
        }
        (total_width_1000 / 1000.0) * font_size
    }

    /// Registrar los objetos PDF necesarios (FontFile2, FontDescriptor, Font) en el Document
    pub fn add_to_pdf_document(&self, doc: &mut Document) -> Result<ObjectId, String> {
        // 1. Stream del archivo TTF comprimido (/FontFile2)
        let mut font_stream = Stream::new(
            dictionary! {
                "Length1" => self.ttf_bytes.len() as i64,
            },
            self.ttf_bytes.clone(),
        );
        font_stream.compress().map_err(|e| format!("Error comprimiendo stream TTF: {:?}", e))?;
        let font_file_id = doc.add_object(font_stream);

        // 2. Diccionario FontDescriptor
        let scale = 1000.0 / self.units_per_em as f64;
        let font_desc_id = doc.add_object(dictionary! {
            "Type" => "FontDescriptor",
            "FontName" => Object::Name(self.postscript_name.as_bytes().to_vec()),
            "Flags" => 32, // Nonsymbolic
            "FontBBox" => vec![
                ((self.bbox[0] as f64) * scale).round().into(),
                ((self.bbox[1] as f64) * scale).round().into(),
                ((self.bbox[2] as f64) * scale).round().into(),
                ((self.bbox[3] as f64) * scale).round().into(),
            ],
            "Ascent" => ((self.ascender as f64) * scale).round() as i64,
            "Descent" => ((self.descender as f64) * scale).round() as i64,
            "CapHeight" => ((self.cap_height as f64) * scale).round() as i64,
            "ItalicAngle" => self.italic_angle as i64,
            "StemV" => 80,
            "FontFile2" => font_file_id,
        });

        // 3. Diccionario Font TrueType
        let widths_objects: Vec<Object> = self.widths.iter().map(|&w| (w as i64).into()).collect();
        let font_id = doc.add_object(dictionary! {
            "Type" => "Font",
            "Subtype" => "TrueType",
            "BaseFont" => Object::Name(self.postscript_name.as_bytes().to_vec()),
            "FirstChar" => 32,
            "LastChar" => 255,
            "Widths" => widths_objects,
            "FontDescriptor" => font_desc_id,
            "Encoding" => "WinAnsiEncoding",
        });

        Ok(font_id)
    }
}

// Registro Global de Fuentes en Memoria
static GLOBAL_FONT_REGISTRY: OnceLock<Mutex<HashMap<String, Arc<CustomFont>>>> = OnceLock::new();

fn get_registry() -> &'static Mutex<HashMap<String, Arc<CustomFont>>> {
    GLOBAL_FONT_REGISTRY.get_or_init(|| Mutex::new(HashMap::new()))
}

pub fn register_global_font(name: &str, bytes: &[u8]) -> Result<Arc<CustomFont>, String> {
    let font = CustomFont::from_bytes(name, bytes)?;
    let font_arc = Arc::new(font);
    let mut reg = get_registry().lock().unwrap();
    reg.insert(name.to_lowercase(), font_arc.clone());
    reg.insert(font_arc.postscript_name.to_lowercase(), font_arc.clone());
    Ok(font_arc)
}

pub fn get_global_font(name: &str) -> Option<Arc<CustomFont>> {
    let reg = get_registry().lock().unwrap();
    reg.get(&name.to_lowercase()).cloned()
}
