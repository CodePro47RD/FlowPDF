use crate::ast::ChartSeriesAst;
use crate::core::{Color, Rect, Size};
use crate::pdf_engine::PdfOp;

pub struct ChartTheme {
    pub bg_color: Color,
    pub border_color: Color,
    pub grid_color: Color,
    pub text_primary: Color,
    pub text_secondary: Color,
}

impl ChartTheme {
    pub fn light() -> Self {
        Self {
            bg_color: Color::rgb(0.98, 0.985, 0.99),
            border_color: Color::rgb(0.88, 0.91, 0.94),
            grid_color: Color::rgb(0.89, 0.91, 0.94),
            text_primary: Color::rgb(0.06, 0.09, 0.16),
            text_secondary: Color::rgb(0.39, 0.45, 0.55),
        }
    }

    pub fn dark() -> Self {
        Self {
            bg_color: Color::rgb(0.06, 0.09, 0.16),
            border_color: Color::rgb(0.12, 0.16, 0.23),
            grid_color: Color::rgb(0.12, 0.16, 0.23),
            text_primary: Color::rgb(0.97, 0.98, 0.99),
            text_secondary: Color::rgb(0.58, 0.64, 0.72),
        }
    }

    pub fn from_str(s: &str) -> Self {
        if s.eq_ignore_ascii_case("dark") {
            Self::dark()
        } else {
            Self::light()
        }
    }
}

pub fn default_color(index: usize) -> Color {
    const PALETTE: [&str; 6] = [
        "#0066FF", // Azul eléctrico
        "#10B981", // Esmeralda
        "#F59E0B", // Ámbar
        "#8B5CF6", // Púrpura
        "#EC4899", // Rosa
        "#06B6D4", // Cian
    ];
    Color::from_hex(PALETTE[index % PALETTE.len()])
}

pub struct ChartRenderer;

impl ChartRenderer {
    pub fn render(
        chart_type: &str,
        title: Option<&str>,
        x: f32,
        y: f32,
        w: f32,
        h: f32,
        categories: Option<&[String]>,
        series: &[ChartSeriesAst],
        show_legend: bool,
        show_grid: bool,
        show_values: bool,
        theme_name: &str,
    ) -> (Vec<PdfOp>, Size) {
        let theme = ChartTheme::from_str(theme_name);
        let mut ops = Vec::new();

        // 1. Fondo y Borde del contenedor del gráfico
        ops.push(PdfOp::RectFill {
            rect: Rect::new(x, y, w, h),
            color: theme.bg_color,
        });
        ops.push(PdfOp::RectStroke {
            rect: Rect::new(x, y, w, h),
            thickness: 1.0,
            color: theme.border_color,
        });

        // 2. Título si existe
        let title_h = if let Some(t) = title {
            ops.push(PdfOp::Text {
                text: t.to_string(),
                font_ref: "/F2".to_string(),
                size: 11.0,
                x: x + 12.0,
                y: y + 10.0,
                color: theme.text_primary,
            });
            22.0
        } else {
            10.0
        };

        if series.is_empty() {
            return (ops, Size::new(w, h));
        }

        match chart_type {
            "pie" | "donut" => {
                Self::render_pie_or_donut(
                    chart_type == "donut",
                    &mut ops,
                    &theme,
                    series,
                    show_legend,
                    show_values,
                    x,
                    y + title_h,
                    w,
                    h - title_h,
                );
            }
            "line" | "area" => {
                Self::render_line_or_area(
                    chart_type == "area",
                    &mut ops,
                    &theme,
                    categories,
                    series,
                    show_legend,
                    show_grid,
                    show_values,
                    x,
                    y + title_h,
                    w,
                    h - title_h,
                );
            }
            _ => {
                // Default: Bar Chart
                Self::render_bar_chart(
                    &mut ops,
                    &theme,
                    categories,
                    series,
                    show_legend,
                    show_grid,
                    show_values,
                    x,
                    y + title_h,
                    w,
                    h - title_h,
                );
            }
        }

        (ops, Size::new(w, h))
    }

