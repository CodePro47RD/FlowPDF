using System;
using System.Collections.Generic;
using ReportForge.Client.Models;

namespace ReportForge.Client.Fluent
{
    public class ReportDocument
    {
        private readonly DocumentDefinition _document = new();

        public static ReportDocument Create(Action<PageSettingsBuilder>? configure = null)
        {
            var doc = new ReportDocument();
            if (configure != null)
            {
                var builder = new PageSettingsBuilder();
                configure(builder);
                doc._document.Page = builder.Build();
            }
            return doc;
        }

        public ReportDocument Page(Action<PageSettingsBuilder> configure)
        {
            var builder = new PageSettingsBuilder();
            configure(builder);
            _document.Page = builder.Build();
            return this;
        }

        public ReportDocument Header(Action<SingleContainerBuilder> configure)
        {
            var builder = new SingleContainerBuilder();
            configure(builder);
            _document.Header = builder.Build();
            return this;
        }

        public ReportDocument Header(ComponentDefinition component)
        {
            _document.Header = component;
            return this;
        }

        public ReportDocument Content(Action<ColumnBuilder> configure)
        {
            var builder = new ColumnBuilder();
            configure(builder);
            _document.Content = builder.Build();
            return this;
        }

        public ReportDocument Content(ComponentDefinition component)
        {
            _document.Content = component;
            return this;
        }

        public ReportDocument Footer(Action<SingleContainerBuilder> configure)
        {
            var builder = new SingleContainerBuilder();
            configure(builder);
            _document.Footer = builder.Build();
            return this;
        }

        public ReportDocument Footer(ComponentDefinition component)
        {
            _document.Footer = component;
            return this;
        }

        public DocumentDefinition Build() => _document;
    }

    public class PageSettingsBuilder
    {
        private readonly PageSettings _settings = new();

        public PageSettingsBuilder Size(string size)
        {
            _settings.Size = size;
            return this;
        }

        public PageSettingsBuilder A4() => Size("A4");
        public PageSettingsBuilder Letter() => Size("Letter");
        public PageSettingsBuilder Legal() => Size("Legal");
        public PageSettingsBuilder A3() => Size("A3");
        public PageSettingsBuilder A5() => Size("A5");

        public PageSettingsBuilder Orientation(string orientation)
        {
            _settings.Orientation = orientation;
            return this;
        }

        public PageSettingsBuilder Portrait() => Orientation("portrait");
        public PageSettingsBuilder Landscape() => Orientation("landscape");

        public PageSettingsBuilder Margin(double margin)
        {
            _settings.Margin = margin;
            return this;
        }

        public PageSettingsBuilder Margins(double top, double right, double bottom, double left)
        {
            _settings.MarginTop = top;
            _settings.MarginRight = right;
            _settings.MarginBottom = bottom;
            _settings.MarginLeft = left;
            return this;
        }

        public PageSettings Build() => _settings;
    }
}
