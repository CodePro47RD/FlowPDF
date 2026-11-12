/// High-performance Unicode to WinAnsi (Windows-1252 / ISO-8859-1) encoder for PDF.
/// Maps Unicode characters to Windows-1252 single-byte codes and serializes them
/// as ISO 32000-1 hexadecimal string literals `<HEX...>` for 100% compliant,
/// clean, escaping-free rendering of Spanish accents, Latin-1, currency symbols,
/// quotes, and punctuation in PDF Type1 fonts.

pub fn unicode_to_winansi_hex(text: &str) -> String {
    let mut hex = String::with_capacity(text.len() * 2 + 2);
    hex.push('<');

    for c in text.chars() {
        let b = char_to_winansi(c);
        use std::fmt::Write;
        write!(&mut hex, "{:02X}", b).unwrap();
    }

    hex.push('>');
    hex
}

pub fn char_to_winansi(c: char) -> u8 {
    let u = c as u32;

    // ASCII range (0x00..=0x7F)
    if u <= 0x7F {
        return u as u8;
    }

    // Direct Latin-1 supplement in Windows-1252 (0x00A0..=0x00FF)
    // Includes:
    // á (0xE1), é (0xE9), í (0xED), ó (0xF3), ú (0xFA)
    // Á (0xC1), É (0xC9), Í (0xCD), Ó (0xD3), Ú (0xDA)
    // ñ (0xF1), Ñ (0xD1), ü (0xFC), Ü (0xDC)
    // ¿ (0xBF), ¡ (0xA1), ° (0xB0), ± (0xB1), © (0xA9), ® (0xAE), etc.
    if (0x00A0..=0x00FF).contains(&u) {
        return u as u8;
    }

    // Windows-1252 specific mappings in the 0x80..=0x9F range
    match c {
        '€' => 0x80, // Euro sign
        '‚' => 0x82, // Single low-9 quotation mark
        'ƒ' => 0x83, // Latin small letter f with hook
        '„' => 0x84, // Double low-9 quotation mark
        '…' => 0x85, // Horizontal ellipsis
        '†' => 0x86, // Dagger
        '‡' => 0x87, // Double dagger
        'ˆ' => 0x88, // Modifier letter circumflex accent
        '‰' => 0x89, // Per mille sign
        'Š' => 0x8A, // Latin capital letter S with caron
        '‹' => 0x8B, // Single left-pointing angle quotation mark
        'Œ' => 0x8C, // Latin capital ligature OE
        'Ž' => 0x8E, // Latin capital letter Z with caron
        '‘' => 0x91, // Left single quotation mark
        '’' => 0x92, // Right single quotation mark
        '“' => 0x93, // Left double quotation mark
        '”' => 0x94, // Right double quotation mark
        '•' | '●' => 0x95, // Bullet / black circle
        '–' => 0x96, // En dash
        '—' => 0x97, // Em dash
        '˜' => 0x98, // Small tilde
        '™' => 0x99, // Trade mark sign
        'š' => 0x9A, // Latin small letter S with caron
        '›' => 0x9B, // Single right-pointing angle quotation mark
        'œ' => 0x9C, // Latin small ligature OE
        'ž' => 0x9E, // Latin small letter Z with caron
        'Ÿ' => 0x9F, // Latin capital letter Y with diaeresis

        // Common typographic fallbacks for symbols outside WinAnsi
        '✓' | '✔' => b'*',
        '★' | '☆' => b'*',
        '≠' => b'#',
        '≤' => b'<',
        '≥' => b'>',
        '→' => b'>',
        '←' => b'<',
        '«' => 0xAB,
        '»' => 0xBB,

        // Transliteration fallbacks for extended Latin characters
        'ā' | 'ă' | 'ą' => b'a',
        'Ā' | 'Ă' | 'Ą' => b'A',
        'ć' | 'č' | 'ĉ' | 'ċ' => b'c',
        'Ć' | 'Č' | 'Ĉ' | 'Ċ' => b'C',
        'ď' | 'đ' => b'd',
        'Ď' | 'Đ' => b'D',
        'ē' | 'ĕ' | 'ė' | 'ę' | 'ě' => b'e',
        'Ē' | 'Ĕ' | 'Ė' | 'Ę' | 'Ě' => b'E',
        'ğ' | 'ĝ' | 'ġ' | 'ģ' => b'g',
        'Ğ' | 'Ĝ' | 'Ġ' | 'Ģ' => b'G',
        'ī' | 'ĭ' | 'į' | 'ı' => b'i',
        'Ī' | 'Ĭ' | 'Į' | 'İ' => b'I',
        'ĺ' | 'ļ' | 'ľ' | 'ł' => b'l',
        'Ĺ' | 'Ļ' | 'Ľ' | 'Ł' => b'L',
        'ń' | 'ņ' | 'ň' => b'n',
        'Ń' | 'Ņ' | 'Ň' => b'N',
        'ō' | 'ŏ' | 'ő' => b'o',
        'Ō' | 'Ŏ' | 'Ő' => b'O',
        'ŕ' | 'ŗ' | 'ř' => b'r',
        'Ŕ' | 'Ŗ' | 'Ř' => b'R',
        'ś' | 'ŝ' | 'ş' | 'ș' => b's',
        'Ś' | 'Ŝ' | 'Ş' | 'Ș' => b'S',
        'ţ' | 'ť' | 'ț' => b't',
        'Ţ' | 'Ť' | 'Ț' => b'T',
        'ū' | 'ŭ' | 'ů' | 'ű' | 'ų' => b'u',
        'Ū' | 'Ŭ' | 'Ů' | 'Ű' | 'Ų' => b'U',
        'ź' | 'ż' => b'z',
        'Ź' | 'Ż' => b'Z',

        // Default replacement character
        _ => b'?',
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_spanish_accents_and_symbols() {
        let text = "Facturación áéíóú ñ Ñ ¿ ¡ €";
        let hex = unicode_to_winansi_hex(text);
        assert!(hex.starts_with('<'));
        assert!(hex.ends_with('>'));
        // 'ó' should be F3
        assert!(hex.contains("F3"));
        // 'ñ' should be F1
        assert!(hex.contains("F1"));
        // '€' should be 80
        assert!(hex.contains("80"));
    }
}