    fn render_bar_chart(
        ops: &mut Vec<PdfOp>,
        theme: &ChartTheme,
        categories: Option<&[String]>,
        series: &[ChartSeriesAst],
        show_legend: bool,
        show_grid: bool,
        show_values: bool,
        ox: f32,
        oy: f32,
        w: f32,
        h: f32,
    ) {
        let legend_w = if show_legend { 90.0 } else { 15.0 };
        let left_pad = 38.0;
        let right_pad = legend_w;
        let top_pad = 12.0;
        let bottom_pad = 22.0;

        let plot_x = ox + left_pad;
        let plot_y = oy + top_pad;
        let plot_w = (w - left_pad - right_pad).max(10.0);
        let plot_h = (h - top_pad - bottom_pad).max(10.0);

        // Encontrar valor máximo
        let mut max_val = 1.0f64;
        for s in series {
            for &v in &s.values {
                if v > max_val {
                    max_val = v;
                }
            }
        }
        // Redondear a escala agradable
        let scale_max = if max_val <= 10.0 {
            10.0
        } else if max_val <= 100.0 {
            ((max_val / 20.0).ceil() * 20.0).max(20.0)
        } else {
            let magnitude = 10f64.powf((max_val.log10().floor() - 1.0).max(0.0));
            (max_val / magnitude).ceil() * magnitude
        };

        // Dibujar Cuadrícula y Escala Y
        let grid_steps = 4;
        for i in 0..=grid_steps {
            let frac = i as f32 / grid_steps as f32;
            let line_y = plot_y + plot_h - (frac * plot_h);
            let val = (frac as f64) * scale_max;

            if show_grid {
                ops.push(PdfOp::Line {
                    x1: plot_x,
                    y1: line_y,
                    x2: plot_x + plot_w,
                    y2: line_y,
                    thickness: 0.5,
                    color: theme.grid_color,
                });
            }

            let label = if val >= 1000.0 {
                format!("{:.1}k", val / 1000.0)
            } else {
                format!("{:.0}", val)
            };
            let text_x = ox + 6.0;
            ops.push(PdfOp::Text {
                text: label,
                font_ref: "/F1".to_string(),
                size: 7.5,
                x: text_x,
                y: line_y - 3.5,
                color: theme.text_secondary,
            });
        }

        // Determinar número de categorías
        let num_cats = if let Some(cats) = categories {
            cats.len()
        } else {
            series.iter().map(|s| s.values.len()).max().unwrap_or(1)
        };

        if num_cats == 0 {
            return;
        }

        let cat_slot_w = plot_w / num_cats as f32;
        let group_padding = cat_slot_w * 0.18;
        let available_group_w = cat_slot_w - (group_padding * 2.0);
        let num_series = series.len();
        let bar_w = (available_group_w / num_series as f32).max(2.0);

        for cat_idx in 0..num_cats {
            let group_x = plot_x + (cat_idx as f32 * cat_slot_w) + group_padding;

            for (s_idx, s) in series.iter().enumerate() {
                let val = s.values.get(cat_idx).copied().unwrap_or(0.0);
                let bar_h = ((val / scale_max) as f32 * plot_h).max(0.0);
                let bar_x = group_x + (s_idx as f32 * bar_w);
                let bar_y = plot_y + plot_h - bar_h;

                let color = s
                    .color
                    .as_deref()
                    .map(Color::from_hex)
                    .unwrap_or_else(|| default_color(s_idx));

                ops.push(PdfOp::RectFill {
                    rect: Rect::new(bar_x, bar_y, bar_w * 0.92, bar_h),
                    color,
                });

                if show_values && bar_h > 10.0 {
                    let v_str = if val >= 1000.0 {
                        format!("{:.1}k", val / 1000.0)
                    } else {
                        format!("{:.0}", val)
                    };
                    let text_w = v_str.len() as f32 * 4.0;
                    ops.push(PdfOp::Text {
                        text: v_str,
                        font_ref: "/F1".to_string(),
                        size: 6.5,
                        x: (bar_x + (bar_w * 0.92 - text_w) / 2.0).max(bar_x),
                        y: bar_y - 8.0,
                        color: theme.text_primary,
                    });
                }
            }

            // Etiqueta de la categoría
            if let Some(cats) = categories {
                if let Some(cat_name) = cats.get(cat_idx) {
                    let text_w = cat_name.len() as f32 * 4.2;
                    let text_x = group_x + (available_group_w - text_w) / 2.0;
                    ops.push(PdfOp::Text {
                        text: cat_name.clone(),
                        font_ref: "/F1".to_string(),
                        size: 7.5,
                        x: text_x,
                        y: plot_y + plot_h + 6.0,
                        color: theme.text_secondary,
                    });
                }
            }
        }

        // Dibujar Leyenda
        if show_legend {
            let leg_x = ox + w - legend_w + 8.0;
            let mut leg_y = plot_y + 4.0;
            for (idx, s) in series.iter().enumerate() {
                let color = s
                    .color
                    .as_deref()
                    .map(Color::from_hex)
                    .unwrap_or_else(|| default_color(idx));
                ops.push(PdfOp::RectFill {
                    rect: Rect::new(leg_x, leg_y + 1.0, 7.0, 7.0),
                    color,
                });
                ops.push(PdfOp::Text {
                    text: s.name.clone(),
                    font_ref: "/F1".to_string(),
                    size: 7.5,
                    x: leg_x + 11.0,
                    y: leg_y,
                    color: theme.text_primary,
                });
                leg_y += 14.0;
            }
        }
    }

