use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct Point {
    pub x: f32,
    pub y: f32,
}

impl Point {
    pub fn new(x: f32, y: f32) -> Self {
        Self { x, y }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct Size {
    pub width: f32,
    pub height: f32,
}

impl Size {
    pub fn new(width: f32, height: f32) -> Self {
        Self { width, height }
    }

    pub fn zero() -> Self {
        Self { width: 0.0, height: 0.0 }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct Rect {
    pub x: f32,
    pub y: f32,
    pub width: f32,
    pub height: f32,
}

impl Rect {
    pub fn new(x: f32, y: f32, width: f32, height: f32) -> Self {
        Self { x, y, width, height }
    }

    pub fn from_origin_and_size(origin: Point, size: Size) -> Self {
        Self {
            x: origin.x,
            y: origin.y,
            width: size.width,
            height: size.height,
        }
    }

    pub fn deflate(&self, insets: EdgeInsets) -> Self {
        Self {
            x: self.x + insets.left,
            y: self.y + insets.top,
            width: (self.width - insets.horizontal()).max(0.0),
            height: (self.height - insets.vertical()).max(0.0),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize, Default)]
pub struct EdgeInsets {
    pub top: f32,
    pub right: f32,
    pub bottom: f32,
    pub left: f32,
}

impl EdgeInsets {
    pub fn all(value: f32) -> Self {
        Self { top: value, right: value, bottom: value, left: value }
    }

    pub fn symmetric(vertical: f32, horizontal: f32) -> Self {
        Self { top: vertical, bottom: vertical, left: horizontal, right: horizontal }
    }

    pub fn horizontal(&self) -> f32 {
        self.left + self.right
    }

    pub fn vertical(&self) -> f32 {
        self.top + self.bottom
    }
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct BoxConstraints {
    pub min_width: f32,
    pub max_width: f32,
    pub min_height: f32,
    pub max_height: f32,
}

impl BoxConstraints {
    pub fn new(min_width: f32, max_width: f32, min_height: f32, max_height: f32) -> Self {
        Self { min_width, max_width, min_height, max_height }
    }

    pub fn tight_for(width: Option<f32>, height: Option<f32>) -> Self {
        Self {
            min_width: width.unwrap_or(0.0),
            max_width: width.unwrap_or(f32::INFINITY),
            min_height: height.unwrap_or(0.0),
            max_height: height.unwrap_or(f32::INFINITY),
        }
    }

    pub fn constrain(&self, size: Size) -> Size {
        Size {
            width: size.width.clamp(self.min_width, self.max_width),
            height: size.height.clamp(self.min_height, self.max_height),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub struct Color {
    pub r: f32,
    pub g: f32,
    pub b: f32,
    pub a: f32,
}

impl Color {
    pub fn rgb(r: f32, g: f32, b: f32) -> Self {
        Self { r, g, b, a: 1.0 }
    }

    pub fn rgba(r: f32, g: f32, b: f32, a: f32) -> Self {
        Self { r, g, b, a }
    }

    pub fn from_hex(hex: &str) -> Self {
        let hex = hex.trim_start_matches('#');
        if hex.len() == 6 {
            let r = u8::from_str_radix(&hex[0..2], 16).unwrap_or(0) as f32 / 255.0;
            let g = u8::from_str_radix(&hex[2..4], 16).unwrap_or(0) as f32 / 255.0;
            let b = u8::from_str_radix(&hex[4..6], 16).unwrap_or(0) as f32 / 255.0;
            Self::rgb(r, g, b)
        } else if hex.len() == 8 {
            let r = u8::from_str_radix(&hex[0..2], 16).unwrap_or(0) as f32 / 255.0;
            let g = u8::from_str_radix(&hex[2..4], 16).unwrap_or(0) as f32 / 255.0;
            let b = u8::from_str_radix(&hex[4..6], 16).unwrap_or(0) as f32 / 255.0;
            let a = u8::from_str_radix(&hex[6..8], 16).unwrap_or(255) as f32 / 255.0;
            Self::rgba(r, g, b, a)
        } else {
            Self::rgb(0.0, 0.0, 0.0)
        }
    }

    pub fn black() -> Self { Self::rgb(0.0, 0.0, 0.0) }
    pub fn white() -> Self { Self::rgb(1.0, 1.0, 1.0) }
    pub fn transparent() -> Self { Self::rgba(0.0, 0.0, 0.0, 0.0) }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub enum PageSize {
    A4,
    Letter,
    Legal,
    A3,
    A5,
}

impl PageSize {
    pub fn dimensions(&self, orientation: &str) -> (f32, f32) {
        let (mut w, mut h) = match self {
            PageSize::A4 => (595.28, 841.89),
            PageSize::Letter => (612.0, 792.0),
            PageSize::Legal => (612.0, 1008.0),
            PageSize::A3 => (841.89, 1190.55),
            PageSize::A5 => (419.53, 595.28),
        };
        if orientation.eq_ignore_ascii_case("landscape") {
            std::mem::swap(&mut w, &mut h);
        }
        (w, h)
    }

    pub fn from_str(s: &str) -> Self {
        match s.to_uppercase().as_str() {
            "LETTER" => PageSize::Letter,
            "LEGAL" => PageSize::Legal,
            "A3" => PageSize::A3,
            "A5" => PageSize::A5,
            _ => PageSize::A4,
        }
    }
}
