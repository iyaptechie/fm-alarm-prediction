import pandas as pd
import os

INVENTORY_DIR = "data/inventory"

def load_devices():
    path = os.path.join(INVENTORY_DIR, "inventory_devices.csv")
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} devices")
    return df

def load_links():
    path = os.path.join(INVENTORY_DIR, "inventory_links.csv")
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} links")
    return df

if __name__ == "__main__":
    devices = load_devices()
    links = load_links()
    print("\nDevice types:")
    print(devices["Device Type"].value_counts())
    print("\nVendors:")
    print(devices["Vendor"].value_counts())
    print("\nLink types:")
    print(links["Link Type"].value_counts())
