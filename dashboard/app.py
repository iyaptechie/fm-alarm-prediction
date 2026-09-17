import streamlit as st
import requests
import pandas as pd
import tempfile, os, time, json

API = "http://localhost:8000"

COLORS = {
    "Core": "#e74c3c", "Metro": "#e67e22",
    "Aggregation": "#f1c40f", "Access": "#2ecc71", "DWDM": "#9b59b6",
}

DEVICES = [
    "BLR-ACC01-HW01","BLR-ACC02-HW01","BLR-ACC03-NK01","BLR-ACC04-ER01",
    "BLR-ACC05-ER01","BLR-ACC06-ER01","BLR-AGG01-NK01","BLR-AGG02-HW01",
    "BLR-AGG03-HW01","BLR-METRO01-NK01","BLR-METRO02-NK01","BLR-CORE01-CS01",
    "MYS-ACC01-HW01","MYS-ACC02-HW01","MYS-AGG01-NK01","MYS-CORE01-CS01",
    "HBL-ACC01-ER01","HBL-AGG01-HW01","HBL-CORE01-CS01",
    "MGR-ACC01-NK01","MGR-AGG01-NK01","MGR-CORE01-CS01",
]

ALARM_TYPES = ["LINK_DOWN","PTP_SYNC_LOSS","PACKET_LOSS","HIGH_CPU",
               "HIGH_MEMORY","INTERFACE_FLAP","CELL_UNAVAILABLE",
               "DU_UNREACHABLE","BGP_SESSION_DOWN","AMPLIFIER_FAIL"]
SEVERITIES = ["CRITICAL","MAJOR","WARNING"]

# Cascade patterns: each step is (delay_sec, alarm_type, severity, description)
CASCADE_PATTERNS = {
    "LINK_DOWN": [
        (0,  "LINK_DOWN",       "CRITICAL", "🔴 Link failure detected on device"),
        (3,  "PACKET_LOSS",     "MAJOR",    "🟡 Packet loss detected on downstream nodes"),
        (6,  "PTP_SYNC_LOSS",   "CRITICAL", "🔴 PTP sync lost — timing reference gone"),
        (10, "CELL_UNAVAILABLE","CRITICAL", "🔴 Cells going unavailable — service impact!"),
        (13, "DU_UNREACHABLE",  "CRITICAL", "🔴 DU unreachable — full outage cascade"),
    ],
    "PTP_SYNC_LOSS": [
        (0,  "PTP_SYNC_LOSS",   "CRITICAL", "🔴 PTP sync loss — timing failure"),
        (4,  "CELL_UNAVAILABLE","CRITICAL", "🔴 Cells losing sync — unavailable"),
        (8,  "DU_UNREACHABLE",  "CRITICAL", "🔴 DU unreachable — cascade complete"),
    ],
    "BGP_SESSION_DOWN": [
        (0,  "BGP_SESSION_DOWN","CRITICAL", "🔴 BGP session dropped — routing failure"),
        (3,  "PACKET_LOSS",     "MAJOR",    "🟡 Traffic black-holing detected"),
        (7,  "LINK_DOWN",       "CRITICAL", "🔴 Links going down — full propagation"),
    ],
    "HIGH_CPU": [
        (0,  "HIGH_CPU",        "WARNING",  "🟡 CPU spike detected"),
        (5,  "PACKET_LOSS",     "MAJOR",    "🟡 Packet drops due to CPU overload"),
        (10, "INTERFACE_FLAP",  "MAJOR",    "🟡 Interfaces flapping under load"),
    ],
}

def get_device_type(device):
    for k,v in {"ACC":"Access","AGG":"Aggregation","METRO":"Metro","CORE":"Core","MWRLY":"Access"}.items():
        if k in device: return v
    return "Access"

def get_vendor(device):
    for k,v in {"HW":"HUAWEI","NK":"NOKIA","ER":"ERICSSON","CS":"CISCO"}.items():
        if device.endswith(k+"01"): return v
    return "HUAWEI"

def get_level(dtype):
    return {"Core":6,"Metro":7,"Aggregation":8,"Access":9}.get(dtype,9)

