import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI      = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER     = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")

def get_driver():
    return GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def get_upstream(device_name):
    """Find all upstream nodes (higher hierarchy level)"""
    driver = get_driver()
    with driver.session() as session:
        result = session.run("""
            MATCH (src:Device {name: $name})-[:CONNECTED_TO*1..5]->(upstream:Device)
            WHERE upstream.hierarchy_level < src.hierarchy_level
            RETURN DISTINCT upstream.name AS name,
                   upstream.device_type  AS type,
                   upstream.hierarchy_level AS level,
                   upstream.vendor       AS vendor
            ORDER BY upstream.hierarchy_level DESC
        """, name=device_name)
        return [dict(r) for r in result]

def get_downstream(device_name):
    """Find all downstream nodes (lower hierarchy level)"""
    driver = get_driver()
    with driver.session() as session:
        result = session.run("""
            MATCH (src:Device {name: $name})<-[:CONNECTED_TO*1..5]-(downstream:Device)
            WHERE downstream.hierarchy_level > src.hierarchy_level
            RETURN DISTINCT downstream.name AS name,
                   downstream.device_type   AS type,
                   downstream.hierarchy_level AS level,
                   downstream.vendor        AS vendor
            ORDER BY downstream.hierarchy_level ASC
        """, name=device_name)
        return [dict(r) for r in result]

def get_neighbours(device_name):
    """Find direct neighbours"""
    driver = get_driver()
    with driver.session() as session:
        result = session.run("""
            MATCH (src:Device {name: $name})-[r:CONNECTED_TO]-(nb:Device)
            RETURN DISTINCT nb.name      AS name,
                   nb.device_type        AS type,
                   nb.hierarchy_level    AS level,
                   r.link_type          AS link_type,
                   r.speed              AS speed
        """, name=device_name)
        return [dict(r) for r in result]

def get_path_to_core(device_name):
    """Find shortest path from device to core"""
    driver = get_driver()
    with driver.session() as session:
        result = session.run("""
            MATCH (src:Device {name: $name}),
                  (core:Device {device_type: 'Core'})
            MATCH path = shortestPath((src)-[:CONNECTED_TO*]->(core))
            RETURN [n IN nodes(path) | n.name] AS path_nodes,
                   length(path) AS hops
            LIMIT 1
        """, name=device_name)
        record = result.single()
        return dict(record) if record else {}

if __name__ == "__main__":
    device = "BLR-ACC01-HW01"
    print(f"\n=== Topology for {device} ===")

    print("\nUpstream nodes:")
    for n in get_upstream(device):
        print(f"  L{n['level']} {n['type']:12s} → {n['name']}")

    print("\nDownstream nodes:")
    for n in get_downstream(device):
        print(f"  L{n['level']} {n['type']:12s} → {n['name']}")

    print("\nDirect neighbours:")
    for n in get_neighbours(device):
        print(f"  {n['name']:30s} [{n['link_type']} / {n['speed']}]")

    print("\nPath to Core:")
    path = get_path_to_core(device)
    if path:
        print(f"  {' → '.join(path['path_nodes'])}  ({path['hops']} hops)")
