import io
import os
import pytest
from PIL import Image as PILImage
from engine import (
    Document,
    Text,
    Image,
    Table,
    TableColumn,
    TableRow,
    TableCell,
    Stack,
    QRCode,
    Barcode,
    Chart,
    Column,
    Spacer,
    PageNumber,
    Typography,
    Colors,
    HorizontalAlignment,
    mm,
)
from engine.core.geometry import Size
from engine.core.constraints import BoxConstraints
from engine.core.context import LayoutContext
from engine.core.page import PageSettings


@pytest.fixture
def layout_ctx():
    return LayoutContext(page_settings=PageSettings())


def test_image_component(layout_ctx):
    # Create test image in memory
    buf = io.BytesIO()
    img = PILImage.new("RGB", (200, 100), color=(30, 64, 175))
    img.save(buf, format="PNG")
    buf.seek(0)

    image_comp = Image(buf, width=100)
    size = image_comp.measure(BoxConstraints.loose(Size(500, 500)), layout_ctx)

    assert size.width == 100.0
    assert size.height == 50.0  # 2:1 aspect ratio


def test_table_measurement_and_splitting(layout_ctx):
    columns = [
        TableColumn("ID", width=50),
        TableColumn("Descripción", flex=2),
        TableColumn("Precio", flex=1, alignment=HorizontalAlignment.RIGHT),
    ]
    data = [
        {"ID": str(i), "Descripción": f"Producto de prueba {i}", "Precio": f"${i * 10}.00"}
        for i in range(1, 21)
    ]
    table = Table(columns=columns, data=data)
    size = table.measure(BoxConstraints.tight_for(width=500), layout_ctx)
    assert size.height > 200.0

    # Test splitting when available height is limited
    part1, part2 = table.split(100.0, layout_ctx)
    assert part1 is not None
    assert part2 is not None
    assert len(part1.rows) + len(part2.rows) == 20
    assert part1.repeat_header is True
    assert part2.repeat_header is True


def test_qr_code_generation(layout_ctx):
    qr = QRCode(data="https://github.com/reportforge", size=100)
    size = qr.measure(BoxConstraints.loose(Size(500, 500)), layout_ctx)
    assert size.width == 100.0
    assert size.height == 100.0


def test_barcode_generation(layout_ctx):
    bc = Barcode(code="123456789012", barcode_type="code128", width=150, height=45)
    size = bc.measure(BoxConstraints.loose(Size(500, 500)), layout_ctx)
    assert size.width == 150.0
    assert size.height == 45.0


def test_chart_generation(layout_ctx):
    chart = Chart(
        chart_type="bar",
        labels=["Ene", "Feb", "Mar", "Abr"],
        values=[1200, 1900, 3000, 2500],
        title="Ventas del Primer Trimestre",
        width=350,
        height=180,
    )
    size = chart.measure(BoxConstraints.loose(Size(500, 500)), layout_ctx)
    assert size.width == 350.0
    assert size.height == 180.0


def test_multipage_invoice_generation(tmp_path):
    output_pdf = tmp_path / "multipage_invoice.pdf"

    # Create 60 items so it naturally overflows into multiple pages
    items = [
        {"Item": f"SKU-{i:03d}", "Desc": f"Servicio especializado #{i}", "Cant": "1", "Total": f"${i * 25}.00"}
        for i in range(1, 61)
    ]

    doc = Document(title="Factura Comercial", author="ReportForge")
    doc.page(size="A4", orientation="portrait", margin=15)
    doc.header(
        Column([
            Text("FACTURA COMERCIAL", style=Typography.H2),
            Text("Tech Solutions Inc. • RNC 101-00000-1", style=Typography.CAPTION),
            Spacer(8),
        ])
    )
    doc.content(
        Column([
            Text("Detalle de Conceptos Facturados", style=Typography.H3),
            Spacer(8),
            Table(
                columns=[
                    TableColumn("Item", width=70),
                    TableColumn("Desc", flex=3),
                    TableColumn("Cant", width=50, alignment=HorizontalAlignment.CENTER),
                    TableColumn("Total", width=80, alignment=HorizontalAlignment.RIGHT),
                ],
                data=items,
                zebra_color=Colors.BG_ZEBRA,
                border_width=0.5,
                repeat_header=True,
            ),
        ])
    )
    doc.footer(
        PageNumber(format_str="Página {page} de {total}", alignment=HorizontalAlignment.RIGHT)
    )

    pdf_bytes = doc.generate(str(output_pdf))

    assert os.path.exists(output_pdf)
    assert os.path.getsize(output_pdf) > 2000
    assert pdf_bytes.startswith(b"%PDF-")