def inject_alarm(device, alarm_type, severity):
    dtype  = get_device_type(device)
    vendor = get_vendor(device)
    hlevel = get_level(dtype)
    payload = {"device_name":device,"alarm_type":alarm_type,
               "severity":severity,"device_type":dtype,
               "vendor":vendor,"hierarchy_level":hlevel}
    try:
        r = requests.post(f"{API}/alarms", json=payload, timeout=30)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def build_graph(device_name, root_cause=None, impacted=[], cascade_step=0):
    from pyvis.network import Network
    try:
        topo = requests.get(f"{API}/topology/{device_name}", timeout=10).json()
    except:
        return "<p>Graph unavailable</p>"

    net = Network(height="480px", width="100%", bgcolor="#0d1117",
                  font_color="white", directed=True)
    net.set_options("""{
      "physics":{"hierarchicalRepulsion":{"nodeDistance":180},"solver":"hierarchicalRepulsion"},
      "layout":{"hierarchical":{"enabled":true,"direction":"UD","sortMethod":"directed","levelSeparation":130}},
      "edges":{"arrows":{"to":{"enabled":true,"scaleFactor":0.8}},"smooth":{"type":"cubicBezier"}},
      "interaction":{"hover":true,"tooltipDelay":100}
    }""")

    added = set()

    def add_node(name, ntype, status="normal"):
        if name in added: return
        if status == "root":
            color, shape, size, prefix = "#ff0000", "star", 35, "💥"
        elif status == "source":
            color, shape, size, prefix = "#00bfff", "diamond", 30, "🔵"
        elif status == "impacted":
            color, shape, size, prefix = "#ff8c00", "triangle", 25, "⚠️"
        elif status == "path":
            color, shape, size, prefix = "#ffd700", "dot", 22, "🟡"
        else:
            color, shape, size, prefix = COLORS.get(ntype,"#95a5a6"), "dot", 18, ""
        label = f"{prefix} {name}"
        tooltip = f"Type: {ntype}\nDevice: {name}\nClick for RCA details"
        net.add_node(name, label=label, color=color, shape=shape,
                     size=size, title=tooltip)
        added.add(name)

    # Add source device
    add_node(device_name, get_device_type(device_name), "source")

    # Path nodes
    path_nodes = topo.get("path_to_core",{}).get("path_nodes",[])
    path_set   = set(path_nodes)

    for n in topo.get("upstream",[]):
        if n["name"] in path_set:
            status = "root" if n["name"]==root_cause else "path"
            add_node(n["name"], n["type"], status)

    for n in topo.get("downstream",[]):
        status = "impacted" if n["name"] in impacted else "normal"
        add_node(n["name"], n["type"], status)

    for n in topo.get("neighbours",[]):
        status = "impacted" if n["name"] in impacted else "normal"
        add_node(n["name"], n.get("type","Access"), status)

    # Edges along path
    for i in range(len(path_nodes)-1):
        s,d = path_nodes[i], path_nodes[i+1]
        if s in added and d in added:
            color = "#ff4444" if cascade_step > 0 else "#ff6b6b"
            net.add_edge(s, d, color=color, width=3, title="Fault propagation path")

    # Neighbour edges
    for n in topo.get("neighbours",[]):
        if n["name"] in added:
            lt = n.get("link_type","Fiber")
            ec = "#ff8c00" if n["name"] in impacted else "#555555"
            net.add_edge(device_name, n["name"], color=ec, width=2,
                         title=f"{lt} / {n.get('speed','')}")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    net.save_graph(tmp.name)
    html = open(tmp.name).read()
    os.unlink(tmp.name)
    return html

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="FM Alarm Prediction", page_icon="📡", layout="wide")
st.title("📡 FM Alarm Prediction — AI Autonomous NOC Engine")

# ── Session state ─────────────────────────────────────────────────────────────
if "sim_running"    not in st.session_state: st.session_state.sim_running    = False
if "sim_step"       not in st.session_state: st.session_state.sim_step       = 0
if "sim_log"        not in st.session_state: st.session_state.sim_log        = []
if "sim_result"     not in st.session_state: st.session_state.sim_result     = None
if "sim_device"     not in st.session_state: st.session_state.sim_device     = None
if "sim_alarm"      not in st.session_state: st.session_state.sim_alarm      = None
if "cascade_steps"  not in st.session_state: st.session_state.cascade_steps  = []
if "impacted_nodes" not in st.session_state: st.session_state.impacted_nodes = []

