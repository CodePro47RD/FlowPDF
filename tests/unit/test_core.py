import pytest
from engine.core.geometry import Size, Rect, EdgeInsets, Point, HorizontalAlignment
from engine.core.constraints import BoxConstraints
from engine.core.colors import Color, Colors
from engine.core.units import mm, cm, inch, pt
from engine.core.page import PageSettings, PageSizes, PageOrientation


def test_units_conversion():
    assert pt(72) == 72.0
    assert inch(1) == 72.0
    assert round(mm(25.4), 1) == 72.0
    assert round(cm(2.54), 1) == 72.0


def test_geometry_rect_deflate_inflate():
    r = Rect(x=10, y=20, width=100, height=200)
    insets = EdgeInsets.all(10)
    deflated = r.deflate(insets)
    assert deflated.x == 20
    assert deflated.y == 30
    assert deflated.width == 80
    assert deflated.height == 180

    inflated = deflated.inflate(insets)
    assert inflated.x == 10
    assert inflated.y == 20
    assert inflated.width == 100
    assert inflated.height == 200


def test_box_constraints():
    bc = BoxConstraints(min_width=50, max_width=150, min_height=20, max_height=80)
    s1 = bc.constrain(Size(30, 100))
    assert s1.width == 50.0
    assert s1.height == 80.0

    tight = BoxConstraints.tight(Size(200, 100))
    assert tight.min_width == 200 and tight.max_width == 200


def test_colors_parsing():
    c_hex = Color.hex("#1E40AF")
    assert round(c_hex.red, 2) == round(0x1e / 255.0, 2)
    assert round(c_hex.green, 2) == round(0x40 / 255.0, 2)
    assert round(c_hex.blue, 2) == round(0xaf / 255.0, 2)
    assert c_hex.alpha == 1.0

    c_rgba = Color.hex("#1E40AF80")
    assert c_rgba.alpha < 1.0

    c_from_name = Color.from_any("primary")
    assert c_from_name == Colors.PRIMARY


def test_page_settings():
    ps = PageSettings(size=PageSizes.A4, orientation=PageOrientation.LANDSCAPE)
    dims = ps.dimensions
    assert dims.width > dims.height
    assert dims.width == PageSizes.A4.height
    assert dims.height == PageSizes.A4.width
