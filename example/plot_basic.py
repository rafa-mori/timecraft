import sys

sys.path.append('../')
sys.path.append('../src')

from datetime import datetime

from model import TimeSeriesModel  # Import the TimeSeriesModel class

start_time = datetime.now()

# Create an instance of TimeSeriesModel
model = TimeSeriesModel(
    data='../../data/hist_cambio_float.csv',  # Path to the CSV file
    date_column='dt',
    value_columns=['purchaseValue', 'saleValue'],
    is_csv=True,
    periods=30
)

# Run the model
model.run()

fcst = model.get_forecast()

for key, value in fcst.items():
    print(key, value)

# Print the time taken to run the script
print("Time taken:", datetime.now() - start_time)