tab1, tab2, tab3 = st.tabs(["🚨 Live Alarms", "🤖 AI Simulation Engine", "🗺️ Topology Explorer"])

# ═══ TAB 1 — Live Alarms ═════════════════════════════════════════════════════
with tab1:
    st.subheader("🚨 Active Alarms — Real Time")
    c1,c2 = st.columns([1,4])
    with c1:
        sev_filter = st.selectbox("Severity", ["ALL","CRITICAL","MAJOR","WARNING"])
        limit = st.slider("Limit", 10, 100, 30)
        st.button("🔄 Refresh")
    try:
        url = f"{API}/alarms?status=ACTIVE&limit={limit}"
        if sev_filter != "ALL": url += f"&severity={sev_filter}"
        data = requests.get(url, timeout=5).json()
        if data["alarms"]:
            df = pd.DataFrame(data["alarms"])
            cols = ["Alarm ID","Raised Timestamp","Device Name","Device Type",
                    "Alarm Type","Severity","Status","Region"]
            def color_sev(val):
                if val=="CRITICAL": return "background-color:#ff4444;color:white"
                if val=="MAJOR":    return "background-color:#ff8800;color:white"
                return "background-color:#ffcc00;color:black"
            st.dataframe(df[cols].style.map(color_sev, subset=["Severity"]),
                         use_container_width=True, height=420)
            st.caption(f"Total: {data['total']} active alarms")
        else:
            st.info("No active alarms")
    except Exception as e:
        st.error(f"API error: {e}")

