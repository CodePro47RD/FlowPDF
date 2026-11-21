//! Imágenes para el PDF.
//!
//! - **JPEG**: se incrusta tal cual (filtro `DCTDecode`); solo se leen sus dimensiones y canales.
//! - **PNG**: se decodifica a 8 bits por canal (escala de grises o RGB). El canal alfa, si lo hay,
//!   se separa en una máscara (`SMask`) para conservar la transparencia.
//!
//! La fuente puede ser un *data URI* (`data:image/png;base64,...`), base64 sin prefijo o una ruta de archivo.

use std::io::Cursor;

/// Imagen lista para escribirse como XObject en el PDF.
#[derive(Debug, Clone)]
pub struct PdfImage {
    pub width: u32,
    pub height: u32,
    /// `DeviceGray`, `DeviceRGB` o `DeviceCMYK`.
    pub color_space: &'static str,
    /// Datos de la imagen: JPEG completo (si `is_jpeg`) o píxeles crudos de 8 bits.
    pub data: Vec<u8>,
    pub is_jpeg: bool,
    /// Canal alfa de 8 bits (una muestra por píxel), si la imagen tiene transparencia.
    pub alpha: Option<Vec<u8>>,
    /// Los JPEG CMYK de Adobe guardan los canales invertidos.
    pub invert_cmyk: bool,
}

/// Lee los bytes de la imagen desde un data URI, una ruta de archivo o base64 sin prefijo.
pub fn load_source(source: &str) -> Result<Vec<u8>, String> {
    use base64::Engine;
    let source = source.trim();
    if source.is_empty() {
        return Err("la imagen no tiene fuente".to_string());
    }

    if let Some(rest) = source.strip_prefix("data:") {
        let (meta, payload) = rest.split_once(',').ok_or("data URI de imagen inválido")?;
        if !meta.ends_with(";base64") {
            return Err("el data URI de la imagen debe estar en base64".to_string());
        }
        return base64::engine::general_purpose::STANDARD
            .decode(payload.trim())
            .map_err(|e| format!("base64 de imagen inválido: {e}"));
    }

    if let Ok(bytes) = std::fs::read(source) {
        return Ok(bytes);
    }

    base64::engine::general_purpose::STANDARD
        .decode(source)
        .map_err(|_| format!("no se pudo leer la imagen: '{}' no es un archivo ni base64 válido", abreviar(source)))
}

/// Decodifica JPEG o PNG.
pub fn decode(bytes: &[u8]) -> Result<PdfImage, String> {
    if bytes.starts_with(&[0xFF, 0xD8]) {
        decode_jpeg(bytes)
    } else if bytes.starts_with(&[0x89, b'P', b'N', b'G']) {
        decode_png(bytes)
    } else {
        Err("formato de imagen no soportado (se admiten JPEG y PNG)".to_string())
    }
}

fn decode_jpeg(bytes: &[u8]) -> Result<PdfImage, String> {
    let mut i = 2;
    let mut adobe = false;
    while i + 4 <= bytes.len() {
        if bytes[i] != 0xFF {
            i += 1;
            continue;
        }
        let marker = bytes[i + 1];
        // Relleno y marcadores sin longitud
        if marker == 0xFF {
            i += 1;
            continue;
        }
        if marker == 0x01 || (0xD0..=0xD9).contains(&marker) {
            i += 2;
            continue;
        }
        let len = u16::from_be_bytes([bytes[i + 2], bytes[i + 3]]) as usize;
        // APP14 "Adobe": los CMYK vienen invertidos
        if marker == 0xEE && bytes.get(i + 4..i + 9) == Some(b"Adobe") {
            adobe = true;
        }
        // SOFn (menos DHT, JPG y DAC)
        let es_sof = (0xC0..=0xCF).contains(&marker) && ![0xC4, 0xC8, 0xCC].contains(&marker);
        if es_sof {
            let seg = bytes.get(i + 4..i + 10).ok_or("JPEG truncado")?;
            let height = u16::from_be_bytes([seg[1], seg[2]]) as u32;
            let width = u16::from_be_bytes([seg[3], seg[4]]) as u32;
            let components = seg[5];
            let color_space = match components {
                1 => "DeviceGray",
                3 => "DeviceRGB",
                4 => "DeviceCMYK",
                _ => return Err(format!("JPEG con {components} canales no soportado")),
            };
            if width == 0 || height == 0 {
                return Err("JPEG sin dimensiones".to_string());
            }
            return Ok(PdfImage {
                width,
                height,
                color_space,
                data: bytes.to_vec(),
                is_jpeg: true,
                alpha: None,
                invert_cmyk: components == 4 && adobe,
            });
        }
        i += 2 + len;
    }
    Err("JPEG sin encabezado de dimensiones (SOF)".to_string())
}

