#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Exemplo de uso do pacote timecraft_ai.
# Certifique-se de instalar o pacote antes de rodar este script:
#     pip install timecraft_ai
from datetime import datetime

from .src.timecraft_ai import TimeCraftModel

start_time = datetime.now()

# Crie uma instância de TimeCraftModel
model = TimeCraftModel(
    data="./example/data/hist_cambio_float.csv",  # Caminho para o arquivo CSV
    date_column="dt",
    value_columns=["purchaseValue", "saleValue"],
    is_csv=True,
    periods=30,
)

# Rode o modelo
model.run()

fcst = model.get_forecast()
for key, value in fcst.items():
    print(key, value)
print("Time taken:", datetime.now() - start_time)
