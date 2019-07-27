import os
import numpy as np
import pandas as pd

from IPython.display import display, Javascript
from bokeh.io import output_notebook
from bokeh.embed import file_html
from bokeh.resources import CDN
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, CustomJS, Slider, HoverTool, Span
from bokeh.models.widgets import Select, DataTable, TableColumn, NumberFormatter
from bokeh.plotting import figure, show

output_notebook(hide_banner=True)

display(Javascript("""
if (!(document.createElement('canvas').getContext('webgl') || document.createElement('canvas').getContext('experimental-webgl')))
    alert('Your browser does not support WebGL. This could impact performance.');
"""))

# Spearman Correlation
if not os.path.isfile("spearman.tsv"):
    data = pd.read_csv("dataset.tsv", delimiter="\t")
    spearman = data.drop(data.columns[[0, 1]], axis=1).corr(method="spearman")
    spearman.to_csv("spearman.tsv", index=False, float_format="%.7f", sep="\t")

spearman = pd.read_csv("spearman.tsv", delimiter="\t").dropna()
corr = spearman.where(np.triu(np.ones(spearman.shape), k=1).astype(np.bool))
corr = corr.set_index(corr.columns)
corr = corr.stack().reset_index()
corr = corr.rename(columns={"level_0": "a", "level_1": "b", 0: "corr"}).sort_values("corr", ascending=False)
s1 = ColumnDataSource(corr)
s2 = ColumnDataSource(corr) # Original Data Source

# Make Plot
p = figure(
    webgl        = True,
    tools        = "box_zoom,box_select,hover,reset",
    active_drag  = "box_select",
    title        = "Chromosome Pairs",
    y_axis_label = "Correlation",
    x_range      = (0, len(corr)))

p.title.align = "center"
p.xaxis.visible = False
p.yaxis.minor_tick_line_color = None
p.circle(corr.index, "corr", source=s1)
p.select(HoverTool).tooltips = [
    ("A", "@a"),
    ("B", "@b"),
    ("Correlation", "@corr")
]

# Make Table
columns = [
    TableColumn(field="a",    title="a",    sortable=True),
    TableColumn(field="b",    title="b",    sortable=True),
    TableColumn(field="corr", title="corr", sortable=True, formatter=NumberFormatter(format="0.000"))]
dtable = DataTable(row_headers=False, source=s1, columns=columns)

# Input Controls
callback = CustomJS(args=dict(s1=s1, s2=s2, dtable=dtable), code="""
    var val = cb_obj.value;
    var d1  = s1.data;
    var d2  = s2.data;
    d1.a    = [];
    d1.b    = [];
    d1.corr = [];
    for (var i = 0; i < d2["a"].length; ++i) {
        if (val == "All" || val == d2["a"][i]) {
            d1.a.push(d2.a[i]);
            d1.b.push(d2.b[i]);
            d1.corr.push(d2.corr[i]);
        }
    }
    s1.trigger("change");
    dtable.trigger("change");
""")

select = Select(title="Chromosome:", value="All", options=["All"] + spearman.columns.tolist(), callback=callback)
layout = layout([[p, widgetbox(select)], [dtable]])
show(layout)

html  = file_html(layout, CDN)
alert = """<script>
    if (!(document.createElement('canvas').getContext('webgl') ||
          document.createElement('canvas').getContext('experimental-webgl')))
        alert('Your browser does not support WebGL. This could impact performance.');
</script>
"""
head = html.find("    <head>")
html = html[:head] + alert + html[head:]
with open("dashboard.html", "w") as f:
    f.write(html)
    print("Dashboard saved.")
