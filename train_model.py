"""
CLIMAIA – Full Training Pipeline
Consolidates all data from the 4 folders and trains LSTM/XGBoost/Ensemble models.

Data sources:
  - /home/lirool/Downloads/2023/  (XLSX tratados, 12 meses)
  - /home/lirool/Downloads/2024/  (XLSX tratados, 12 meses)
  - /home/lirool/Downloads/2025/  (XLSX tratados, 12 meses)
  - /home/lirool/Downloads/Dados_Brutos/  (CSV brutos 2022-2025)

Usage:
  python train_model.py
"""

import os
import sys
import glob
import time
import json
import pickle
import warnings
import numpy as np
import pandas as pd
from datetime import datetime

warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# ─── Configuration ────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(DATA_DIR, "models_trained")
RESULTS_DIR = os.path.join(DATA_DIR, "results")

DOWNLOADS = "/home/lirool/Downloads"

# Treated XLSX folders (2023, 2024, 2025)
TREATED_DIRS = [
    os.path.join(DOWNLOADS, "2023"),
    os.path.join(DOWNLOADS, "2024"),
    os.path.join(DOWNLOADS, "2025"),
]

# Raw CSV folders (Dados_Brutos/2022_Bruto ... 2025_Bruto)
RAW_DIRS = [
    os.path.join(DOWNLOADS, "Dados_Brutos", "2022_Bruto"),
    os.path.join(DOWNLOADS, "Dados_Brutos", "2023_Bruto"),
    os.path.join(DOWNLOADS, "Dados_Brutos", "2024_Bruto"),
    os.path.join(DOWNLOADS, "Dados_Brutos", "2025_Bruto"),
]

# Target variables to train models for
TARGET_VARIABLES = [
    "temperatura",
    "vel_vento",
    "radiacao",
    "umidade",
]

# Treated column suffix (Akima + Savitzky-Golay interpolated)
TREATED_SUFFIX = "_akima_savgol"

# Training hyperparameters
LSTM_EPOCHS = 80
LSTM_BATCH = 64
LSTM_UNITS_1 = 64
LSTM_UNITS_2 = 32
XGB_ESTIMATORS = 200
XGB_DEPTH = 6
XGB_LR = 0.05
VAL_SPLIT = 0.15
MAX_SAMPLES = 50_000  # Cap for memory safety

# Data is 5-minute intervals: 288 samples/day
STEPS_PER_DAY = 288
STEPS_PER_HOUR = 12


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    icons = {"INFO": "ℹ️", "OK": "✅", "WARN": "⚠️", "ERR": "❌", "TRAIN": "🧠", "DATA": "📊"}
    icon = icons.get(level, "•")
    print(f"  [{ts}] {icon}  {msg}")


def banner(text):
    w = 60
    print(f"\n{'━' * w}")
    print(f"  {text}")
    print(f"{'━' * w}")


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1: DATA CONSOLIDATION
# ══════════════════════════════════════════════════════════════════════════════

def load_treated_xlsx(dirs):
    """Load all treated XLSX files into a single DataFrame."""
    banner("ETAPA 1/4 — Carregando dados TRATADOS (XLSX)")
    
    all_dfs = []
    total_files = 0
    
    for folder in dirs:
        if not os.path.isdir(folder):
            log(f"Pasta não encontrada: {folder}", "WARN")
            continue
        
        year = os.path.basename(folder)
        xlsx_files = sorted(glob.glob(os.path.join(folder, "**", "*_TRATADO.xlsx"), recursive=True))
        log(f"Ano {year}: {len(xlsx_files)} arquivos XLSX encontrados", "DATA")
        
        for f in xlsx_files:
            try:
                df = pd.read_excel(f, engine='openpyxl')
                all_dfs.append(df)
                total_files += 1
            except Exception as e:
                log(f"Erro lendo {os.path.basename(f)}: {e}", "WARN")
        
        log(f"  → {year} carregado ({len(xlsx_files)} arquivos)", "OK")
    
    if not all_dfs:
        log("Nenhum arquivo XLSX tratado encontrado!", "ERR")
        return None
    
    combined = pd.concat(all_dfs, ignore_index=True)
    log(f"Total tratados: {total_files} arquivos → {len(combined):,} registros", "OK")
    return combined


