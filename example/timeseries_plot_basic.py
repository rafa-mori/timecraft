import sys

sys.path.append('../')
sys.path.append('../src')

from statistics import LinearRegression

from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split



import pandas as pd

from datetime import datetime

from timeseries import TimeSeries  # Importa a classe TimeSeriesModel

start_time = datetime.now()  # Marca o tempo de início da execução

# Cria uma instância de TimeSeriesModel
model = TimeSeriesModel(
    data='data/hist_cambio_float.csv',  # Caminho para o arquivo CSV
    date_column='dt',  # Nome da coluna de datas
    value_columns=['purchaseValue', 'saleValue'],  # Lista de colunas de valores
    is_csv=True,  # Indica se os dados são de um arquivo CSV
    periods=30  # Número de períodos para previsão
)

# Executa o modelo
model.run()

# Obtém as previsões
fcst = model.get_forecast()

# Imprime as previsões
for key, value in fcst.items():
    print(key, value)

# Imprime o tempo levado para executar o script
print("Time taken:", datetime.now() - start_time)