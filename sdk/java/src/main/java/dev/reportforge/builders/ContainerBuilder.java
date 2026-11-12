package dev.reportforge.builders;

import java.util.LinkedHashMap;
import java.util.Map;

public class ContainerBuilder {
    private final Map<String, Object> container = new LinkedHashMap<>();

    public ContainerBuilder() {
        container.put("type", "container");
    }

    public ContainerBuilder padding(double padding) {
        container.put("padding", padding);
        return this;
    }

    public ContainerBuilder margin(double margin) {
        container.put("margin", margin);
        return this;
    }

    public ContainerBuilder background(String color) {
        container.put("background", color);
        return this;
    }

    public ContainerBuilder border(String color, double width, double radius) {
        container.put("border_color", color);
        container.put("border_width", width);
        container.put("border_radius", radius);
        return this;
    }

    public ContainerBuilder child(Map<String, Object> component) {
        container.put("child", component);
        return this;
    }

    public Map<String, Object> build() {
        return new LinkedHashMap<>(container);
    }
}
