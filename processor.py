import pandas as pd

#backend

df = pd.read_excel("res/exportacion.xlsx", header=5)
print(df.head())
print(len(df))

