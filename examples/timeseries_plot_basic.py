"""
Example usage of the timecraft_ai package for basic forecasting.
Make sure to install the package before running this script:
    pip install timecraft_ai
"""

from datetime import datetime

from timecraft_ai import TimeCraftModel

start_time = datetime.now()

model = TimeCraftModel(
    data="data/hist_cambio_float.csv",
    date_column="dt",
    value_columns=["purchaseValue", "saleValue"],
    is_csv=True,
    periods=30,
)

model.run()
fcst = model.get_forecast()
for key, value in fcst.items():
    print(key, value)

print("Time taken:", datetime.now() - start_time)
