import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

try:
    from tensorflow import keras
    from tensorflow.keras import layers
    TF_AVAILABLE = True
except Exception:
    TF_AVAILABLE = False


class MLAnomaly:
    """Simple wrapper exposing `fit` and `predict` for ML anomaly detectors.

    Implements Isolation Forest (sklearn), Clustering, and Autoencoder (Keras).
    """

    def __init__(self, method='isolation_forest', random_state=42, contamination=0.05):
        self.method = method
        self.random_state = random_state
        self.contamination = contamination  # Expected fraction of anomalies
        self.scaler = StandardScaler()
        self.model = None
        self.ae_threshold = None
        self.kmeans = None
        self.distance_threshold = None

    def fit(self, X):
        X = self._prepare_X(X)
        if self.method == 'isolation_forest':
            self.model = IsolationForest(contamination=self.contamination, random_state=self.random_state)
            self.model.fit(X)
        elif self.method == 'clustering':
            # Use K-means with k=5 clusters; anomalies are far from cluster centers
            n_clusters = max(3, min(10, X.shape[0] // 1000))
            self.kmeans = KMeans(n_clusters=n_clusters, random_state=self.random_state, n_init=10)
            self.kmeans.fit(X)
            # Distance from cluster center
            distances = np.min(self.kmeans.transform(X), axis=1)
            # Threshold: mean + 3*std of distances
            self.distance_threshold = np.mean(distances) + 3 * np.std(distances)
        elif self.method == 'autoencoder':
            if not TF_AVAILABLE:
                raise RuntimeError('TensorFlow is required for autoencoder method')
            n_features = X.shape[1]
            # Shallow autoencoder to avoid overfitting
            input_layer = keras.Input(shape=(n_features,))
            encoded = layers.Dense(max(3, n_features // 2), activation='relu')(input_layer)
            decoded = layers.Dense(n_features, activation='linear')(encoded)
            ae = keras.Model(inputs=input_layer, outputs=decoded)
            ae.compile(optimizer='adam', loss='mse')
            ae.fit(X, X, epochs=10, batch_size=32, verbose=0)
            self.model = ae
            # Calculate reconstruction errors
            train_recon = ae.predict(X, verbose=0)
            train_mse = np.mean(np.square(X - train_recon), axis=1)
            # Handle case where MSE is very small; use percentile threshold
            mse_nonzero = train_mse[train_mse > 0]
            if len(mse_nonzero) > 0:
                # Use 95th percentile if there's variation, else use max value
                self.ae_threshold = np.percentile(mse_nonzero, 95) if len(mse_nonzero) > 20 else np.max(train_mse) * 0.5
            else:
                # No variation; set high threshold to detect nothing (safe default)
                self.ae_threshold = np.max(train_mse) + 1
        else:
            raise ValueError('Unknown method: %s' % self.method)

    def predict(self, X):
        """Return boolean mask: True = anomaly"""
        X = self._prepare_X(X)
        if self.method == 'isolation_forest':
            # sklearn returns -1 for outliers
            preds = self.model.predict(X)
            return preds == -1
        elif self.method == 'clustering':
            # Distance from nearest cluster center
            distances = np.min(self.kmeans.transform(X), axis=1)
            return distances > self.distance_threshold
        elif self.method == 'autoencoder':
            recon = self.model.predict(X, verbose=0)
            mse = np.mean(np.square(X - recon), axis=1)
            # Use percentile threshold
            return mse > self.ae_threshold

    def _prepare_X(self, X):
        # X can be DataFrame or ndarray
        if hasattr(X, 'values'):
            arr = X.values.astype(float)
        else:
            arr = np.asarray(X, dtype=float)
        # handle single-column case
        if arr.ndim == 1:
            arr = arr.reshape(-1, 1)
        # Fill NaN values with column mean
        for col in range(arr.shape[1]):
            col_data = arr[:, col]
            mask = np.isnan(col_data)
            if mask.any():
                col_mean = np.nanmean(col_data)
                arr[mask, col] = col_mean
        # fit scaler only if model not trained yet
        if self.model is None:
            arr = self.scaler.fit_transform(arr)
        else:
            arr = self.scaler.transform(arr)
        return arr
