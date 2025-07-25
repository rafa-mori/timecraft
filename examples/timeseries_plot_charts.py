"""
Example usage of the timecraft_ai package to save time series charts.
Make sure to install the package before running this script:
    pip install timecraft_ai
"""

from datetime import datetime

from timecraft_ai import TimeCraftModel

start_time = datetime.now()

tsm = TimeCraftModel(
    data="data/hist_cambio_float.csv",
    date_column="dt",
    value_columns=["purchaseValue", "saleValue"],
    is_csv=True,
    periods=30,
)

tsm.run()

plot_types = ["line", "scatter", "bar"]
formats = ["html", "png"]

tsm.save_plots(output_dir="output", plot_types=plot_types, formats=formats)

print("Time taken:", datetime.now() - start_time)
