"""
Servo-AI - ML Model Manager
Handles loading, caching, retraining, and saving the demand forecasting model.
Never crashes the API if the model file is missing.
"""
import logging
from pathlib import Path
from typing import Optional, Dict, Any

import joblib

from app.config import MODEL_FILE, BUNDLED_MODEL_FILE, MODEL_DIR

logger = logging.getLogger("servo_ai.model_manager")


class ModelManager:
    """Manages the lifecycle of the demand forecasting ML model."""

    def __init__(self):
        self._model = None
        self._metadata: Dict[str, Any] = {}
        self._is_loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded and self._model is not None

    @property
    def model(self):
        return self._model

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata

    def get_model(self):
        """Returns the cached model, loading it first if necessary.
        Returns None if no model is available (never raises)."""
        if self._is_loaded:
            return self._model
        try:
            self.load_model()
        except Exception as e:
            logger.warning(f"Could not load model: {e}")
        return self._model

    def load_model(self) -> bool:
        """Loads the active model, falling back to the bundled model.
        Returns True if a model was loaded successfully."""
        # Try active model first
        candidates = [MODEL_FILE, BUNDLED_MODEL_FILE]
        for fpath in candidates:
            if fpath and Path(fpath).exists():
                try:
                    bundle = joblib.load(fpath)
                    self._model = bundle.get("model")
                    self._metadata = {
                        "residual_std": bundle.get("residual_std", 25.0),
                        "feature_names": bundle.get("feature_names", []),
                        "label_encoders": bundle.get("label_encoders", {}),
                        "metrics": bundle.get("metrics", {}),
                        "last_trained": bundle.get("last_trained"),
                        "training_rows": bundle.get("training_rows", 0),
                    }
                    self._is_loaded = True
                    logger.info(f"Model loaded successfully from {fpath}")
                    return True
                except Exception as e:
                    logger.warning(f"Failed to load model from {fpath}: {e}")

        logger.info("No pre-trained model found. Model will be trained on first request.")
        self._is_loaded = False
        return False

    def save_model(self, model, metadata: Dict[str, Any]) -> bool:
        """Saves the trained model bundle to disk."""
        try:
            MODEL_DIR.mkdir(parents=True, exist_ok=True)
            bundle = {"model": model, **metadata}
            joblib.dump(bundle, MODEL_FILE)
            self._model = model
            self._metadata = metadata
            self._is_loaded = True
            logger.info(f"Model saved to {MODEL_FILE}")
            return True
        except (OSError, PermissionError) as e:
            logger.error(f"Could not save model file: {e}")
            # Still cache in memory even if disk save fails (serverless)
            self._model = model
            self._metadata = metadata
            self._is_loaded = True
            return False

    def retrain(self, db) -> Dict[str, Any]:
        """Triggers a full model retrain using data from the database."""
        from app.ml.train import train_demand_model
        return train_demand_model(db, self)

    def clear(self):
        """Clears the cached model."""
        self._model = None
        self._metadata = {}
        self._is_loaded = False


# Global singleton — imported by routes
model_manager = ModelManager()