def load_raw_csv(dirs):
    """Load all raw CSV files into a single DataFrame."""
    banner("ETAPA 2/4 — Carregando dados BRUTOS (CSV)")
    
    all_dfs = []
    total_files = 0
    
    for folder in dirs:
        if not os.path.isdir(folder):
            log(f"Pasta não encontrada: {folder}", "WARN")
            continue
        
        year_name = os.path.basename(folder)
        csv_files = sorted(glob.glob(os.path.join(folder, "**", "*.csv"), recursive=True))
        log(f"{year_name}: {len(csv_files)} arquivos CSV encontrados", "DATA")
        
        for f in csv_files:
            try:
                df = pd.read_csv(f, sep=';')
                all_dfs.append(df)
                total_files += 1
            except Exception as e:
                log(f"Erro lendo {os.path.basename(f)}: {e}", "WARN")
        
        log(f"  → {year_name} carregado ({len(csv_files)} arquivos)", "OK")
    
    if not all_dfs:
        log("Nenhum arquivo CSV bruto encontrado!", "ERR")
        return None
    
    combined = pd.concat(all_dfs, ignore_index=True)
    log(f"Total brutos: {total_files} arquivos → {len(combined):,} registros", "OK")
    return combined


def prepare_dataset(df_treated, df_raw):
    """Merge and prepare the final training dataset."""
    banner("ETAPA 3/4 — Preparando dataset de treinamento")
    
    # Use treated data as primary (has interpolated columns)
    # Fall back to raw data for 2022 (which has no treated XLSX)
    
    # --- Prepare treated data ---
    if df_treated is not None and 'data_hora_dt' in df_treated.columns:
        df_treated['datetime'] = pd.to_datetime(df_treated['data_hora_dt'], errors='coerce')
    elif df_treated is not None and 'data_hora' in df_treated.columns:
        df_treated['datetime'] = pd.to_datetime(df_treated['data_hora'], format='%d/%m/%Y %H:%M', errors='coerce')
    
    # --- Prepare raw data (only use 2022 since 2023-2025 have treated versions) ---
    if df_raw is not None and 'data_hora' in df_raw.columns:
        df_raw['datetime'] = pd.to_datetime(df_raw['data_hora'], format='%d/%m/%Y %H:%M', errors='coerce')
        # Filter only 2022 from raw (2023-2025 are already covered by treated)
        df_raw_2022 = df_raw[df_raw['datetime'].dt.year == 2022].copy()
        log(f"Dados brutos 2022 filtrados: {len(df_raw_2022):,} registros", "DATA")
    else:
        df_raw_2022 = pd.DataFrame()
    
    # Build unified dataset with common columns
    # For treated: use the _akima_savgol columns (better quality)
    # For raw 2022: use original columns
    
    common_cols = ['datetime', 'temperatura', 'vel_vento', 'radiacao', 
                   'umidade', 'delta_pluv', 'dir_vento', 'max_velocidade']
    
    parts = []
    
    # Add treated data (prefer interpolated columns)
    if df_treated is not None and len(df_treated) > 0:
        treated_part = pd.DataFrame()
        treated_part['datetime'] = df_treated['datetime']
        
        for col in ['temperatura', 'vel_vento', 'radiacao', 'umidade', 
                     'delta_pluv', 'dir_vento', 'max_velocidade']:
            treated_col = col + TREATED_SUFFIX
            if treated_col in df_treated.columns:
                treated_part[col] = df_treated[treated_col].astype(float)
            elif col in df_treated.columns:
                treated_part[col] = df_treated[col].astype(float)
        
        parts.append(treated_part)
        log(f"Dados tratados (2023-2025): {len(treated_part):,} registros", "OK")
    
    # Add raw 2022 data
    if len(df_raw_2022) > 0:
        raw_part = pd.DataFrame()
        raw_part['datetime'] = df_raw_2022['datetime']
        for col in ['temperatura', 'vel_vento', 'radiacao', 'umidade',
                     'delta_pluv', 'dir_vento', 'max_velocidade']:
            if col in df_raw_2022.columns:
                raw_part[col] = df_raw_2022[col].astype(float)
        parts.append(raw_part)
        log(f"Dados brutos 2022: {len(raw_part):,} registros", "OK")
    
    if not parts:
        log("Nenhum dado disponível para treinamento!", "ERR")
        return None
    
    # Combine and sort
    dataset = pd.concat(parts, ignore_index=True)
    dataset = dataset.dropna(subset=['datetime'])
    dataset = dataset.sort_values('datetime').reset_index(drop=True)
    dataset = dataset.drop_duplicates(subset='datetime', keep='last')
    
    # Remove rows where all value columns are zero (sensor offline)
    value_cols = [c for c in dataset.columns if c != 'datetime']
    mask_all_zero = (dataset[value_cols] == 0).all(axis=1)
    n_zero = mask_all_zero.sum()
    if n_zero > 0:
        dataset = dataset[~mask_all_zero].reset_index(drop=True)
        log(f"Removidos {n_zero:,} registros com todos valores zerados", "WARN")
    
    # Fill small gaps with interpolation
    for col in value_cols:
        dataset[col] = dataset[col].interpolate(method='linear', limit=6)
    dataset = dataset.dropna()
    
    # Add temporal features
    dataset['hour'] = dataset['datetime'].dt.hour
    dataset['month'] = dataset['datetime'].dt.month
    dataset['day'] = dataset['datetime'].dt.day
    dataset['dayofweek'] = dataset['datetime'].dt.dayofweek
    dataset['hour_sin'] = np.sin(2 * np.pi * dataset['hour'] / 24)
    dataset['hour_cos'] = np.cos(2 * np.pi * dataset['hour'] / 24)
    dataset['month_sin'] = np.sin(2 * np.pi * dataset['month'] / 12)
    dataset['month_cos'] = np.cos(2 * np.pi * dataset['month'] / 12)
    
    date_range = f"{dataset['datetime'].min()} → {dataset['datetime'].max()}"
    log(f"Dataset final: {len(dataset):,} registros", "OK")
    log(f"Período: {date_range}", "DATA")
    log(f"Colunas: {list(dataset.columns)}", "DATA")
    
    # Save consolidated dataset
    os.makedirs(os.path.join(DATA_DIR, "treated"), exist_ok=True)
    csv_path = os.path.join(DATA_DIR, "treated", "dataset_consolidado.csv")
    dataset.to_csv(csv_path, index=False)
    log(f"Dataset salvo em: {csv_path}", "OK")
    
    return dataset


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2: MODEL TRAINING
# ══════════════════════════════════════════════════════════════════════════════