    fn render_line_or_area(
        is_area: bool,
        ops: &mut Vec<PdfOp>,
        theme: &ChartTheme,
        categories: Option<&[String]>,
        series: &[ChartSeriesAst],
        show_legend: bool,
        show_grid: bool,
        show_values: bool,
        ox: f32,
        oy: f32,
        w: f32,
        h: f32,
    ) {
        let legend_w = if show_legend { 90.0 } else { 15.0 };
        let left_pad = 38.0;
        let right_pad = legend_w;
        let top_pad = 12.0;
        let bottom_pad = 22.0;

        let plot_x = ox + left_pad;
        let plot_y = oy + top_pad;
        let plot_w = (w - left_pad - right_pad).max(10.0);
        let plot_h = (h - top_pad - bottom_pad).max(10.0);

        let mut max_val = 1.0f64;
        for s in series {
            for &v in &s.values {
                if v > max_val {
                    max_val = v;
                }
            }
        }
        let scale_max = if max_val <= 10.0 {
            10.0
        } else {
            let magnitude = 10f64.powf((max_val.log10().floor() - 1.0).max(0.0));
            (max_val / magnitude).ceil() * magnitude
        };

        // Grid
        let grid_steps = 4;
        for i in 0..=grid_steps {
            let frac = i as f32 / grid_steps as f32;
            let line_y = plot_y + plot_h - (frac * plot_h);
            let val = (frac as f64) * scale_max;

            if show_grid {
                ops.push(PdfOp::Line {
                    x1: plot_x,
                    y1: line_y,
                    x2: plot_x + plot_w,
                    y2: line_y,
                    thickness: 0.5,
                    color: theme.grid_color,
                });
            }

            let label = format!("{:.0}", val);
            ops.push(PdfOp::Text {
                text: label,
                font_ref: "/F1".to_string(),
                size: 7.5,
                x: ox + 6.0,
                y: line_y - 3.5,
                color: theme.text_secondary,
            });
        }

        let num_points = categories.map(|c| c.len()).unwrap_or_else(|| {
            series.iter().map(|s| s.values.len()).max().unwrap_or(1)
        });

        if num_points <= 1 {
            return;
        }

        let step_x = plot_w / (num_points - 1) as f32;

        for (s_idx, s) in series.iter().enumerate() {
            let color = s
                .color
                .as_deref()
                .map(Color::from_hex)
                .unwrap_or_else(|| default_color(s_idx));

            let mut prev_pt: Option<(f32, f32)> = None;

            for (p_idx, &val) in s.values.iter().enumerate() {
                let px = plot_x + (p_idx as f32 * step_x);
                let py = plot_y + plot_h - ((val / scale_max) as f32 * plot_h);

                if let Some((prev_x, prev_y)) = prev_pt {
                    // Línea continua entre puntos
                    ops.push(PdfOp::Line {
                        x1: prev_x,
                        y1: prev_y,
                        x2: px,
                        y2: py,
                        thickness: 2.0,
                        color,
                    });

                    if is_area {
                        // Sombra de área vertical simple bajo el segmento
                        let baseline_y = plot_y + plot_h;
                        let area_color = Color::rgba(color.r, color.g, color.b, 0.15);
                        let mid_y = (prev_y + py) / 2.0;
                        ops.push(PdfOp::RectFill {
                            rect: Rect::new(prev_x, mid_y, px - prev_x, baseline_y - mid_y),
                            color: area_color,
                        });
                    }
                }

                // Punto destacado (marcador)
                ops.push(PdfOp::RectFill {
                    rect: Rect::new(px - 2.5, py - 2.5, 5.0, 5.0),
                    color,
                });

                if show_values {
                    let v_str = format!("{:.0}", val);
                    ops.push(PdfOp::Text {
                        text: v_str,
                        font_ref: "/F1".to_string(),
                        size: 6.5,
                        x: px - 6.0,
                        y: py - 9.0,
                        color: theme.text_primary,
                    });
                }

                prev_pt = Some((px, py));
            }
        }

        // Categorías en X
        if let Some(cats) = categories {
            for (idx, cat) in cats.iter().enumerate() {
                let px = plot_x + (idx as f32 * step_x);
                let text_w = cat.len() as f32 * 4.2;
                ops.push(PdfOp::Text {
                    text: cat.clone(),
                    font_ref: "/F1".to_string(),
                    size: 7.5,
                    x: px - (text_w / 2.0),
                    y: plot_y + plot_h + 6.0,
                    color: theme.text_secondary,
                });
            }
        }

        // Leyenda
        if show_legend {
            let leg_x = ox + w - legend_w + 8.0;
            let mut leg_y = plot_y + 4.0;
            for (idx, s) in series.iter().enumerate() {
                let color = s
                    .color
                    .as_deref()
                    .map(Color::from_hex)
                    .unwrap_or_else(|| default_color(idx));
                ops.push(PdfOp::RectFill {
                    rect: Rect::new(leg_x, leg_y + 1.0, 7.0, 7.0),
                    color,
                });
                ops.push(PdfOp::Text {
                    text: s.name.clone(),
                    font_ref: "/F1".to_string(),
                    size: 7.5,
                    x: leg_x + 11.0,
                    y: leg_y,
                    color: theme.text_primary,
                });
                leg_y += 14.0;
            }
        }
    }

