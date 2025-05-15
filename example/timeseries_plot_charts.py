import sys

sys.path.append('../')
sys.path.append('../src')

from statistics import LinearRegression

from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split


import pandas as pd

from datetime import datetime

from timeseries import TimeSeriesModel  # Importa a classe TimeSeriesModel

start_time = datetime.now()  # Marca o tempo de início da execução

# Cria uma instância de TimeSeriesModel
tsm = TimeSeriesModel(
    data='data/hist_cambio_float.csv',  # Caminho para o arquivo CSV
    date_column='dt',  # Nome da coluna de datas
    value_columns=['purchaseValue', 'saleValue'],  # Lista de colunas de valores
    is_csv=True,  # Indica se os dados são de um arquivo CSV
    periods=30  # Número de períodos para previsão
)

# Executa o modelo
tsm.run()

# Salva os gráficos nos formatos desejados
plot_types = list(['line', 'scatter', 'bar'])  # Tipos de gráficos
formats = list(['html', 'png'])  # Formatos dos arquivos

tsm.save_plots(output_dir="./output", plot_types=plot_types, formats=formats)

# Imprime o tempo levado para executar o script
print("Time taken:", datetime.now() - start_time)