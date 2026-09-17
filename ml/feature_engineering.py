import pandas as pd
import numpy as np
import os

ALARMS_PATH = "data/alarms/alarms.csv"

def load_alarms():
    df = pd.read_csv(ALARMS_PATH, parse_dates=["Raised Timestamp"])
    return df

def build_features(window_minutes=10):
    df = load_alarms()
    df = df.sort_values("Raised Timestamp")

    # Severity score mapping
    sev_score = {"WARNING": 1, "MAJOR": 2, "CRITICAL": 3}
    df["sev_score"] = df["Severity"].map(sev_score).fillna(0)

    # Alarm type binary flags
    alarm_types = [
        "LINK_DOWN", "PTP_SYNC_LOSS", "PACKET_LOSS",
        "HIGH_CPU", "HIGH_MEMORY", "INTERFACE_FLAP",
        "CELL_UNAVAILABLE", "DU_UNREACHABLE"
    ]

    records = []
    devices = df["Device Name"].unique()

    for device in devices:
        dev_df = df[df["Device Name"] == device].copy()

        for i, row in dev_df.iterrows():
            ts = row["Raised Timestamp"]
            window_start = ts - pd.Timedelta(minutes=window_minutes)

            # Alarms in window for this device
            window = dev_df[
                (dev_df["Raised Timestamp"] >= window_start) &
                (dev_df["Raised Timestamp"] <= ts)
            ]

            # Features
            feat = {
                "device_name":          device,
                "timestamp":            ts,
                "device_type":          row["Device Type"],
                "hierarchy_level":      row["Hierarchy Level"],
                "vendor":               row["Vendor"],
                "alarm_count_10min":    len(window),
                "critical_count_10min": len(window[window["Severity"] == "CRITICAL"]),
                "major_count_10min":    len(window[window["Severity"] == "MAJOR"]),
                "severity_score_sum":   window["sev_score"].sum(),
                "unique_alarm_types":   window["Alarm Type"].nunique(),
            }

            # Binary flag per alarm type
            for at in alarm_types:
                feat[f"has_{at.lower()}"] = int(at in window["Alarm Type"].values)

            # Target: CELL_UNAVAILABLE or LINK_DOWN in next 10 min
            future_end = ts + pd.Timedelta(minutes=window_minutes)
            future = dev_df[
                (dev_df["Raised Timestamp"] > ts) &
                (dev_df["Raised Timestamp"] <= future_end)
            ]
            feat["target_down"] = int(
                future["Alarm Type"].isin(["CELL_UNAVAILABLE", "LINK_DOWN", "DU_UNREACHABLE"]).any()
            )

            records.append(feat)

    features_df = pd.DataFrame(records)

    # Encode categoricals
    features_df["device_type_enc"] = pd.Categorical(features_df["device_type"]).codes
    features_df["vendor_enc"]      = pd.Categorical(features_df["vendor"]).codes

    os.makedirs("data/features", exist_ok=True)
    features_df.to_csv("data/features/features.csv", index=False)
    print(f"Features built : {len(features_df)} rows")
    print(f"Target balance :\n{features_df['target_down'].value_counts()}")
    return features_df

if __name__ == "__main__":
    build_features()