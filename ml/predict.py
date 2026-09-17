import pandas as pd
import joblib

MODEL_PATH   = "ml/model_registry/rf_model.pkl"
FEATURE_COLS = [
    "alarm_count_10min", "critical_count_10min", "major_count_10min",
    "severity_score_sum", "unique_alarm_types", "hierarchy_level",
    "device_type_enc", "vendor_enc",
    "has_link_down", "has_ptp_sync_loss", "has_packet_loss",
    "has_high_cpu", "has_high_memory", "has_interface_flap",
    "has_cell_unavailable", "has_du_unreachable",
]

DEVICE_TYPE_ENC = {"Access": 0, "Aggregation": 1, "Core": 2, "DWDM": 3, "Metro": 4}
VENDOR_ENC      = {"CISCO": 0, "ERICSSON": 1, "HUAWEI": 2, "NOKIA": 3}

def predict_device(device_name, recent_alarms):
    model = joblib.load(MODEL_PATH)
    sev_score = {"WARNING": 1, "MAJOR": 2, "CRITICAL": 3}
    alarm_types_present = [a["Alarm Type"] for a in recent_alarms]
    severities          = [a["Severity"]   for a in recent_alarms]
    features = {
        "alarm_count_10min":    len(recent_alarms),
        "critical_count_10min": severities.count("CRITICAL"),
        "major_count_10min":    severities.count("MAJOR"),
        "severity_score_sum":   sum(sev_score.get(s, 0) for s in severities),
        "unique_alarm_types":   len(set(alarm_types_present)),
        "hierarchy_level":      recent_alarms[0].get("Hierarchy Level", 9) if recent_alarms else 9,
        "device_type_enc":      DEVICE_TYPE_ENC.get(recent_alarms[0].get("Device Type", "Access"), 0),
        "vendor_enc":           VENDOR_ENC.get(recent_alarms[0].get("Vendor", "HUAWEI"), 2),
        "has_link_down":        int("LINK_DOWN"        in alarm_types_present),
        "has_ptp_sync_loss":    int("PTP_SYNC_LOSS"    in alarm_types_present),
        "has_packet_loss":      int("PACKET_LOSS"      in alarm_types_present),
        "has_high_cpu":         int("HIGH_CPU"         in alarm_types_present),
        "has_high_memory":      int("HIGH_MEMORY"      in alarm_types_present),
        "has_interface_flap":   int("INTERFACE_FLAP"   in alarm_types_present),
        "has_cell_unavailable": int("CELL_UNAVAILABLE" in alarm_types_present),
        "has_du_unreachable":   int("DU_UNREACHABLE"   in alarm_types_present),
    }
    X    = pd.DataFrame([features])[FEATURE_COLS]
    prob = model.predict_proba(X)[0][1]
    risk = "HIGH" if prob >= 0.7 else "MEDIUM" if prob >= 0.4 else "LOW"
    return {
        "device_name":       device_name,
        "fault_probability": round(prob, 4),
        "risk":              risk,
        "alarm_count":       len(recent_alarms),
        "top_alarms":        list(set(alarm_types_present)),
    }

if __name__ == "__main__":
    test_alarms = [
        {"Alarm Type": "PTP_SYNC_LOSS",    "Severity": "CRITICAL", "Device Type": "Access", "Vendor": "HUAWEI", "Hierarchy Level": 9},
        {"Alarm Type": "CELL_UNAVAILABLE", "Severity": "CRITICAL", "Device Type": "Access", "Vendor": "HUAWEI", "Hierarchy Level": 9},
        {"Alarm Type": "PACKET_LOSS",      "Severity": "MAJOR",    "Device Type": "Access", "Vendor": "HUAWEI", "Hierarchy Level": 9},
    ]
    result = predict_device("BLR-ACC01-HW01", test_alarms)
    print("=" * 45)
    print(f"  Device      : {result['device_name']}")
    print(f"  Probability : {result['fault_probability']:.1%}")
    print(f"  Risk        : {result['risk']}")
    print(f"  Alarms      : {', '.join(result['top_alarms'])}")
    print("=" * 45)
