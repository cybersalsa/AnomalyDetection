import pandas as pd
from adtk.data import validate_series
from adtk.visualization import plot
import matplotlib.pyplot as plt
from adtk.detector import SeasonalAD
from datetime import timedelta

df = pd.read_csv('CSV/ALBIG_elaborato.csv', parse_dates=True, squeeze=True)
df.rename(columns={'Unnamed: 0': 'DATE'}, inplace=True)

datetime_series = pd.to_datetime(df['DATE'])

# create datetime index passing the datetime series
datetime_index = pd.DatetimeIndex(datetime_series.values)

df_1 = df.set_index(datetime_index)

# somma dei capi d'abbigliamento venduti giorno per giorno
somma_1 = df_1.sum(axis=1, numeric_only=True)

# rimuovo i dati in eccesso dal dataframe
df_1.drop(['DATE', 'MAGLIE', 'CAMICIE', 'GONNE', 'PANTALONI', 'VESTITI', 'GIACCHE'], axis=1, inplace=True)

# inserisco la somma dei capi d'abbigliamento venduti precedentemente calcolata
df_1['Albig'] = somma_1

# LETTURA SECONDO CSV

df = pd.read_csv('CSV/ALGHE_elaborato.csv', parse_dates=True, squeeze=True)
df.rename(columns={'Unnamed: 0': 'DATE'}, inplace=True)
datetime_series = pd.to_datetime(df['DATE'])

# create datetime index passing the datetime series
datetime_index = pd.DatetimeIndex(datetime_series.values)

df_2 = df.set_index(datetime_index)

# somma dei capi d'abbigliamento venduti giorno per giorno
somma_2 = df_2.sum(axis=1, numeric_only=True)

# inserisco la somma dei capi d'abbigliamento venduti precedentemente calcolata
df_1['Alghe'] = somma_2

# LETTURA TERZO CSV

df = pd.read_csv('CSV/APRIL_elaborato.csv', parse_dates=True, squeeze=True)
df.rename(columns={'Unnamed: 0': 'DATE'}, inplace=True)
datetime_series = pd.to_datetime(df['DATE'])

# create datetime index passing the datetime series
datetime_index = pd.DatetimeIndex(datetime_series.values)

df_3 = df.set_index(datetime_index)

# somma dei capi d'abbigliamento venduti giorno per giorno
somma_3 = df_3.sum(axis=1, numeric_only=True)

# inserisco la somma dei capi d'abbigliamento venduti precedentemente calcolata
df_1['April'] = somma_3

# LETTURA QUARTO CSV

df = pd.read_csv('CSV/ARESE_elaborato.csv', parse_dates=True, squeeze=True)
df.rename(columns={'Unnamed: 0': 'DATE'}, inplace=True)
datetime_series = pd.to_datetime(df['DATE'])

# create datetime index passing the datetime series
datetime_index = pd.DatetimeIndex(datetime_series.values)

df_4 = df.set_index(datetime_index)

# somma dei capi d'abbigliamento venduti giorno per giorno
somma_4 = df_4.sum(axis=1, numeric_only=True)

# inserisco la somma dei capi d'abbigliamento venduti precedentemente calcolata
df_1['Arese'] = somma_4

s_train = validate_series(df_1)

# calcolo la derivata del segnale
diff = s_train.diff()

# analizzo l'andamento settimanale del segnale derivato
diff = diff.resample('W').sum()

# resample delle date con frequenza settimanale
df_1 = df_1.resample('W').sum()

# rilevo le anomalie e le mostro su grafico
seasonal_ad = SeasonalAD(freq=7)
anomalies = seasonal_ad.fit_detect(diff)
plot(diff, anomaly=anomalies, anomaly_color="red", anomaly_tag="marker")
plt.show()

# creo delle liste vuote che verranno usate per inserire le date delle anomalie rilevate
albig = []
alghe = []
april = []
arese = []

# itero per ogni anomalia rilevata
for index, row in anomalies.iterrows():
    if row['Albig']:
        # conversione di un hashable in data ed a seguire mi salvo il giorno iniziale e finale della settimana
        # inoltre, mi salvo il valore totale delle vendite effettuate quella settimana
        date = index.to_pydatetime().date()
        albig.append([pd.to_datetime(date - timedelta(days=6)), index, df_1.loc[index, 'Albig']])
    if row['Alghe']:
        date = index.to_pydatetime().date()
        alghe.append([pd.to_datetime(date - timedelta(days=6)), index, df_1.loc[index, 'Alghe']])
    if row['April']:
        date = index.to_pydatetime().date()
        april.append([pd.to_datetime(date - timedelta(days=6)), index, df_1.loc[index, 'April']])
    if row['Arese']:
        date = index.to_pydatetime().date()
        arese.append([pd.to_datetime(date - timedelta(days=6)), index, df_1.loc[index, 'Arese']])

# rendo le liste dei dataframe (per questione di costi conviene fare append su liste e poi trasformare in df)
albig_df = pd.DataFrame(albig, columns=['Settimana dal', 'al', 'Capi venduti'])
alghe_df = pd.DataFrame(alghe, columns=['Settimana dal', 'al', 'Capi venduti'])
april_df = pd.DataFrame(april, columns=['Settimana dal', 'al', 'Capi venduti'])
arese_df = pd.DataFrame(arese, columns=['Settimana dal', 'al', 'Capi venduti'])

# formatto le date da inserire nel file excel
albig_df['Settimana dal'] = albig_df['Settimana dal'].dt.strftime('%Y-%m-%d')
alghe_df['Settimana dal'] = alghe_df['Settimana dal'].dt.strftime('%Y-%m-%d')
april_df['Settimana dal'] = april_df['Settimana dal'].dt.strftime('%Y-%m-%d')
arese_df['Settimana dal'] = arese_df['Settimana dal'].dt.strftime('%Y-%m-%d')
albig_df['al'] = albig_df['al'].dt.strftime('%Y-%m-%d')
alghe_df['al'] = alghe_df['al'].dt.strftime('%Y-%m-%d')
april_df['al'] = april_df['al'].dt.strftime('%Y-%m-%d')
arese_df['al'] = arese_df['al'].dt.strftime('%Y-%m-%d')

anomalies_sheets = {'Albig': albig_df, 'Alghe': alghe_df, 'April': april_df, 'Arese': arese_df}

writer = pd.ExcelWriter('./anomalies.xlsx', engine='xlsxwriter')

for sheets in anomalies_sheets.keys():
    anomalies_sheets[sheets].to_excel(writer, sheet_name=sheets, index=False)

# scrivo su file
writer.save()
