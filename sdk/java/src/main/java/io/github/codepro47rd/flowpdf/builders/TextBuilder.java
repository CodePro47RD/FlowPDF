package io.github.codepro47rd.flowpdf.builders;

import java.util.LinkedHashMap;
import java.util.Map;

public class TextBuilder {
    private final Map<String, Object> text = new LinkedHashMap<>();

    public TextBuilder(String value) {
        text.put("type", "text");
        text.put("value", value != null ? value : "");
    }

    public TextBuilder style(String style) { text.put("style", style); return this; }
    public TextBuilder h1() { return style("h1"); }
    public TextBuilder h2() { return style("h2"); }
    public TextBuilder h3() { return style("h3"); }
    public TextBuilder body() { return style("body"); }
    public TextBuilder caption() { return style("caption"); }

    public TextBuilder align(String align) { text.put("alignment", align); return this; }
    public TextBuilder left() { return align("left"); }
    public TextBuilder center() { return align("center"); }
    public TextBuilder right() { return align("right"); }

    public TextBuilder color(String hexOrName) { text.put("color", hexOrName); return this; }
    public TextBuilder fontSize(double size) { text.put("font_size", size); return this; }
    public TextBuilder bold(boolean bold) { text.put("bold", bold); return this; }
    public TextBuilder bold() { return bold(true); }
    public TextBuilder italic(boolean italic) { text.put("italic", italic); return this; }
    public TextBuilder italic() { return italic(true); }
    public TextBuilder underline(boolean underline) { text.put("underline", underline); return this; }
    public TextBuilder underline() { return underline(true); }

    public Map<String, Object> build() {
        return new LinkedHashMap<>(text);
    }
}