    fn render_pie_or_donut(
        is_donut: bool,
        ops: &mut Vec<PdfOp>,
        theme: &ChartTheme,
        series: &[ChartSeriesAst],
        show_legend: bool,
        _show_values: bool,
        ox: f32,
        oy: f32,
        w: f32,
        h: f32,
    ) {
        let legend_w = if show_legend { 110.0 } else { 15.0 };
        let plot_w = w - legend_w;
        let radius = (plot_w.min(h) / 2.0 - 15.0).max(10.0);
        let center_x = ox + (plot_w / 2.0);
        let center_y = oy + (h / 2.0);

        // Sumar valores
        let total_sum: f64 = series
            .iter()
            .map(|s| s.values.first().copied().unwrap_or(0.0))
            .sum();

        if total_sum <= 0.0 {
            return;
        }

        let mut start_angle = -std::f32::consts::FRAC_PI_2; // Comenzar arriba (-90 grados)

        for (idx, s) in series.iter().enumerate() {
            let val = s.values.first().copied().unwrap_or(0.0);
            let slice_angle = ((val / total_sum) * 2.0 * std::f64::consts::PI) as f32;
            let end_angle = start_angle + slice_angle;

            let color = s
                .color
                .as_deref()
                .map(Color::from_hex)
                .unwrap_or_else(|| default_color(idx));

            // Dibujar sector aproximado con segmentos triangulares desde el centro
            let steps = ((slice_angle / (std::f32::consts::PI / 12.0)).ceil() as usize).max(3);
            let angle_step = slice_angle / steps as f32;

            for step in 0..steps {
                let a1 = start_angle + (step as f32 * angle_step);
                let a2 = a1 + angle_step;

                let x1 = center_x + radius * a1.cos();
                let y1 = center_y + radius * a1.sin();
                let x2 = center_x + radius * a2.cos();
                let y2 = center_y + radius * a2.sin();

                // Dibuja el trazo del sector
                ops.push(PdfOp::Line {
                    x1: center_x,
                    y1: center_y,
                    x2: x1,
                    y2: y1,
                    thickness: 1.0,
                    color,
                });
                ops.push(PdfOp::Line {
                    x1,
                    y1,
                    x2,
                    y2,
                    thickness: 1.5,
                    color,
                });
            }

            start_angle = end_angle;
        }

        // Si es Donut: agujero central con el color de fondo del tema
        if is_donut {
            let hole_r = radius * 0.52;
            ops.push(PdfOp::RectFill {
                rect: Rect::new(center_x - hole_r, center_y - hole_r, hole_r * 2.0, hole_r * 2.0),
                color: theme.bg_color,
            });
            ops.push(PdfOp::RectStroke {
                rect: Rect::new(center_x - hole_r, center_y - hole_r, hole_r * 2.0, hole_r * 2.0),
                thickness: 1.0,
                color: theme.border_color,
            });
        }

        // Leyenda con porcentajes
        if show_legend {
            let leg_x = ox + w - legend_w + 10.0;
            let mut leg_y = oy + (h / 2.0) - (series.len() as f32 * 8.0).max(10.0);

            for (idx, s) in series.iter().enumerate() {
                let val = s.values.first().copied().unwrap_or(0.0);
                let pct = (val / total_sum) * 100.0;
                let color = s
                    .color
                    .as_deref()
                    .map(Color::from_hex)
                    .unwrap_or_else(|| default_color(idx));

                ops.push(PdfOp::RectFill {
                    rect: Rect::new(leg_x, leg_y + 1.0, 7.0, 7.0),
                    color,
                });
                let text = format!("{} ({:.1}%)", s.name, pct);
                ops.push(PdfOp::Text {
                    text,
                    font_ref: "/F1".to_string(),
                    size: 7.5,
                    x: leg_x + 11.0,
                    y: leg_y,
                    color: theme.text_primary,
                });
                leg_y += 14.0;
            }
        }
    }
}