def build_features(dataset, target_col):
    """Build feature matrix with lags and temporal features for a target variable."""
    df = dataset.copy()
    
    # Lag features
    df['lag_1'] = df[target_col].shift(1)
    df['lag_2'] = df[target_col].shift(2)
    df['lag_6'] = df[target_col].shift(6)   # 30 min ago
    df['lag_12'] = df[target_col].shift(12)  # 1 hour ago
    df['lag_day'] = df[target_col].shift(STEPS_PER_DAY)  # 24h ago
    
    # Rolling statistics (1h window = 12 steps)
    df['rolling_mean_1h'] = df[target_col].rolling(12).mean()
    df['rolling_std_1h'] = df[target_col].rolling(12).std()
    
    # Rolling 6h
    df['rolling_mean_6h'] = df[target_col].rolling(72).mean()
    
    df = df.dropna()
    
    feature_cols = [
        'hour', 'month', 'day', 'dayofweek',
        'hour_sin', 'hour_cos', 'month_sin', 'month_cos',
        'lag_1', 'lag_2', 'lag_6', 'lag_12', 'lag_day',
        'rolling_mean_1h', 'rolling_std_1h', 'rolling_mean_6h',
    ]
    
    X = df[feature_cols]
    y = df[target_col]
    
    return X, y, feature_cols


def train_xgboost(X_train, y_train, X_val, y_val, var_name):
    """Train XGBoost model."""
    from xgboost import XGBRegressor
    
    log(f"Treinando XGBoost para '{var_name}'...", "TRAIN")
    t0 = time.time()
    
    model = XGBRegressor(
        n_estimators=XGB_ESTIMATORS,
        max_depth=XGB_DEPTH,
        learning_rate=XGB_LR,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        verbosity=0,
    )
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )
    
    elapsed = time.time() - t0
    
    # Metrics
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    y_pred = model.predict(X_val)
    rmse = np.sqrt(mean_squared_error(y_val, y_pred))
    mae = mean_absolute_error(y_val, y_pred)
    r2 = r2_score(y_val, y_pred)
    
    log(f"  XGBoost '{var_name}': RMSE={rmse:.4f} | MAE={mae:.4f} | R²={r2:.4f} ({elapsed:.1f}s)", "OK")
    
    return model, {'rmse': rmse, 'mae': mae, 'r2': r2}


