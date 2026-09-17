import pandas as pd
from graph.graph_queries import get_downstream, get_neighbours

def get_blast_radius(device_name):
    """
    Find all downstream devices impacted if this device fails.
    """
    downstream = get_downstream(device_name)
    neighbours = get_neighbours(device_name)

    # Group downstream by type
    impacted = {"Access": [], "Aggregation": [], "Metro": [], "Core": [], "DWDM": []}
    for node in downstream:
        dtype = node.get("type", "Unknown")
        if dtype in impacted:
            impacted[dtype].append(node["name"])

    total = sum(len(v) for v in impacted.values())

    return {
        "device_name":    device_name,
        "total_impacted": total,
        "impacted":       impacted,
        "neighbours":     [n["name"] for n in neighbours],
        "severity":       "CRITICAL" if total > 5 else "MAJOR" if total > 2 else "MINOR",
    }

if __name__ == "__main__":
    # Test on AGG node — should show many downstream access sites
    for device in ["BLR-AGG01-NK01", "BLR-METRO01-NK01", "BLR-ACC01-HW01"]:
        print(f"\n=== Blast Radius: {device} ===")
        result = get_blast_radius(device)
        print(f"  Total impacted : {result['total_impacted']}  [{result['severity']}]")
        for dtype, nodes in result["impacted"].items():
            if nodes:
                print(f"  {dtype:12s} : {', '.join(nodes)}")