fn decode_png(bytes: &[u8]) -> Result<PdfImage, String> {
    let mut decoder = png::Decoder::new(Cursor::new(bytes));
    // Paleta y profundidades bajas → 8 bits por canal
    decoder.set_transformations(png::Transformations::EXPAND | png::Transformations::STRIP_16);
    let mut reader = decoder.read_info().map_err(|e| format!("PNG inválido: {e}"))?;
    let size = reader.output_buffer_size().ok_or("PNG demasiado grande")?;
    let mut buf = vec![0u8; size];
    let info = reader.next_frame(&mut buf).map_err(|e| format!("PNG inválido: {e}"))?;
    buf.truncate(info.buffer_size());

    let (color_space, channels, has_alpha) = match info.color_type {
        png::ColorType::Grayscale => ("DeviceGray", 1, false),
        png::ColorType::GrayscaleAlpha => ("DeviceGray", 2, true),
        png::ColorType::Rgb => ("DeviceRGB", 3, false),
        png::ColorType::Rgba => ("DeviceRGB", 4, true),
        png::ColorType::Indexed => return Err("PNG con paleta sin expandir".to_string()),
    };

    let (data, alpha) = if has_alpha {
        let color_channels = channels - 1;
        let pixels = buf.len() / channels;
        let mut color = Vec::with_capacity(pixels * color_channels);
        let mut alpha = Vec::with_capacity(pixels);
        for px in buf.chunks_exact(channels) {
            color.extend_from_slice(&px[..color_channels]);
            alpha.push(px[color_channels]);
        }
        // Sin transparencia real, no hace falta la máscara
        let alpha = if alpha.iter().all(|&a| a == 255) { None } else { Some(alpha) };
        (color, alpha)
    } else {
        (buf, None)
    };

    Ok(PdfImage {
        width: info.width,
        height: info.height,
        color_space,
        data,
        is_jpeg: false,
        alpha,
        invert_cmyk: false,
    })
}

fn abreviar(texto: &str) -> String {
    if texto.chars().count() <= 40 {
        texto.to_string()
    } else {
        format!("{}…", texto.chars().take(40).collect::<String>())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rechaza_formatos_desconocidos() {
        assert!(decode(b"GIF89a....").is_err());
    }

    #[test]
    fn lee_dimensiones_de_un_jpeg_minimo() {
        // SOI, SOF0 (alto 2, ancho 3, 3 canales), EOI
        let jpeg = [
            0xFF, 0xD8, 0xFF, 0xC0, 0x00, 0x11, 0x08, 0x00, 0x02, 0x00, 0x03, 0x03, 0x01, 0x22, 0x00, 0x02, 0x11,
            0x01, 0x03, 0x11, 0x01, 0xFF, 0xD9,
        ];
        let img = decode(&jpeg).unwrap();
        assert_eq!((img.width, img.height, img.color_space, img.is_jpeg), (3, 2, "DeviceRGB", true));
    }

    #[test]
    fn data_uri_y_base64() {
        let bytes = load_source("data:image/png;base64,iVBORw0KGgo=").unwrap();
        assert_eq!(&bytes[..4], &[0x89, b'P', b'N', b'G']);
        let bytes = load_source("iVBORw0KGgo=").unwrap();
        assert_eq!(&bytes[..4], &[0x89, b'P', b'N', b'G']);
    }
}