def train_lstm(X_train, y_train, X_val, y_val, var_name, scaler_X, scaler_y):
    """Train LSTM model."""
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    
    log(f"Treinando LSTM para '{var_name}'...", "TRAIN")
    t0 = time.time()
    
    # Scale data
    X_train_sc = scaler_X.fit_transform(X_train)
    X_val_sc = scaler_X.transform(X_val)
    y_train_sc = scaler_y.fit_transform(y_train.values.reshape(-1, 1)).flatten()
    y_val_sc = scaler_y.transform(y_val.values.reshape(-1, 1)).flatten()
    
    # Reshape for LSTM [samples, timesteps, features]
    X_train_3d = X_train_sc.reshape((X_train_sc.shape[0], 1, X_train_sc.shape[1]))
    X_val_3d = X_val_sc.reshape((X_val_sc.shape[0], 1, X_val_sc.shape[1]))
    
    model = Sequential([
        LSTM(LSTM_UNITS_1, activation='relu', return_sequences=True,
             input_shape=(1, X_train_sc.shape[1])),
        Dropout(0.2),
        LSTM(LSTM_UNITS_2, activation='relu'),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(1)
    ])
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
    
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=0),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, verbose=0),
    ]
    
    history = model.fit(
        X_train_3d, y_train_sc,
        epochs=LSTM_EPOCHS,
        batch_size=LSTM_BATCH,
        validation_data=(X_val_3d, y_val_sc),
        callbacks=callbacks,
        verbose=0,
    )
    
    elapsed = time.time() - t0
    actual_epochs = len(history.history['loss'])
    
    # Metrics (inverse scaled)
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    y_pred_sc = model.predict(X_val_3d, verbose=0).flatten()
    y_pred = scaler_y.inverse_transform(y_pred_sc.reshape(-1, 1)).flatten()
    
    rmse = np.sqrt(mean_squared_error(y_val, y_pred))
    mae = mean_absolute_error(y_val, y_pred)
    r2 = r2_score(y_val, y_pred)
    
    log(f"  LSTM '{var_name}': RMSE={rmse:.4f} | MAE={mae:.4f} | R²={r2:.4f} ({actual_epochs} épocas, {elapsed:.1f}s)", "OK")
    
    return model, {'rmse': rmse, 'mae': mae, 'r2': r2, 'epochs_run': actual_epochs}


