import pandas as pd
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI      = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER     = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")

def get_driver():
    return GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def clear_graph(tx):
    tx.run("MATCH (n) DETACH DELETE n")

def create_device(tx, row):
    tx.run("""
        MERGE (d:Device {name: $name})
        SET d.vendor         = $vendor,
            d.device_type    = $device_type,
            d.hierarchy_level = $level,
            d.city           = $city,
            d.region         = $region
    """,
    name=row["Device Name"],
    vendor=row["Vendor"],
    device_type=row["Device Type"],
    level=int(row["Hierarchy Level"]),
    city=row["City"],
    region=row["Region"])

def create_link(tx, row):
    tx.run("""
        MATCH (src:Device {name: $src})
        MATCH (dst:Device {name: $dst})
        MERGE (src)-[r:CONNECTED_TO {
            src_interface : $src_iface,
            dst_interface : $dst_iface,
            link_type     : $link_type,
            speed         : $speed,
            vendor        : $vendor,
            last_updated  : $last_updated
        }]->(dst)
    """,
    src=row["Source Device"],
    dst=row["Destination Device"],
    src_iface=row["Source Interface"],
    dst_iface=row["Destination Interface"],
    link_type=row["Link Type"],
    speed=row["Speed"],
    vendor=row["Vendor"],
    last_updated=row["Last Update Timestamp"])

def load_all():
    devices = pd.read_csv("data/inventory/inventory_devices.csv")
    links   = pd.read_csv("data/inventory/inventory_links.csv")

    driver = get_driver()
    with driver.session() as session:
        print("Clearing existing graph...")
        session.execute_write(clear_graph)

        print(f"Loading {len(devices)} devices...")
        for _, row in devices.iterrows():
            session.execute_write(create_device, row)

        print(f"Loading {len(links)} links...")
        for _, row in links.iterrows():
            session.execute_write(create_link, row)

        # Verify
        result = session.run("MATCH (n) RETURN count(n) as nodes")
        print(f"Graph nodes : {result.single()['nodes']}")
        result = session.run("MATCH ()-[r]->() RETURN count(r) as rels")
        print(f"Graph rels  : {result.single()['rels']}")

    driver.close()
    print("Neo4j load complete ✓")

if __name__ == "__main__":
    load_all()
