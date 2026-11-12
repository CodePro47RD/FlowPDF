package dev.reportforge.builders;

import java.util.LinkedHashMap;
import java.util.Map;

public class PageConfigBuilder {
    private final Map<String, Object> config = new LinkedHashMap<>();

    public PageConfigBuilder() {
        config.put("size", "A4");
        config.put("orientation", "portrait");
        config.put("margin", 15.0);
    }

    public PageConfigBuilder size(String size) {
        config.put("size", size);
        return this;
    }

    public PageConfigBuilder a4() { return size("A4"); }
    public PageConfigBuilder letter() { return size("Letter"); }
    public PageConfigBuilder legal() { return size("Legal"); }
    public PageConfigBuilder a3() { return size("A3"); }
    public PageConfigBuilder a5() { return size("A5"); }

    public PageConfigBuilder orientation(String orientation) {
        config.put("orientation", orientation);
        return this;
    }

    public PageConfigBuilder portrait() { return orientation("portrait"); }
    public PageConfigBuilder landscape() { return orientation("landscape"); }

    public PageConfigBuilder margin(double margin) {
        config.put("margin", margin);
        return this;
    }

    public PageConfigBuilder margins(double top, double right, double bottom, double left) {
        config.put("margin_top", top);
        config.put("margin_right", right);
        config.put("margin_bottom", bottom);
        config.put("margin_left", left);
        return this;
    }

    public Map<String, Object> build() {
        return new LinkedHashMap<>(config);
    }
}