def train_all_models(dataset):
    """Train models for all target variables."""
    banner("ETAPA 4/4 — Treinamento dos Modelos de IA")
    
    from sklearn.preprocessing import MinMaxScaler
    
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    all_results = {}
    
    for var in TARGET_VARIABLES:
        if var not in dataset.columns:
            log(f"Variável '{var}' não encontrada no dataset. Pulando.", "WARN")
            continue
        
        log(f"\n{'─' * 40}", "INFO")
        log(f"Variável alvo: {var.upper()}", "TRAIN")
        log(f"{'─' * 40}", "INFO")
        
        # Build features
        X, y, feature_cols = build_features(dataset, var)
        
        # Cap samples
        if len(X) > MAX_SAMPLES:
            X = X.iloc[-MAX_SAMPLES:]
            y = y.iloc[-MAX_SAMPLES:]
            log(f"Dataset truncado para {MAX_SAMPLES:,} amostras mais recentes", "WARN")
        
        log(f"Amostras: {len(X):,} | Features: {len(feature_cols)}", "DATA")
        
        # Train/Val split (chronological)
        val_size = int(len(X) * VAL_SPLIT)
        X_train, X_val = X.iloc[:-val_size], X.iloc[-val_size:]
        y_train, y_val = y.iloc[:-val_size], y.iloc[-val_size:]
        
        log(f"Treino: {len(X_train):,} | Validação: {len(X_val):,}", "DATA")
        
        var_results = {'variable': var, 'train_size': len(X_train), 'val_size': len(X_val)}
        
        # ── Train XGBoost ──
        xgb_model, xgb_metrics = train_xgboost(X_train, y_train, X_val, y_val, var)
        var_results['xgboost'] = xgb_metrics
        
        # Save XGBoost
        xgb_path = os.path.join(MODELS_DIR, f"xgboost_{var}.pkl")
        with open(xgb_path, 'wb') as f:
            pickle.dump(xgb_model, f)
        
        # ── Train LSTM ──
        scaler_X = MinMaxScaler()
        scaler_y = MinMaxScaler()
        
        lstm_model, lstm_metrics = train_lstm(X_train, y_train, X_val, y_val, var, scaler_X, scaler_y)
        var_results['lstm'] = lstm_metrics
        
        # Save LSTM + scalers
        lstm_path = os.path.join(MODELS_DIR, f"lstm_{var}.keras")
        lstm_model.save(lstm_path)
        
        scalers_path = os.path.join(MODELS_DIR, f"scalers_{var}.pkl")
        with open(scalers_path, 'wb') as f:
            pickle.dump({'scaler_X': scaler_X, 'scaler_y': scaler_y}, f)
        
        # ── Ensemble metrics ──
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        
        X_val_sc = scaler_X.transform(X_val)
        X_val_3d = X_val_sc.reshape((X_val_sc.shape[0], 1, X_val_sc.shape[1]))
        
        y_xgb = xgb_model.predict(X_val)
        y_lstm_sc = lstm_model.predict(X_val_3d, verbose=0).flatten()
        y_lstm = scaler_y.inverse_transform(y_lstm_sc.reshape(-1, 1)).flatten()
        
        y_ensemble = 0.5 * y_xgb + 0.5 * y_lstm
        ens_rmse = np.sqrt(mean_squared_error(y_val, y_ensemble))
        ens_mae = mean_absolute_error(y_val, y_ensemble)
        ens_r2 = r2_score(y_val, y_ensemble)
        
        var_results['ensemble'] = {'rmse': ens_rmse, 'mae': ens_mae, 'r2': ens_r2}
        log(f"  Ensemble '{var}': RMSE={ens_rmse:.4f} | MAE={ens_mae:.4f} | R²={ens_r2:.4f}", "OK")
        
        # Save feature columns config
        config_path = os.path.join(MODELS_DIR, f"config_{var}.json")
        with open(config_path, 'w') as f:
            json.dump({
                'feature_cols': feature_cols,
                'target': var,
                'steps_per_day': STEPS_PER_DAY,
                'trained_at': datetime.now().isoformat(),
                'train_samples': len(X_train),
                'val_samples': len(X_val),
            }, f, indent=2)
        
        all_results[var] = var_results
        log(f"Modelos para '{var}' salvos em {MODELS_DIR}", "OK")
    
    # ── Save training report ──
    report_path = os.path.join(RESULTS_DIR, "training_report.json")
    
    # Convert numpy types for JSON serialization
    def convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        return obj
    
    with open(report_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=convert)
    
    return all_results


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("\n" + "═" * 60)
    print("  🌩️  CLIMAIA — Pipeline de Treinamento Completo")
    print(f"  📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("═" * 60)
    
    t_start = time.time()
    
    # Step 1: Load treated XLSX
    df_treated = load_treated_xlsx(TREATED_DIRS)
    
    # Step 2: Load raw CSV
    df_raw = load_raw_csv(RAW_DIRS)
    
    # Step 3: Prepare unified dataset
    dataset = prepare_dataset(df_treated, df_raw)
    
    if dataset is None or len(dataset) == 0:
        log("Dataset vazio. Abortando treinamento.", "ERR")
        sys.exit(1)
    
    # Step 4: Train models
    results = train_all_models(dataset)
    
    # ── Final Summary ──
    elapsed = time.time() - t_start
    
    print("\n" + "═" * 60)
    print("  🎉  TREINAMENTO CONCLUÍDO!")
    print(f"  ⏱️  Tempo total: {elapsed/60:.1f} minutos")
    print("═" * 60)
    
    for var, res in results.items():
        print(f"\n  📊 {var.upper()}:")
        for model_name in ['xgboost', 'lstm', 'ensemble']:
            if model_name in res:
                m = res[model_name]
                print(f"     {model_name:10s} → RMSE: {m['rmse']:.4f} | MAE: {m['mae']:.4f} | R²: {m['r2']:.4f}")
    
    print(f"\n  📁 Modelos salvos em: {MODELS_DIR}")
    print(f"  📁 Relatório em: {RESULTS_DIR}")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    main()
