import sys

sys.path.append('../../src')

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

# Load the data
# data = pd.read_csv('../data/hist_cambio_float.csv', header=None, names=['purchaseValue', 'saleValue', 'Date'])
data = pd.read_csv('data/hist_cambio_float.csv')

# Convert the data to a DataFrame
data = pd.DataFrame(data, columns=['purchaseValue', 'saleValue', 'dt'])

# Rename the columns
data = data.rename(columns={'purchaseValue': 'y', 'saleValue': 'yhat', 'dt': 'ds'})

# Remove rows with null values
data = data.dropna()

# Analyze the correlation
correlation = data['y'].corr(data['yhat'])
print(f'Correlation between purchaseValue and saleValue: {correlation}')

# Prepare the data for the regression model
X = data[['yhat']]  # Fix: Use 'yhat' as the feature
y = data['y']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train the linear regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Calculate the mean squared error
mse = mean_squared_error(y_test, y_pred)
print(f'Mean Squared Error: {mse}')

# Print the model coefficients
print(f'Model Coefficients: {model.coef_}')
print(f'Model Intercept: {model.intercept_}')
