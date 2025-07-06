"""
Example usage of the timecraft_ai package.
Make sure to install the package before running this script:
    pip install timecraft_ai
"""

from datetime import datetime

import timecraft_ai

start_time = datetime.now()

# Create an instance of TimeCraftModel
model = timecraft_ai.TimeCraftModel(
    data="data/hist_cambio_float.csv",  # Path to the CSV file
    date_column="dt",
    value_columns=["purchaseValue", "saleValue"],
    is_csv=True,
    periods=30,
)

# Run the model
model.run()

fcst = model.get_forecast()

for key, value in fcst.items():
    print(key, value)

print("Time taken:", datetime.now() - start_time)
print("Time taken:", datetime.now() - start_time)
