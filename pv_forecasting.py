import os
import sys
import pandas as pd
import numpy as np
import pvlib
import pickle
from xgboost import XGBRegressor
from sklearn.multioutput import MultiOutputRegressor
from pymongo import MongoClient
from datetime import datetime, timedelta

# 1. SETUP E CONEXÃO
mongo_password = os.getenv("MONGO_PWD", "nexusdbdeploytest")
mongo_uri = f"mongodb+srv://fdantascarmo:{mongo_password}@forecasting-db.lodb9.mongodb.net/?retryWrites=true&w=majority&appName=forecasting-db"

client = MongoClient(mongo_uri)
db = client["pv_forecasting"]
col_forecasts = db["pv_forecasts_new"]
col_models = db["pv_models"]

LAT, LON = 37.95, -8.87

# 2. LÓGICA DE CARGA OU TREINO
print("Verificando modelo no MongoDB...")
model_doc = col_models.find_one({"tipo": "XGBoost_MultiOutput", "local": "Porto_Sines"})

if model_doc:
    print("Modelo encontrado. Carregando pesos para inferência rápida...")
    model = pickle.loads(model_doc["model_binary"])
    MODO_TREINO = False
else:
    print("Modelo NÃO encontrado. Iniciando fase de treino pesado...")
    MODO_TREINO = True

# 3. SINCRONIZAÇÃO DINÂMICA COM O PVGIS
ano_teste = datetime.now().year
data_pvgis = None

while ano_teste >= 2005:
    try:
        # Se for modo treino, pegamos 5 anos. Se for inferência, apenas o ano atual.
        start_f = (ano_teste - 5) if MODO_TREINO else ano_teste
        data_pvgis, _ = pvlib.iotools.get_pvgis_hourly(
            latitude=LAT, longitude=LON, 
            start=start_f, end=ano_teste, map_variables=True
        )
        print(f"Fronteira de dados encontrada: {ano_teste}")
        break
    except Exception:
        ano_teste -= 1

if data_pvgis is None:
    print("Erro: Servidor PVGIS inacessível.")
    sys.exit()

# 4. PROCESSAMENTO DE DADOS
data_pvgis.index = data_pvgis.index.floor('h')
data_pvgis['poa_total'] = data_pvgis['poa_direct'] + data_pvgis['poa_sky_diffuse'] + data_pvgis['poa_ground_diffuse']

def extrair_features(df):
    df_daily = df.pivot_table(index=df.index.date, columns=df.index.hour, values='poa_total').dropna()
    df_temp = df.pivot_table(index=df.index.date, columns=df.index.hour, values='temp_air').dropna()
    df_wind = df.pivot_table(index=df.index.date, columns=df.index.hour, values='wind_speed').dropna()
    
    X = pd.DataFrame(index=df_daily.index)
    doy = pd.to_datetime(X.index).dayofyear
    X['day_sin'], X['day_cos'] = np.sin(2*np.pi*doy/365), np.cos(2*np.pi*doy/365)
    
    solar_pos = pvlib.solarposition.get_solarposition(
        pd.to_datetime(X.index).tz_localize('UTC') + pd.Timedelta(hours=12), LAT, LON)
    X['zenith_noon'] = solar_pos['zenith'].values
    
    X['lag_mean_rad'] = df_daily.mean(axis=1).shift(1)
    X['lag_temp_mean'] = df_temp.mean(axis=1).shift(1)
    X['lag_wind_mean'] = df_wind.mean(axis=1).shift(1)
    return X.dropna(), df_daily.loc[X.dropna().index]

X_data, Y_data = extrair_features(data_pvgis)

# 5. EXECUÇÃO DO TREINO (SE NECESSÁRIO)
if MODO_TREINO:
    print(f"Treinando XGBoost com {len(X_data)} dias de histórico...")
    model = MultiOutputRegressor(XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=6))
    model.fit(X_data, Y_data)
    
    col_models.update_one(
        {"tipo": "XGBoost_MultiOutput"},
        {"$set": {"model_binary": pickle.dumps(model), "data_treino": datetime.now()}},
        upsert=True
    )
    print("Modelo no MongoDB Atlas.")

# 6. FORECAST PARA O DIA SEGUINTE
# Pegamos a última linha de informação real para prever o amanhã
X_final = X_data.iloc[[-1]]
data_base = X_data.index[-1]
target_date = data_base + timedelta(days=1)

y_pred = model.predict(X_final)[0]

doc_forecast = {
    "timestamp_execucao": datetime.now(),
    "data_previsao": target_date.strftime("%Y-%m-%d"),
    "dia_base_real": data_base.strftime("%Y-%m-%d"),
    "previsoes_horarias": [{"hora": i, "valor": float(np.round(v, 2))} for i, v in enumerate(y_pred)]
}

col_forecasts.update_one({"data_previsao": doc_forecast["data_previsao"]}, {"$set": doc_forecast}, upsert=True)
print(f"Sucesso! Forecast para {target_date} guardado.")
client.close()