import sys

sys.path.append('../')
sys.path.append('../src')

from datetime import datetime

from model import TimeSeriesModel  # Import the TimeSeriesModel class

start_time = datetime.now()

# Create an instance of TimeSeriesModel
tsm = TimeSeriesModel(
    data='../data/hist_cambio_float.csv',  # Path to the CSV file
    date_column='dt',
    value_columns=['purchaseValue', 'saleValue'],
    is_csv=True,
    periods=30
)

# Run the model
tsm.run()

# Save the plots in the desired formats
plot_types = list(['line', 'scatter', 'bar'])
formats = list(['html', 'png'])

out_dir = tsm.save_plots(output_dir="../output", plot_types=plot_types, formats=formats)

# Print the time taken to run the script
print("Time taken:", datetime.now() - start_time)
