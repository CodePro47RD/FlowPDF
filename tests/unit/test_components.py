import os
import pytest
from engine import (
    Document,
    Text,
    Container,
    Column,
    Row,
    Spacer,
    Divider,
    PageNumber,
    Typography,
    Colors,
    mm,
)
from engine.core.geometry import Size, Rect, EdgeInsets
from engine.core.constraints import BoxConstraints
from engine.core.context import LayoutContext
from engine.core.page import PageSettings


@pytest.fixture
def layout_ctx():
    return LayoutContext(page_settings=PageSettings())


def test_text_measurement_and_wrapping(layout_ctx):
    short_text = Text("Hello World", style=Typography.BODY)
    size = short_text.measure(BoxConstraints(max_width=300), layout_ctx)
    assert size.width > 0
    assert size.height > 0

    long_text = Text("Word " * 50, style=Typography.BODY)
    wrapped_size = long_text.measure(BoxConstraints(max_width=200), layout_ctx)
    assert wrapped_size.height > size.height


def test_container_padding_and_margin(layout_ctx):
    child = Text("Test", style=Typography.BODY)
    container = Container(child=child, padding=10.0, margin=5.0)
    size = container.measure(BoxConstraints(max_width=300), layout_ctx)
    child_size = child.measure(BoxConstraints(max_width=300), layout_ctx)

    assert size.width == pytest.approx(child_size.width + 30.0, abs=1.0)
    assert size.height == pytest.approx(child_size.height + 30.0, abs=1.0)


def test_column_layout(layout_ctx):
    col = Column(
        [
            Text("Line 1", style=Typography.BODY),
            Spacer(15),
            Text("Line 2", style=Typography.BODY),
        ],
        spacing=5.0,
    )
    size = col.measure(BoxConstraints(max_width=300), layout_ctx)
    assert size.height > 30.0


def test_row_flex_distribution(layout_ctx):
    row = (
        Row(spacing=10.0)
        .constant_item(100.0, Text("Fixed", style=Typography.BODY))
        .relative_item(1.0, Text("Col A", style=Typography.BODY))
        .relative_item(2.0, Text("Col B", style=Typography.BODY))
    )
    size = row.measure(BoxConstraints.tight_for(width=400), layout_ctx)
    assert size.width == 400.0


def test_fluent_document_pdf_generation(tmp_path):
    output_pdf = tmp_path / "test_document.pdf"

    doc = Document(title="Test Document", author="ReportForge Engine")
    doc.page(size="A4", orientation="portrait", margin=20)
    doc.header(
        Row([
            Text("REPORTFORGE DEMO", style=Typography.H3),
            PageNumber(alignment="right"),
        ])
    )
    doc.content(
        Column([
            Text("Bienvenido al Motor de Composición ReportForge", style=Typography.H1),
            Spacer(10),
            Divider(thickness=1.5, color=Colors.PRIMARY),
            Spacer(15),
            Text(
                "Este es un documento generado mediante la API fluida, "
                "con soporte para medición automática de cajas, envoltura de texto y separación de páginas.",
                style=Typography.BODY,
            ),
            Spacer(20),
            Row([
                Text("Columna Izquierda (Flex 1)", style=Typography.BODY_BOLD)
                .padding(all=8)
                .background(Colors.GRAY_100)
                .border(Colors.GRAY_300, 1),
                Text("Columna Derecha (Flex 2)", style=Typography.BODY)
                .padding(all=8)
                .background(Colors.PRIMARY_LIGHT.with_alpha(0.15))
                .border(Colors.PRIMARY, 1),
            ], spacing=12),
        ])
    )
    doc.footer(
        Text("ReportForge • Generador Universal de Documentos", style=Typography.CAPTION)
        .align_center()
    )

    pdf_bytes = doc.generate(str(output_pdf))

    assert os.path.exists(output_pdf)
    assert os.path.getsize(output_pdf) > 1000
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF-")
