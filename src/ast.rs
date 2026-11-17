use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PageConfigAst {
    #[serde(default = "default_page_size")]
    pub size: String,
    #[serde(default = "default_orientation")]
    pub orientation: String,
    #[serde(default = "default_margin")]
    pub margin: f32,
    pub margin_top: Option<f32>,
    pub margin_bottom: Option<f32>,
    pub margin_left: Option<f32>,
    pub margin_right: Option<f32>,
}

fn default_page_size() -> String { "A4".to_string() }
fn default_orientation() -> String { "portrait".to_string() }
fn default_margin() -> f32 { 15.0 }

impl Default for PageConfigAst {
    fn default() -> Self {
        Self {
            size: default_page_size(),
            orientation: default_orientation(),
            margin: default_margin(),
            margin_top: None,
            margin_bottom: None,
            margin_left: None,
            margin_right: None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum ComponentAst {
    #[serde(rename = "text")]
    Text {
        value: String,
        style: Option<String>,
        alignment: Option<String>,
        color: Option<String>,
        font_size: Option<f32>,
        bold: Option<bool>,
        italic: Option<bool>,
        underline: Option<bool>,
    },
    #[serde(rename = "spacer")]
    Spacer {
        #[serde(default = "default_spacer_height")]
        height: f32,
    },
    #[serde(rename = "divider")]
    Divider {
        #[serde(default = "default_thickness")]
        thickness: f32,
        color: Option<String>,
        #[serde(default = "default_divider_margin")]
        margin: f32,
    },
    #[serde(rename = "column")]
    Column {
        #[serde(default)]
        items: Vec<ComponentAst>,
        #[serde(default)]
        spacing: f32,
    },
    #[serde(rename = "row")]
    Row {
        #[serde(default)]
        items: Vec<RowItemAst>,
        #[serde(default)]
        spacing: f32,
        vertical_alignment: Option<String>,
    },
    #[serde(rename = "container")]
    Container {
        child: Option<Box<ComponentAst>>,
        width: Option<f32>,
        height: Option<f32>,
        padding: Option<f32>,
        margin: Option<f32>,
        background: Option<String>,
        border_color: Option<String>,
        border_width: Option<f32>,
        border_radius: Option<f32>,
        alignment: Option<String>,
    },
    #[serde(rename = "table")]
    Table {
        columns: Vec<TableColumnAst>,
        source: Option<String>,
        data: Option<Vec<HashMap<String, serde_json::Value>>>,
        header_background: Option<String>,
        #[serde(default = "default_true")]
        zebra: bool,
        border_color: Option<String>,
        border_width: Option<f32>,
        #[serde(default = "default_true")]
        repeat_header: bool,
    },
    #[serde(rename = "qr")]
    Qr {
        value: String,
        #[serde(default = "default_qr_size")]
        size: f32,
        fill_color: Option<String>,
        back_color: Option<String>,
    },
    #[serde(rename = "barcode")]
    Barcode {
        value: String,
        #[serde(default = "default_barcode_type")]
        barcode_type: String,
        #[serde(default = "default_barcode_width")]
        width: f32,
        #[serde(default = "default_barcode_height")]
        height: f32,
        #[serde(default = "default_true")]
        include_text: bool,
    },
    #[serde(rename = "page_number")]
    PageNumber {
        #[serde(default = "default_page_number_format")]
        format: String,
        #[serde(default = "default_page_number_align")]
        alignment: String,
        style: Option<String>,
    },
    #[serde(rename = "image")]
    Image {
        source: String,
        width: Option<f32>,
        height: Option<f32>,
        fit: Option<String>,
        alignment: Option<String>,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(untagged)]
pub enum RowItemAst {
    Detailed {
        width: Option<f32>,
        #[serde(default = "default_flex")]
        flex: Option<f32>,
        item: ComponentAst,
    },
    Simple(ComponentAst),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TableColumnAst {
    pub title: String,
    pub field: Option<String>,
    pub width: Option<f32>,
    #[serde(default = "default_flex")]
    pub flex: Option<f32>,
    pub format: Option<String>,
    pub align: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DocumentDefinitionAst {
    #[serde(default)]
    pub page: PageConfigAst,
    pub header: Option<Box<ComponentAst>>,
    pub content: ContentAst,
    pub footer: Option<Box<ComponentAst>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(untagged)]
pub enum ContentAst {
    Single(Box<ComponentAst>),
    Multiple(Vec<ComponentAst>),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReportPayloadAst {
    pub document: Option<DocumentDefinitionAst>,
    pub template: Option<String>,
    pub data: Option<serde_json::Value>,
    #[serde(default = "default_format")]
    pub format: String,
}

fn default_spacer_height() -> f32 { 10.0 }
fn default_thickness() -> f32 { 1.0 }
fn default_divider_margin() -> f32 { 8.0 }
fn default_true() -> bool { true }
fn default_flex() -> Option<f32> { Some(1.0) }
fn default_qr_size() -> f32 { 80.0 }
fn default_barcode_type() -> String { "code128".to_string() }
fn default_barcode_width() -> f32 { 180.0 }
fn default_barcode_height() -> f32 { 40.0 }
fn default_page_number_format() -> String { "Página {page} de {total}".to_string() }
fn default_page_number_align() -> String { "right".to_string() }
fn default_format() -> String { "pdf".to_string() }
