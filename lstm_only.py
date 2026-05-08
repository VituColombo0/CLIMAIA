import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error

# Load data
data_path = r'C:\Users\fdant\.spyder-py3\projects\wind forecasting\dados_limpos_interpolados.csv'
data = pd.read_csv(data_path)

# Date feature extraction
data['Date'] = pd.to_datetime(data['Date'])
data['Year'] = data['Date'].dt.year
data['Month'] = data['Date'].dt.month
data['Day'] = data['Date'].dt.day
data['Hour'] = data['Date'].dt.hour
data['Minute'] = data['Date'].dt.minute

# Add 24-hour lag (24h * 6 = 144 steps for 10-minute intervals)
lag_1d = 144
lag_7d = 144 * 7

data['Wspd_avg_83m_lag_24h'] = data['Wspd_avg_83m'].shift(lag_1d)
data['Wspd_avg_83m_lag_7d']  = data['Wspd_avg_83m'].shift(lag_7d)

# Drop rows with NA values due to lagging
data.dropna(inplace=True)

# Use only temporal features and lagged targets
features_to_keep = [
    'Year', 'Month', 'Day', 'Hour', 'Minute',
    'Wspd_avg_83m_lag_24h', 'Wspd_avg_83m_lag_7d'
]
X = data[features_to_keep]
y = data['Wspd_avg_83m']

# Set aside the last day (144 amostras) como validação
val_size = 144
X_train, X_val = X.iloc[:-val_size], X.iloc[-val_size:]
y_train, y_val = y.iloc[:-val_size], y.iloc[-val_size:]

# Scaling
scaler_X, scaler_y = MinMaxScaler(), MinMaxScaler()
X_train_scaled = scaler_X.fit_transform(X_train)
X_val_scaled = scaler_X.transform(X_val)
y_train_scaled = scaler_y.fit_transform(y_train.values.reshape(-1, 1))
y_val_scaled = scaler_y.transform(y_val.values.reshape(-1, 1))

# Reshape for LSTM [samples, time steps, features]
X_train_lstm = np.reshape(X_train_scaled, (X_train_scaled.shape[0], 1, X_train_scaled.shape[1]))
X_val_lstm = np.reshape(X_val_scaled, (X_val_scaled.shape[0], 1, X_val_scaled.shape[1]))

# Modelo LSTM
lstm_model = Sequential([
    LSTM(128, activation='relu', return_sequences=True, input_shape=(X_train_lstm.shape[1], X_train_lstm.shape[2])),
    Dropout(0.2),
    LSTM(64, activation='relu'),
    Dropout(0.2),
    Dense(1)
])
lstm_model.compile(optimizer=Adam(0.001), loss='mse')
lstm_model.fit(
    X_train_lstm, y_train_scaled, 
    epochs=1000,
    batch_size=32,
    validation_data=(X_val_lstm, y_val_scaled),
    verbose=1
)

# Previsão do modelo LSTM no dia-ahead
lstm_pred_scaled = lstm_model.predict(X_val_lstm)
lstm_pred = scaler_y.inverse_transform(lstm_pred_scaled)

# --- Modelo de persistência (lag de 7 dias) ---
# Aqui só precisamos comparar para o conjunto de validação:
# y_pred_persist = valor observado 7 dias antes
persist_pred = X_val['Wspd_avg_83m_lag_7d'].values

# Métricas de avaliação
rmse_lstm = np.sqrt(mean_squared_error(y_val, lstm_pred))
mape_lstm = mean_absolute_percentage_error(y_val, lstm_pred) * 100
rmse_persist = np.sqrt(mean_squared_error(y_val, persist_pred))
mape_persist = mean_absolute_percentage_error(y_val, persist_pred) * 100

print("LSTM Day-ahead RMSE:", rmse_lstm)
print("LSTM Day-ahead MAPE (%):", mape_lstm)
print("Persistência (lag 7d) RMSE:", rmse_persist)
print("Persistência (lag 7d) MAPE (%):", mape_persist)

# Visualização para o dia-ahead
plt.figure(figsize=(15, 6))
plt.plot(y_val.values, label='Actual', alpha=0.7)
plt.plot(lstm_pred, label='LSTM Predicted', alpha=0.7)
plt.plot(persist_pred, label='Persistence 7d (Baseline)', alpha=0.7)
plt.title('LSTM vs Persistence Model - Day-ahead Forecast (Last 24h)')
plt.xlabel('Sample (10-min interval)')
plt.ylabel('Wind Speed (Wspd_avg_83m)')
plt.legend()
plt.show()