# ═══ TAB 2 — AI Simulation Engine ════════════════════════════════════════════
with tab2:
    st.subheader("🤖 AI Autonomous Simulation Engine")
    st.caption("Trigger an alarm → watch the AI engine observe, predict, trace root cause and explain impact in real time")

    # ── Control panel ─────────────────────────────────────────────────────────
    with st.container():
        ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([2,2,1,2])
        with ctrl1:
            sim_device = st.selectbox("🖥️ Target Device", DEVICES, key="sim_dev")
        with ctrl2:
            sim_alarm = st.selectbox("🚨 Alarm Type", ALARM_TYPES, key="sim_alm")
        with ctrl3:
            sim_sev = st.selectbox("⚡ Severity", SEVERITIES, key="sim_sev")
        with ctrl4:
            st.markdown("<br>", unsafe_allow_html=True)
            b1,b2,b3 = st.columns(3)
            start_btn  = b1.button("▶️ Start",  type="primary", use_container_width=True)
            pause_btn  = b2.button("⏸️ Pause",  use_container_width=True)
            reset_btn  = b3.button("🔄 Reset",  use_container_width=True)

    if reset_btn:
        st.session_state.sim_running    = False
        st.session_state.sim_step       = 0
        st.session_state.sim_log        = []
        st.session_state.sim_result     = None
        st.session_state.cascade_steps  = []
        st.session_state.impacted_nodes = []
        st.rerun()

    if pause_btn:
        st.session_state.sim_running = False

    if start_btn:
        st.session_state.sim_running    = True
        st.session_state.sim_step       = 0
        st.session_state.sim_log        = []
        st.session_state.sim_result     = None
        st.session_state.sim_device     = sim_device
        st.session_state.sim_alarm      = sim_alarm
        st.session_state.cascade_steps  = CASCADE_PATTERNS.get(sim_alarm, CASCADE_PATTERNS["LINK_DOWN"])
        st.session_state.impacted_nodes = []

    st.divider()

    # ── Main simulation area ──────────────────────────────────────────────────
    left, right = st.columns([3, 2])

    with left:
        graph_placeholder = st.empty()
        status_placeholder = st.empty()

    with right:
        log_placeholder    = st.empty()
        metrics_placeholder = st.empty()
        rca_placeholder    = st.empty()

    # ── Run simulation ────────────────────────────────────────────────────────
    if st.session_state.sim_running and st.session_state.sim_device:
        device  = st.session_state.sim_device
        steps   = st.session_state.cascade_steps
        step    = st.session_state.sim_step

        if step < len(steps):
            delay, alarm_t, sev, desc = steps[step]

            # Update status
            status_placeholder.info(f"⏱️ **Step {step+1}/{len(steps)}** — {desc}")

            # Inject alarm
            with st.spinner(f"🤖 AI Engine: injecting {alarm_t} on {device}..."):
                result = inject_alarm(device, alarm_t, sev)
                st.session_state.sim_result = result
                st.session_state.sim_log.append({
                    "step":  step+1,
                    "alarm": alarm_t,
                    "sev":   sev,
                    "desc":  desc,
                    "prob":  result.get("prediction",{}).get("fault_probability",0),
                    "risk":  result.get("prediction",{}).get("risk","LOW"),
                    "root":  result.get("rca",{}).get("root_cause","?"),
                })

            # Get blast radius impacted nodes
            blast = result.get("blast_radius",{})
            all_impacted = []
            for nodes in blast.get("impacted",{}).values():
                all_impacted.extend(nodes)
            st.session_state.impacted_nodes = all_impacted

            # Build graph
            root_cause = result.get("rca",{}).get("root_cause")
            graph_html = build_graph(device, root_cause=root_cause,
                                     impacted=all_impacted, cascade_step=step)
            st.components.v1.html(graph_html, height=500, scrolling=False)

            # Log panel
            log_df = pd.DataFrame(st.session_state.sim_log)
            if not log_df.empty:
                def color_risk(val):
                    if val=="HIGH":   return "color:#ff4444;font-weight:bold"
                    if val=="MEDIUM": return "color:#ff8800;font-weight:bold"
                    return "color:#2ecc71;font-weight:bold"
                log_placeholder.dataframe(
                    log_df[["step","alarm","sev","prob","risk","root"]].style.map(
                        color_risk, subset=["risk"]),
                    use_container_width=True, height=200
                )

            # Metrics
            pred = result.get("prediction",{})
            prob = pred.get("fault_probability",0)
            risk = pred.get("risk","LOW")
            rca  = result.get("rca",{})

            with metrics_placeholder.container():
                m1,m2 = st.columns(2)
                icon = "🔴" if risk=="HIGH" else "🟡" if risk=="MEDIUM" else "🟢"
                m1.metric("Fault Probability", f"{prob:.1%}")
                m2.metric("Risk", f"{icon} {risk}")
                st.markdown(f"**Root Cause:** 🔴 `{rca.get('root_cause','?')}`")
                st.markdown(f"**Reason:** {rca.get('reason','?')}")
                blast = result.get("blast_radius",{})
                sc = {"CRITICAL":"🔴","MAJOR":"🟡","MINOR":"🟢"}.get(blast.get("severity",""),"⚪")
                st.markdown(f"**Blast Radius:** {sc} {blast.get('total_impacted',0)} devices impacted")

            # RCA explanation
            with rca_placeholder.container():
                st.markdown("#### 💬 AI NOC Explanation")
                st.success(result.get("explanation","No explanation available"))

            # Advance step
            st.session_state.sim_step += 1
            if st.session_state.sim_step >= len(steps):
                st.session_state.sim_running = False
                status_placeholder.success("✅ Simulation complete — full cascade observed!")
            else:
                time.sleep(2)
                st.rerun()

        else:
            st.session_state.sim_running = False

    elif st.session_state.sim_result and not st.session_state.sim_running:
        # Show final state after pause/complete
        device     = st.session_state.sim_device
        result     = st.session_state.sim_result
        root_cause = result.get("rca",{}).get("root_cause")

        graph_html = build_graph(device, root_cause=root_cause,
                                 impacted=st.session_state.impacted_nodes,
                                 cascade_step=st.session_state.sim_step)
        st.components.v1.html(graph_html, height=500, scrolling=False)

        log_df = pd.DataFrame(st.session_state.sim_log)
        if not log_df.empty:
            log_placeholder.dataframe(log_df, use_container_width=True, height=200)

        pred = result.get("prediction",{})
        prob = pred.get("fault_probability",0)
        risk = pred.get("risk","LOW")
        rca  = result.get("rca",{})
        blast = result.get("blast_radius",{})

        with metrics_placeholder.container():
            m1,m2 = st.columns(2)
            icon = "🔴" if risk=="HIGH" else "🟡" if risk=="MEDIUM" else "🟢"
            m1.metric("Fault Probability", f"{prob:.1%}")
            m2.metric("Risk", f"{icon} {risk}")
            st.markdown(f"**Root Cause:** 🔴 `{rca.get('root_cause','?')}`")
            st.markdown(f"**Reason:** {rca.get('reason','?')}")
            sc = {"CRITICAL":"🔴","MAJOR":"🟡","MINOR":"🟢"}.get(blast.get("severity",""),"⚪")
            st.markdown(f"**Blast Radius:** {sc} {blast.get('total_impacted',0)} devices")

        with rca_placeholder.container():
            st.markdown("#### 💬 AI NOC Explanation")
            st.success(result.get("explanation",""))

    else:
        # Empty state
        graph_placeholder.info("👈 Select a device and alarm type → click ▶️ Start to run the simulation")

