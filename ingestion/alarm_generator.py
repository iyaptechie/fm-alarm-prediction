import pandas as pd
import os

ALARMS_PATH = "data/alarms/alarms.csv"

def load_alarms():
    df = pd.read_csv(ALARMS_PATH, parse_dates=["Raised Timestamp", "Cleared Timestamp"])
    print(f"Loaded {len(df)} alarms")
    return df

def get_active_alarms():
    df = load_alarms()
    active = df[df["Status"] == "ACTIVE"]
    print(f"Active alarms : {len(active)}")
    return active

def get_alarms_for_device(device_name):
    df = load_alarms()
    return df[df["Device Name"] == device_name]

def get_critical_alarms():
    df = load_alarms()
    return df[df["Severity"] == "CRITICAL"]

if __name__ == "__main__":
    df = load_alarms()
    print("\nSeverity breakdown:")
    print(df["Severity"].value_counts())
    print("\nAlarm type breakdown:")
    print(df["Alarm Type"].value_counts())
    print("\nStatus breakdown:")
    print(df["Status"].value_counts())
    print("\nSample active critical alarms:")
    sample = df[(df["Status"] == "ACTIVE") & (df["Severity"] == "CRITICAL")].head(5)
    print(sample[["Alarm ID","Raised Timestamp","Device Name","Alarm Type","Severity"]].to_string(index=False))
