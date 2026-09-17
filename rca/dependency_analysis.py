import pandas as pd
from graph.graph_queries import get_upstream, get_path_to_core
from ingestion.alarm_generator import load_alarms


def find_root_cause(device_name, window_minutes=15):
    upstream = get_upstream(device_name)
    if not upstream:
        return {
            "root_cause": device_name,
            "root_alarm": "Unknown",
            "root_type": "Unknown",
            "reason": "No upstream found",
            "upstream_alarms": [],
            "path": get_path_to_core(device_name),
        }

    df = load_alarms()
    active = df[df["Status"].isin(["ACTIVE", "ACKNOWLEDGED"])]
    critical = active[active["Severity"] == "CRITICAL"]

    upstream_names = [n["name"] for n in upstream]
    upstream_alarms = critical[critical["Device Name"].isin(upstream_names)]

    if upstream_alarms.empty:
        return {
            "root_cause": device_name,
            "root_alarm": "Unknown",
            "root_type": "Unknown",
            "reason": "No upstream critical alarms found",
            "upstream_alarms": [],
            "path": get_path_to_core(device_name),
        }

    upstream_with_alarm = []
    for _, row in upstream_alarms.iterrows():
        node = next((n for n in upstream if n["name"] == row["Device Name"]), None)
        if node:
            upstream_with_alarm.append({
                "name":       row["Device Name"],
                "level":      node["level"],
                "type":       node["type"],
                "alarm_type": row["Alarm Type"],
                "severity":   row["Severity"],
            })

    upstream_with_alarm.sort(key=lambda x: x["level"])
    root = upstream_with_alarm[0]

    return {
        "root_cause":      root["name"],
        "root_alarm":      root["alarm_type"],
        "root_type":       root["type"],
        "reason":          f"{root['alarm_type']} on {root['type']} {root['name']}",
        "upstream_alarms": upstream_with_alarm,
        "path":            get_path_to_core(device_name),
    }


if __name__ == "__main__":
    device = "BLR-ACC01-HW01"
    print(f"\n=== RCA for {device} ===")
    rca = find_root_cause(device)
    print(f"  Root Cause : {rca['root_cause']}")
    print(f"  Reason     : {rca['reason']}")
    for a in rca.get("upstream_alarms", []):
        print(f"    L{a['level']} {a['type']:12s} {a['name']:25s} → {a['alarm_type']}")
