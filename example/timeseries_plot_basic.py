"""
Exemplo de uso do pacote timecraft_ai para previsão básica.
Certifique-se de instalar o pacote antes de rodar este script:
    pip install timecraft_ai
"""
from datetime import datetime
from timecraft_ai import TimeCraftModel

start_time = datetime.now()

model = TimeCraftModel(
    data='data/hist_cambio_float.csv',
    date_column='dt',
    value_columns=['purchaseValue', 'saleValue'],
    is_csv=True,
    periods=30
)

model.run()
fcst = model.get_forecast()
for key, value in fcst.items():
    print(key, value)

print("Time taken:", datetime.now() - start_time)