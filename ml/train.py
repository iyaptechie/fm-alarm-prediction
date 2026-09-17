import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

FEATURES_PATH = "data/features/features.csv"
MODEL_PATH    = "ml/model_registry/rf_model.pkl"

FEATURE_COLS = [
    "alarm_count_10min", "critical_count_10min", "major_count_10min",
    "severity_score_sum", "unique_alarm_types", "hierarchy_level",
    "device_type_enc", "vendor_enc",
    "has_link_down", "has_ptp_sync_loss", "has_packet_loss",
    "has_high_cpu", "has_high_memory", "has_interface_flap",
    "has_cell_unavailable", "has_du_unreachable",
]

def train():
    df = pd.read_csv(FEATURES_PATH)

    X = df[FEATURE_COLS]
    y = df["target_down"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        class_weight="balanced",
        random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("=== Classification Report ===")
    print(classification_report(y_test, y_pred, target_names=["NO_FAULT", "FAULT"]))

    print("=== Confusion Matrix ===")
    print(confusion_matrix(y_test, y_pred))

    print("=== Top Feature Importances ===")
    importances = pd.Series(model.feature_importances_, index=FEATURE_COLS)
    print(importances.sort_values(ascending=False).head(10))

    os.makedirs("ml/model_registry", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved → {MODEL_PATH} ✓")

    return model

if __name__ == "__main__":
    train()