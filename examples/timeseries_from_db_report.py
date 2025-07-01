import sys

sys.path.append('../')
sys.path.append('../../src')

from statistics import LinearRegression

from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

import pandas as pd