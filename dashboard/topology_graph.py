from pyvis.network import Network
import requests
import tempfile, os

API = "http://localhost:8000"

COLORS = {
    "Core":        "#e74c3c",
    "Metro":       "#e67e22",
    "Aggregation": "#f1c40f",
    "Access":      "#2ecc71",
    "DWDM":        "#9b59b6",
}

def build_graph(device_name, root_cause=None):
    r = requests.get(f"{API}/topology/{device_name}")
    topo = r.json()

    net = Network(height="500px", width="100%", bgcolor="#1a1a2e",
                  font_color="white", directed=True)
    net.set_options("""
    {
      "physics": {
        "hierarchicalRepulsion": {"nodeDistance": 150},
        "solver": "hierarchicalRepulsion"
      },
      "layout": {
        "hierarchical": {
          "enabled": true,
          "direction": "UD",
          "sortMethod": "directed",
          "levelSeparation": 120
        }
      },
      "edges": {
        "arrows": {"to": {"enabled": true}},
        "color": {"color": "#aaaaaa"},
        "smooth": {"type": "cubicBezier"}
      }
    }
    """)

    added = set()

    def add_node(name, ntype, is_source=False, is_root=False):
        if name in added:
            return
        color = "#ff0000" if is_root else ("#00bfff" if is_source else COLORS.get(ntype, "#95a5a6"))
        shape = "star" if is_root else ("diamond" if is_source else "dot")
        size  = 30 if is_source or is_root else 20
        label = f"🔴 {name}" if is_root else (f"🔵 {name}" if is_source else name)
        net.add_node(name, label=label, color=color,
                     shape=shape, size=size, title=f"{ntype}\n{name}")
        added.add(name)

    # Add source device
    add_node(device_name, "Access", is_source=True)

    # Add upstream nodes
    for n in topo.get("upstream", []):
        is_root = (n["name"] == root_cause)
        add_node(n["name"], n["type"], is_root=is_root)

    # Add downstream nodes
    for n in topo.get("downstream", []):
        add_node(n["name"], n["type"])

    # Add neighbours
    for n in topo.get("neighbours", []):
        add_node(n["name"], n.get("type","Access"))

    # Add edges from path
    path_nodes = topo.get("path_to_core", {}).get("path_nodes", [])
    for i in range(len(path_nodes) - 1):
        src, dst = path_nodes[i], path_nodes[i+1]
        if src in added and dst in added:
            net.add_edge(src, dst, color="#ff6b6b", width=3, title="Path to Core")

    # Add neighbour edges
    for n in topo.get("neighbours", []):
        if n["name"] in added:
            net.add_edge(device_name, n["name"],
                        color="#aaaaaa", title=f"{n.get('link_type','')} {n.get('speed','')}")

    # Save to temp file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    net.save_graph(tmp.name)
    with open(tmp.name, "r") as f:
        html = f.read()
    os.unlink(tmp.name)
    return html