# ═══ TAB 3 — Topology Explorer ═══════════════════════════════════════════════
with tab3:
    st.subheader("🗺️ Network Topology Explorer")
    t_device  = st.selectbox("Select Device", DEVICES, key="topo_device")
    show_topo = st.button("🔍 Show Topology", type="primary")

    if show_topo:
        try:
            topo = requests.get(f"{API}/topology/{t_device}", timeout=10).json()

            st.markdown("#### 📡 Interactive Network Graph")
            graph_html = build_graph(t_device)
            st.components.v1.html(graph_html, height=500, scrolling=False)

            st.markdown("#### 🔎 Node Details")
            st.caption("Click any node in the graph above, then select it below for full RCA:")
            sel_node = st.selectbox("Inspect Node",
                [t_device] +
                [n["name"] for n in topo.get("upstream",[])] +
                [n["name"] for n in topo.get("neighbours",[])]
            )
            if st.button("🧠 Get RCA for this node"):
                with st.spinner("Running RCA + LLM..."):
                    try:
                        r = requests.get(f"{API}/rca/{sel_node}", timeout=30)
                        if r.status_code == 200:
                            rca_data = r.json()
                            pred  = rca_data["prediction"]
                            rca   = rca_data["rca"]
                            blast = rca_data["blast_radius"]
                            m1,m2,m3 = st.columns(3)
                            icon = "🔴" if pred["risk"]=="HIGH" else "🟡" if pred["risk"]=="MEDIUM" else "🟢"
                            m1.metric("Fault Probability", f"{pred['fault_probability']:.1%}")
                            m2.metric("Risk", f"{icon} {pred['risk']}")
                            m3.metric("Impacted", blast["total_impacted"])
                            st.error(f"🔴 Root Cause: **{rca['root_cause']}** — {rca['reason']}")
                            path = " → ".join(rca.get("path",{}).get("path_nodes",[]))
                            st.code(path)
                            st.success(rca_data["explanation"])
                        else:
                            st.warning(f"No active alarms for {sel_node}")
                    except Exception as e:
                        st.error(f"RCA error: {e}")

            st.divider()
            c1,c2,c3 = st.columns(3)
            with c1:
                st.markdown("**⬆️ Upstream**")
                if topo["upstream"]:
                    st.dataframe(pd.DataFrame(topo["upstream"]), use_container_width=True)
            with c2:
                st.markdown("**⬇️ Downstream**")
                if topo["downstream"]:
                    st.dataframe(pd.DataFrame(topo["downstream"]), use_container_width=True)
                else:
                    st.info("None")
            with c3:
                st.markdown("**🔗 Neighbours**")
                if topo["neighbours"]:
                    st.dataframe(pd.DataFrame(topo["neighbours"]), use_container_width=True)

            st.divider()
            st.markdown("#### 💥 Blast Radius")
            br = requests.get(f"{API}/impact/{t_device}").json()
            b1,b2,b3 = st.columns(3)
            b1.metric("Total Impacted", br["total_impacted"])
            b2.metric("Severity", br["severity"])
            b3.metric("Neighbours", len(br["neighbours"]))
            for dtype,nodes in br["impacted"].items():
                if nodes:
                    st.markdown(f"**{dtype}:** {', '.join(nodes)}")
        except Exception as e:
            st.error(f"Topology error: {e}")
