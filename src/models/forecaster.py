"""
CLIMAIA – AI Prediction and Training Engine
Implements training and inference for LSTM, XGBoost, and Ensemble models.
"""

import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBRegressor
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import Callback
import tensorflow as tf

# Disable TensorFlow verbose logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


class GUIProgressCallback(Callback):
    """Keras callback to update GUI console during training."""
    def __init__(self, console_log_fn, total_epochs):
        super().__init__()
        self.console_log_fn = console_log_fn
        self.total_epochs = total_epochs

    def on_epoch_end(self, epoch, logs=None):
        loss = logs.get('loss', 0.0)
        val_loss = logs.get('val_loss', 0.0)
        # Log every 5 epochs or the first/last epochs
        if epoch == 0 or (epoch + 1) % 5 == 0 or (epoch + 1) == self.total_epochs:
            self.console_log_fn(f"  → Época {epoch + 1}/{self.total_epochs} - Perda: {loss:.5f} | Val Perda: {val_loss:.5f}")


class ClimaiaForecaster:
    """Wraps model training, persistence, and inference."""
    def __init__(self, model_type="LSTM", epochs=50):
        self.model_type = model_type
        self.epochs = epochs
        self.lstm_model = None
        self.xgb_model = None
        self.scaler_X = MinMaxScaler()
        self.scaler_y = MinMaxScaler()
        self.feature_cols = []
        self.last_sequence = None
        self.std_err = 0.1  # Default fallback standard error

    def _prepare_data(self, df: pd.DataFrame, target_col: str, date_col: str):
        """Extract temporal features and lag features from data."""
        df_clean = df.copy()
        
        # Ensure date_col is datetime
        if date_col and date_col in df_clean.columns:
            df_clean[date_col] = pd.to_datetime(df_clean[date_col], errors='coerce')
            df_clean = df_clean.dropna(subset=[date_col]).sort_values(by=date_col)
            
            # Temporal features
            df_clean['Hour'] = df_clean[date_col].dt.hour
            df_clean['Month'] = df_clean[date_col].dt.month
            df_clean['Day'] = df_clean[date_col].dt.day
            df_clean['DayOfWeek'] = df_clean[date_col].dt.dayofweek
        else:
            # Fallback index-based features if no date column
            df_clean['Hour'] = df_clean.index % 24
            df_clean['Month'] = (df_clean.index // 24) % 12 + 1
            df_clean['Day'] = (df_clean.index // (24 * 30)) % 30 + 1
            df_clean['DayOfWeek'] = (df_clean.index // 24) % 7

        # Detect dataset frequency (in minutes) to set lag steps
        if date_col and date_col in df_clean.columns and len(df_clean) > 2:
            time_diffs = df_clean[date_col].diff().median()
            minutes = time_diffs.total_seconds() / 60.0
            # If 10-min interval, 1 day = 144 steps. If hourly, 1 day = 24 steps.
            steps_in_day = int(1440 / minutes) if minutes > 0 else 24
        else:
            steps_in_day = 24

        # Create lags
        df_clean['lag_1'] = df_clean[target_col].shift(1)
        df_clean['lag_2'] = df_clean[target_col].shift(2)
        df_clean['lag_day'] = df_clean[target_col].shift(steps_in_day)

        df_clean = df_clean.dropna()

        features = ['Hour', 'Month', 'Day', 'DayOfWeek', 'lag_1', 'lag_2', 'lag_day']
        X = df_clean[features]
        y = df_clean[target_col]

        return X, y, steps_in_day

    def train(self, df: pd.DataFrame, target_col: str, date_col: str, console_log_fn):
        """Train models based on model_type."""
        X, y, steps_in_day = self._prepare_data(df, target_col, date_col)
        self.feature_cols = list(X.columns)
        
        # Limit training sample size to keep performance snappy in desktop environment
        max_samples = 5000
        if len(X) > max_samples:
            X = X.iloc[-max_samples:]
            y = y.iloc[-max_samples:]

        # Fit Scalers
        X_scaled = self.scaler_X.fit_transform(X)
        y_scaled = self.scaler_y.fit_transform(y.values.reshape(-1, 1)).flatten()

        # Split for validation (last 20%)
        val_size = int(len(X) * 0.2)
        if val_size < 10:
            val_size = 0
            X_train, y_train = X_scaled, y_scaled
            X_val, y_val = None, None
        else:
            X_train, X_val = X_scaled[:-val_size], X_scaled[-val_size:]
            y_train, y_val = y_scaled[:-val_size], y_scaled[-val_size:]

        # Train XGBoost
        if "XGBoost" in self.model_type or "Ensemble" in self.model_type:
            console_log_fn("  ⚡ Treinando modelo XGBoost...")
            self.xgb_model = XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.08, random_state=42)
            self.xgb_model.fit(X_train, y_train)
            
            # Compute Z-score error bounds
            preds = self.xgb_model.predict(X_train)
            residuals = y_train - preds
            self.std_err = float(np.std(residuals))
            console_log_fn("  ✅ XGBoost treinado com sucesso.")

        # Train LSTM
        if "LSTM" in self.model_type or "Ensemble" in self.model_type:
            console_log_fn("  🧠 Treinando rede neural LSTM...")
            
            # Reshape for LSTM: [samples, time steps, features]
            X_train_lstm = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
            validation_data = None
            if X_val is not None:
                X_val_lstm = np.reshape(X_val, (X_val.shape[0], 1, X_val.shape[1]))
                validation_data = (X_val_lstm, y_val)

            # Build simple LSTM
            model = Sequential([
                LSTM(32, activation='relu', input_shape=(1, X_train.shape[1])),
                Dense(16, activation='relu'),
                Dense(1)
            ])
            model.compile(optimizer=Adam(learning_rate=0.01), loss='mse')
            
            callback = GUIProgressCallback(console_log_fn, self.epochs)
            model.fit(
                X_train_lstm, y_train,
                epochs=self.epochs,
                batch_size=64,
                validation_data=validation_data,
                callbacks=[callback],
                verbose=0
            )
            self.lstm_model = model
            
            # Compute residuals
            preds = self.lstm_model.predict(X_train_lstm).flatten()
            residuals = y_train - preds
            self.std_err = float(np.std(residuals))
            console_log_fn("  ✅ LSTM treinada com sucesso.")

        # Store the very last row of X and y as base for future predictions
        self.last_row_X = X.iloc[-1].copy()
        self.last_y = y.iloc[-1]
        self.steps_in_day = steps_in_day

    def predict(self, df: pd.DataFrame, target_col: str, date_col: str, horizon_hours: int, confidence_level: float):
        """Generate prediction horizon with confidence intervals using recursive multi-step forecasting."""
        # Setup target date range
        last_date = pd.to_datetime(df[date_col].max()) if date_col and date_col in df.columns else datetime.now()
        
        # Calculate dataset interval in minutes
        if date_col and date_col in df.columns and len(df) > 2:
            time_diffs = df[date_col].diff().median()
            minutes = int(time_diffs.total_seconds() / 60.0)
            minutes = max(minutes, 10)  # Avoid zero division
        else:
            minutes = 60  # Default to hourly

        steps = int((horizon_hours * 60) / minutes)
        if steps < 1:
            steps = 1
            
        future_dates = [last_date + pd.Timedelta(minutes=minutes * i) for i in range(1, steps + 1)]
        
        # We start with the last real observations as lags
        curr_y = self.last_y
        lag_1 = df[target_col].iloc[-1]
        lag_2 = df[target_col].iloc[-2] if len(df) > 1 else lag_1
        
        # Gather recent history for day lag
        recent_history = list(df[target_col].iloc[-self.steps_in_day:].values)
        
        predictions = []
        lower_bounds = []
        upper_bounds = []
        
        # Determine critical Z value for confidence interval
        # E.g., 95% -> 1.96
        alpha = 1.0 - (confidence_level / 100.0)
        from scipy import stats
        z_critical = stats.norm.ppf(1.0 - alpha / 2.0)
        
        for i, f_date in enumerate(future_dates):
            # Extract time features
            hour = f_date.hour
            month = f_date.month
            day = f_date.day
            dayofweek = f_date.dayofweek
            
            # Lag day value from actual history or prior predictions
            lag_day_idx = len(recent_history) - self.steps_in_day
            lag_day = recent_history[lag_day_idx] if lag_day_idx >= 0 else curr_y
            
            # Assemble feature array
            feat_dict = {
                'Hour': hour,
                'Month': month,
                'Day': day,
                'DayOfWeek': dayofweek,
                'lag_1': lag_1,
                'lag_2': lag_2,
                'lag_day': lag_day
            }
            
            feat_df = pd.DataFrame([feat_dict])[self.feature_cols]
            feat_scaled = self.scaler_X.transform(feat_df)
            
            # Model predictions (scaled)
            pred_val_scaled = 0.0
            
            if self.model_type == "XGBoost" and self.xgb_model:
                pred_val_scaled = float(self.xgb_model.predict(feat_scaled)[0])
            elif self.model_type == "LSTM" and self.lstm_model:
                feat_lstm = np.reshape(feat_scaled, (1, 1, feat_scaled.shape[1]))
                pred_val_scaled = float(self.lstm_model.predict(feat_lstm, verbose=0)[0][0])
            elif self.model_type == "Ensemble" and self.xgb_model and self.lstm_model:
                p_xgb = float(self.xgb_model.predict(feat_scaled)[0])
                feat_lstm = np.reshape(feat_scaled, (1, 1, feat_scaled.shape[1]))
                p_lstm = float(self.lstm_model.predict(feat_lstm, verbose=0)[0][0])
                pred_val_scaled = 0.5 * (p_xgb + p_lstm)
            else:
                # Fallback to simple mean if model is not set
                pred_val_scaled = 0.5
                
            # Inverse scale to original units
            pred_original = float(self.scaler_y.inverse_transform([[pred_val_scaled]])[0][0])
            
            # Ensure no negative predictions for physical parameters like speed, radiation
            if pred_original < 0:
                pred_original = 0.0
                
            predictions.append(pred_original)
            
            # Uncertainty increases with steps in recursive forecasting
            step_std = self.std_err * np.sqrt(i + 1)
            # Scale uncertainty back to original scale
            original_scale_std = step_std * (self.scaler_y.data_max_[0] - self.scaler_y.data_min_[0])
            
            margin = z_critical * original_scale_std
            lower_bounds.append(max(0.0, pred_original - margin))
            upper_bounds.append(pred_original + margin)
            
            # Shift lags for next recursive step
            lag_2 = lag_1
            lag_1 = pred_original
            recent_history.append(pred_original)
            
        return pd.DataFrame({
            'Date': future_dates,
            'Prediction': predictions,
            'Lower': lower_bounds,
            'Upper': upper_bounds
        })
