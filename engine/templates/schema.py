"""
Pydantic v2 schemas for declarative JSON document templates in ReportForge.
Strict validation, versioning, and discriminated component unions.
"""

from __future__ import annotations
from typing import Annotated, Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


class PageConfigSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    size: str = Field(default="A4", description="Page size: A4, Letter, Legal, A3, A5")
    orientation: Literal["portrait", "landscape"] = Field(default="portrait")
    margin: float = Field(default=15.0, description="Global page margin in millimeters or points")
    margin_top: Optional[float] = None
    margin_bottom: Optional[float] = None
    margin_left: Optional[float] = None
    margin_right: Optional[float] = None


# =============================================================================
# Component Schemas
# =============================================================================

class TextComponentSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["text"]
    value: str
    style: Optional[str] = Field(default=None, description="Preset: h1, h2, h3, h4, body, caption, code")
    alignment: Optional[Literal["left", "center", "right", "justify"]] = "left"
    color: Optional[str] = None
    font_size: Optional[float] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    strike: Optional[bool] = None


class ImageComponentSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["image"]
    source: str = Field(description="File path, URL, asset key, or data:image base64 string")
    width: Optional[float] = None
    height: Optional[float] = None
    fit: Optional[Literal["contain", "cover", "fill", "none"]] = "contain"
    alignment: Optional[Literal["left", "center", "right"]] = "center"


class SpacerComponentSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["spacer"]
    height: float = Field(default=10.0)


class DividerComponentSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["divider"]
    thickness: float = Field(default=1.0)
    color: Optional[str] = None
    margin: float = Field(default=8.0)


class PageNumberComponentSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["page_number"]
    format: str = Field(default="Página {page} de {total}")
    alignment: Literal["left", "center", "right"] = "right"
    style: Optional[str] = "caption"


class RowItemSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")
    width: Optional[float] = None
    flex: Optional[float] = 1.0
    item: "AnyComponentSchema"


class ColumnComponentSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["column"]
    items: List["AnyComponentSchema"]
    spacing: float = Field(default=0.0)


class RowComponentSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["row"]
    items: List[Union["AnyComponentSchema", RowItemSchema]]
    spacing: float = Field(default=0.0)
    vertical_alignment: Optional[Literal["top", "middle", "bottom"]] = "top"


class ContainerComponentSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["container"]
    child: Optional["AnyComponentSchema"] = None
    width: Optional[float] = None
    height: Optional[float] = None
    padding: Optional[float] = None
    margin: Optional[float] = None
    background: Optional[str] = None
    border_color: Optional[str] = None
    border_width: Optional[float] = None
    border_radius: Optional[float] = None
    alignment: Optional[Literal["left", "center", "right"]] = None


class TableColumnSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str = Field(description="Header title display text")
    field: Optional[str] = Field(default=None, description="Data row dictionary field key")
    width: Optional[float] = None
    flex: Optional[float] = 1.0
    format: Optional[str] = Field(default=None, description="currency, number, percentage, date")
    align: Optional[Literal["left", "center", "right"]] = "left"


class TableComponentSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["table"]
    columns: List[TableColumnSchema]
    source: Optional[str] = Field(default=None, description="Key in context data containing rows list")
    data: Optional[List[Dict[str, Any]]] = None
    header_background: Optional[str] = None
    zebra: Optional[bool] = True
    zebra_color: Optional[str] = None
    border_color: Optional[str] = None
    border_width: Optional[float] = 0.5
    repeat_header: Optional[bool] = True


class ChartComponentSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["chart"]
    chart_type: Literal["bar", "line", "pie", "area", "multi_bar"] = "bar"
    title: Optional[str] = None
    labels: Optional[Union[List[str], str]] = None
    values: Optional[Union[List[float], str]] = None
    series: Optional[Union[List[Dict[str, Any]], str]] = None
    width: float = 400.0
    height: float = 200.0
    colors: Optional[List[str]] = None


class QRComponentSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["qr"]
    value: str
    size: float = 80.0
    fill_color: Optional[str] = None
    back_color: Optional[str] = None


class BarcodeComponentSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["barcode"]
    value: str
    barcode_type: str = "code128"
    width: float = 180.0
    height: float = 50.0
    include_text: bool = True


# Discriminated Union
AnyComponentSchema = Annotated[
    Union[
        TextComponentSchema,
        ImageComponentSchema,
        SpacerComponentSchema,
        DividerComponentSchema,
        PageNumberComponentSchema,
        ColumnComponentSchema,
        RowComponentSchema,
        ContainerComponentSchema,
        TableComponentSchema,
        ChartComponentSchema,
        QRComponentSchema,
        BarcodeComponentSchema,
    ],
    Field(discriminator="type"),
]


# Resolve recursive model references
ColumnComponentSchema.model_rebuild()
RowComponentSchema.model_rebuild()
ContainerComponentSchema.model_rebuild()


class DocumentTemplateSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    version: str = Field(default="1.0")
    page: PageConfigSchema = Field(default_factory=PageConfigSchema)
    header: Optional[AnyComponentSchema] = None
    content: Union[AnyComponentSchema, List[AnyComponentSchema]]
    footer: Optional[AnyComponentSchema] = None


class DocumentPayloadSchema(BaseModel):
    """Full HTTP request or standalone JSON payload schema."""
    model_config = ConfigDict(extra="ignore")

    version: str = Field(default="1.0")
    document: DocumentTemplateSchema
    data: Dict[str, Any] = Field(default_factory=dict)
