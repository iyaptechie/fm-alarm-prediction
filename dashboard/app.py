import streamlit as st
import requests
import pandas as pd
import tempfile, os, time

API = "http://localhost:8000"

# ── NOCVISION Color System ─────────────────────────────────────────────────
# Primary: #003F72 (NOCVISION deep navy)
# Secondary: #0057A8 (NOCVISION blue)
# Accent: #00A3E0 (NOCVISION cyan)
# Critical: #E3001B (NOCVISION red)
# Major: #FF6B00 (amber)
# Minor: #FFD100 (yellow)
# Clear: #00A878 (green)
# Surface: #0A1628 (near-black navy)
# Panel: #0D1F3C (dark panel)
# Border: #1B3A5C (panel border)

NOCVISION_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --nocvision-navy:    #003F72;
    --nocvision-blue:    #0057A8;
    --nocvision-cyan:    #00A3E0;
    --critical:      #E3001B;
    --major:         #FF6B00;
    --minor:         #FFD100;
    --clear:         #00A878;
    --surface:       #0A1628;
    --panel:         #0D1F3C;
    --panel2:        #112444;
    --border:        #1B3A5C;
    --text:          #FFFFFF;
    --text-dim:      #C8DCF0;
    --font:          'Inter', sans-serif;
    --mono:          'JetBrains Mono', monospace;
}

/* Global */
html, body, [class*="css"] {
    font-family: var(--font) !important;
    background-color: var(--surface) !important;
    color: var(--text) !important;
}

.stApp { background-color: var(--surface) !important; }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 1.5rem 2rem 1.5rem !important; max-width: 100% !important; }

/* NOCVISION header bar */
.nocvision-header {
    background: linear-gradient(90deg, #003F72 0%, #0057A8 60%, #00A3E0 100%);
    padding: 12px 24px;
    margin: -1rem -1.5rem 1.5rem -1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 2px solid var(--nocvision-cyan);
}
.nocvision-header-title {
    font-size: 18px;
    font-weight: 600;
    letter-spacing: 0.04em;
    color: white;
}
.nocvision-header-sub {
    font-size: 11px;
    color: rgba(255,255,255,0.7);
    font-family: var(--mono);
    margin-top: 2px;
}
.nocvision-logo {
    font-size: 22px;
    font-weight: 700;
    color: white;
    letter-spacing: 0.1em;
    border: 2px solid white;
    padding: 2px 8px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--panel) !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #FFFFFF !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.06em !important;
    padding: 10px 20px !important;
    border-right: 1px solid var(--border) !important;
    border-radius: 0 !important;
}
.stTabs [aria-selected="true"] {
    background: var(--nocvision-navy) !important;
    color: var(--nocvision-cyan) !important;
    border-bottom: 2px solid var(--nocvision-cyan) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: var(--surface) !important;
    padding: 1rem 0 !important;
}

/* Metric cards */
.noc-metric {
    background: var(--panel);
    border: 1px solid var(--border);
    border-left: 3px solid var(--nocvision-cyan);
    padding: 12px 16px;
    border-radius: 2px;
}
.noc-metric-label {
    font-size: 10px;
    color: #B8D4F0;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 4px;
    font-family: var(--mono);
}
.noc-metric-value {
    font-size: 24px;
    font-weight: 600;
    color: var(--text);
}
.noc-metric-sub {
    font-size: 11px;
    color: #B8D4F0;
    margin-top: 2px;
}

/* Alarm badges */
.badge-critical { background:#E3001B; color:white; padding:2px 8px; border-radius:2px; font-size:11px; font-weight:600; font-family:var(--mono); }
.badge-major    { background:#FF6B00; color:white; padding:2px 8px; border-radius:2px; font-size:11px; font-weight:600; font-family:var(--mono); }
.badge-minor    { background:#FFD100; color:#000;  padding:2px 8px; border-radius:2px; font-size:11px; font-weight:600; font-family:var(--mono); }
.badge-clear    { background:#00A878; color:white; padding:2px 8px; border-radius:2px; font-size:11px; font-weight:600; font-family:var(--mono); }

/* Panel boxes */
.noc-panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 16px;
    margin-bottom: 12px;
}
.noc-panel-title {
    font-size: 11px;
    font-weight: 600;
    color: var(--nocvision-cyan);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-family: var(--mono);
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin-bottom: 12px;
}

/* RCA root cause box */
.rca-root {
    background: rgba(227,0,27,0.12);
    border: 1px solid #E3001B;
    border-left: 4px solid #E3001B;
    padding: 12px 16px;
    border-radius: 2px;
    font-family: var(--mono);
    font-size: 13px;
}
.rca-path {
    background: var(--panel2);
    border: 1px solid var(--border);
    padding: 10px 16px;
    border-radius: 2px;
    font-family: var(--mono);
    font-size: 12px;
    color: var(--nocvision-cyan);
}

/* Simulation step indicator */
.sim-step {
    background: var(--panel);
    border: 1px solid var(--nocvision-blue);
    border-left: 4px solid var(--nocvision-cyan);
    padding: 10px 16px;
    border-radius: 2px;
    font-size: 13px;
    font-family: var(--mono);
    margin-bottom: 12px;
}

/* LLM explanation */
.llm-box {
    background: rgba(0,163,224,0.08);
    border: 1px solid rgba(0,163,224,0.3);
    border-left: 4px solid var(--nocvision-cyan);
    padding: 14px 18px;
    border-radius: 2px;
    font-size: 13px;
    line-height: 1.7;
    color: var(--text);
}

/* Dataframe */
.stDataFrame { border: 1px solid var(--border) !important; }
[data-testid="stDataFrame"] { background: var(--panel) !important; }

/* Selectbox / inputs */
.stSelectbox > div > div {
    background: #112444 !important;
    border: 1px solid #00A3E0 !important;
    color: #FFFFFF !important;
    border-radius: 2px !important;
}
.stSelectbox label, .stSlider label, .stSelectbox p {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}
label, p, span, div {
    color: #FFFFFF !important;
}
.stSelectbox [data-baseweb="select"] span {
    color: #FFFFFF !important;
}
[data-testid="stWidgetLabel"] {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* Buttons */
.stButton > button {
    background: var(--nocvision-blue) !important;
    color: white !important;
    border: 1px solid var(--nocvision-cyan) !important;
    border-radius: 2px !important;
    font-family: var(--mono) !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    padding: 6px 16px !important;
}
.stButton > button:hover {
    background: var(--nocvision-cyan) !important;
    color: var(--surface) !important;
}
button[kind="primary"] {
    background: var(--nocvision-cyan) !important;
    color: var(--surface) !important;
    font-weight: 600 !important;
}

/* Slider */
.stSlider [data-testid="stSlider"] { color: var(--nocvision-cyan) !important; }

/* Divider */
hr { border-color: var(--border) !important; }

/* Status bar */
.status-bar {
    background: var(--panel);
    border-top: 1px solid var(--border);
    padding: 6px 16px;
    font-size: 10px;
    font-family: var(--mono);
    color: #B8D4F0;
    display: flex;
    gap: 24px;
}
.status-dot { width:8px; height:8px; border-radius:50%; display:inline-block; margin-right:6px; }
.dot-green  { background: #00A878; box-shadow: 0 0 6px #00A878; }
.dot-red    { background: #E3001B; box-shadow: 0 0 6px #E3001B; }
.dot-amber  { background: #FF6B00; box-shadow: 0 0 6px #FF6B00; }

/* Cascade log table */
.cascade-row { 
    font-family: var(--mono); 
    font-size: 12px; 
    padding: 6px 10px;
    border-bottom: 1px solid var(--border);
}

/* Dropdown text white, background dark */
.stSelectbox div[data-baseweb="select"] div { color: #FFFFFF !important; }
.stSelectbox div[data-baseweb="select"] input { color: #FFFFFF !important; }
.stSelectbox svg { fill: #FFFFFF !important; }
[data-baseweb="popover"] { background: #0D1F3C !important; }
[data-baseweb="popover"] li { background: #0D1F3C !important; color: #FFFFFF !important; }
[data-baseweb="popover"] li:hover { background: #0057A8 !important; color: #FFFFFF !important; }
ul[data-baseweb="menu"] { background: #0D1F3C !important; }


/* Dropdown popup dark background */
[data-baseweb="popover"] * { background-color: #0D1F3C !important; color: #FFFFFF !important; }
[data-baseweb="menu"] { background-color: #0D1F3C !important; }
[data-baseweb="menu"] li { color: #FFFFFF !important; background-color: #0D1F3C !important; }
[data-baseweb="menu"] li:hover { background-color: #0057A8 !important; color: #FFFFFF !important; }
[data-baseweb="select"] * { color: #FFFFFF !important; }
[data-baseweb="select"] div { background-color: #112444 !important; }
div[role="listbox"] { background-color: #0D1F3C !important; }
div[role="option"] { background-color: #0D1F3C !important; color: #FFFFFF !important; }
div[role="option"]:hover { background-color: #0057A8 !important; }

</style>
"""

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

CASCADE_PATTERNS = {
    "LINK_DOWN":       [(0,"LINK_DOWN","CRITICAL","Link failure detected"),(3,"PACKET_LOSS","MAJOR","Packet loss on downstream"),(6,"PTP_SYNC_LOSS","CRITICAL","PTP sync lost — timing gone"),(10,"CELL_UNAVAILABLE","CRITICAL","Cells going unavailable"),(13,"DU_UNREACHABLE","CRITICAL","DU unreachable — full outage")],
    "PTP_SYNC_LOSS":   [(0,"PTP_SYNC_LOSS","CRITICAL","PTP sync loss"),(4,"CELL_UNAVAILABLE","CRITICAL","Cells losing sync"),(8,"DU_UNREACHABLE","CRITICAL","DU unreachable")],
    "BGP_SESSION_DOWN":[(0,"BGP_SESSION_DOWN","CRITICAL","BGP session dropped"),(3,"PACKET_LOSS","MAJOR","Traffic black-holing"),(7,"LINK_DOWN","CRITICAL","Links going down")],
    "HIGH_CPU":        [(0,"HIGH_CPU","WARNING","CPU spike"),(5,"PACKET_LOSS","MAJOR","Packet drops due to CPU"),(10,"INTERFACE_FLAP","MAJOR","Interfaces flapping")],
}

COLORS = {"Core":"#e74c3c","Metro":"#e67e22","Aggregation":"#f1c40f","Access":"#2ecc71","DWDM":"#9b59b6"}

def get_device_type(device):
    for k,v in {"ACC":"Access","AGG":"Aggregation","METRO":"Metro","CORE":"Core","MWRLY":"Access"}.items():
        if k in device: return v
    return "Access"

def get_vendor(device):
    for k,v in {"HW":"HUAWEI","NK":"NOCVISION","ER":"ERICSSON","CS":"CISCO"}.items():
        if device.endswith(k+"01"): return v
    return "HUAWEI"

def get_level(dtype):
    return {"Core":6,"Metro":7,"Aggregation":8,"Access":9}.get(dtype,9)

def inject_alarm(device, alarm_type, severity):
    dtype  = get_device_type(device)
    vendor = get_vendor(device)
    hlevel = get_level(dtype)
    payload = {"device_name":device,"alarm_type":alarm_type,"severity":severity,
               "device_type":dtype,"vendor":vendor,"hierarchy_level":hlevel}
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
        return "<p style='color:#FFFFFF'>Graph unavailable</p>"

    net = Network(height="420px", width="100%", bgcolor="#0A1628",
                  font_color="#E8EDF5", directed=True)
    net.set_options("""{
      "physics":{"hierarchicalRepulsion":{"nodeDistance":160},"solver":"hierarchicalRepulsion"},
      "layout":{"hierarchical":{"enabled":true,"direction":"UD","sortMethod":"directed","levelSeparation":120}},
      "edges":{"arrows":{"to":{"enabled":true,"scaleFactor":0.7}},"smooth":{"type":"cubicBezier"}},
      "interaction":{"hover":true,"tooltipDelay":80}
    }""")

    added = set()
    path_nodes = topo.get("path_to_core",{}).get("path_nodes",[])
    path_set   = set(path_nodes)

    def add_node(name, ntype, status="normal"):
        if name in added: return
        if status=="root":
            color,shape,size = "#E3001B","star",38
        elif status=="source":
            color,shape,size = "#00A3E0","diamond",32
        elif status=="impacted":
            color,shape,size = "#FF6B00","triangle",26
        elif status=="path":
            color,shape,size = "#0057A8","dot",22
        else:
            color,shape,size = COLORS.get(ntype,"#1B3A5C"),"dot",18
        border = "#00A3E0" if status=="source" else ("#E3001B" if status=="root" else "#1B3A5C")
        net.add_node(name, label=name, color={"background":color,"border":border},
                     shape=shape, size=size,
                     title=f"<b style='color:#00A3E0'>{name}</b><br>Type: {ntype}<br>Status: {status.upper()}")
        added.add(name)

    add_node(device_name, get_device_type(device_name), "source")
    for n in topo.get("upstream",[]):
        if n["name"] in path_set:
            add_node(n["name"],n["type"],"root" if n["name"]==root_cause else "path")
    for n in topo.get("downstream",[]):
        add_node(n["name"],n["type"],"impacted" if n["name"] in impacted else "normal")
    for n in topo.get("neighbours",[]):
        add_node(n["name"],n.get("type","Access"),"impacted" if n["name"] in impacted else "normal")

    for i in range(len(path_nodes)-1):
        s,d = path_nodes[i],path_nodes[i+1]
        if s in added and d in added:
            net.add_edge(s,d,color="#E3001B" if cascade_step>0 else "#0057A8",width=3,title="Fault path")

    for n in topo.get("neighbours",[]):
        if n["name"] in added:
            ec = "#FF6B00" if n["name"] in impacted else "#1B3A5C"
            net.add_edge(device_name,n["name"],color=ec,width=2,
                        title=f"{n.get('link_type','')} / {n.get('speed','')}")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    net.save_graph(tmp.name)
    html = open(tmp.name).read()
    os.unlink(tmp.name)
    return html

def severity_badge(sev):
    colors = {"CRITICAL":"#E3001B","MAJOR":"#FF6B00","WARNING":"#FFD100","CLEARED":"#00A878"}
    tc     = {"CRITICAL":"white","MAJOR":"white","WARNING":"black","CLEARED":"white"}
    c = colors.get(sev,"#1B3A5C")
    t = tc.get(sev,"white")
    return f"<span style='background:{c};color:{t};padding:2px 8px;border-radius:2px;font-size:11px;font-weight:600;font-family:monospace'>{sev}</span>"

# ── Page ─────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="NOCVISION — AI NOC Platform", page_icon="📡", layout="wide")
st.markdown(NOCVISION_CSS, unsafe_allow_html=True)

# Header
st.markdown("""
<div class="nocvision-header">
    <div>
        <div class="nocvision-header-title">📡 FAULT MANAGEMENT — AI PREDICTION ENGINE</div>
        <div class="nocvision-header-sub">Autonomous 5G Fault Intelligence Platform</div>
    </div>
    <div class="nocvision-logo">NOCVISION</div>
</div>
""", unsafe_allow_html=True)

# Status bar
try:
    r = requests.get(f"{API}/health", timeout=2)
    api_status = '<span class="status-dot dot-green"></span>API ONLINE'
except:
    api_status = '<span class="status-dot dot-red"></span>API OFFLINE'

try:
    alarms_r = requests.get(f"{API}/alarms?status=ACTIVE&limit=1", timeout=2)
    total = alarms_r.json().get("total",0)
    alarm_status = f'<span class="status-dot dot-amber"></span>{total} ACTIVE ALARMS'
except:
    alarm_status = '<span class="status-dot dot-red"></span>ALARMS UNAVAILABLE'

st.markdown(f"""
<div class="status-bar">
    <span>{api_status}</span>
    <span>{alarm_status}</span>
    <span><span class="status-dot dot-green"></span>NEO4J CONNECTED</span>
    <span style="margin-left:auto;color:#FFFFFF">GROQ LLM · RANDOM FOREST v1.0</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for k,v in [("sim_running",False),("sim_step",0),("sim_log",[]),("sim_result",None),
             ("sim_device",None),("cascade_steps",[]),("impacted_nodes",[]),
             ("rca_node",None),("rca_data",None)]:
    if k not in st.session_state: st.session_state[k] = v

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "LIVE ALARMS",
    "AI SIMULATION ENGINE",
    "TOPOLOGY EXPLORER",
    "NODE RCA DETAILS",
])

# ═══ TAB 1 — Live Alarms ═════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="noc-panel-title">ACTIVE ALARM FEED</div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,1,4])
    with c1:
        sev_filter = st.selectbox("Severity Filter", ["ALL","CRITICAL","MAJOR","WARNING"])
    with c2:
        limit = st.slider("Rows", 10, 100, 30)
    with c3:
        st.markdown("<br>",unsafe_allow_html=True)
        st.button("↻  Refresh Feed")

    try:
        url = f"{API}/alarms?status=ACTIVE&limit={limit}"
        if sev_filter != "ALL": url += f"&severity={sev_filter}"
        data = requests.get(url, timeout=5).json()
        if data["alarms"]:
            df = pd.DataFrame(data["alarms"])
            cols = ["Alarm ID","Raised Timestamp","Device Name","Device Type",
                    "Alarm Type","Severity","Region","City"]
            def color_row(row):
                c = {"CRITICAL":"rgba(227,0,27,0.15)","MAJOR":"rgba(255,107,0,0.15)",
                     "WARNING":"rgba(255,209,0,0.10)"}.get(row["Severity"],"")
                return [f"background-color:{c}" for _ in row]
            styled = df[cols].style.apply(color_row, axis=1)
            st.dataframe(styled, use_container_width=True, height=500)
            st.markdown(f'<div style="font-family:monospace;font-size:11px;color:#FFFFFF;margin-top:8px">Showing {len(df)} of {data["total"]} active alarms</div>', unsafe_allow_html=True)
        else:
            st.info("No active alarms in feed")
    except Exception as e:
        st.error(f"Feed error: {e}")

# ═══ TAB 2 — AI Simulation Engine ════════════════════════════════════════════
with tab2:
    st.markdown('<div class="noc-panel-title">AI AUTONOMOUS SIMULATION ENGINE</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:12px;color:#FFFFFF;margin-bottom:16px">Trigger a fault → observe ML prediction → trace root cause → watch cascade propagate in real time</div>', unsafe_allow_html=True)

    # Control bar
    ctrl = st.container()
    with ctrl:
        c1,c2,c3,c4 = st.columns([2,2,1,2])
        with c1:
            sim_device = st.selectbox("TARGET DEVICE", DEVICES, key="sim_dev")
        with c2:
            sim_alarm = st.selectbox("FAULT TYPE", ALARM_TYPES, key="sim_alm")
        with c3:
            sim_sev = st.selectbox("SEVERITY", SEVERITIES, key="sim_sev")
        with c4:
            st.markdown("<br>",unsafe_allow_html=True)
            b1,b2,b3 = st.columns(3)
            start_btn = b1.button("▶ START", type="primary", use_container_width=True)
            pause_btn = b2.button("⏸ PAUSE", use_container_width=True)
            reset_btn = b3.button("↺ RESET", use_container_width=True)

    if reset_btn:
        for k in ["sim_running","sim_step","sim_log","sim_result","sim_device","cascade_steps","impacted_nodes"]:
            st.session_state[k] = False if k=="sim_running" else 0 if k=="sim_step" else [] if k in ["sim_log","cascade_steps","impacted_nodes"] else None
        st.rerun()

    if pause_btn: st.session_state.sim_running = False

    if start_btn:
        st.session_state.sim_running   = True
        st.session_state.sim_step      = 0
        st.session_state.sim_log       = []
        st.session_state.sim_result    = None
        st.session_state.sim_device    = sim_device
        st.session_state.cascade_steps = CASCADE_PATTERNS.get(sim_alarm, CASCADE_PATTERNS["LINK_DOWN"])
        st.session_state.impacted_nodes= []

    st.markdown("<hr>",unsafe_allow_html=True)

    left, right = st.columns([3,2])

    with left:
        graph_ph  = st.empty()
        status_ph = st.empty()

    with right:
        metrics_ph = st.empty()
        log_ph     = st.empty()
        llm_ph     = st.empty()

    # Run simulation
    if st.session_state.sim_running and st.session_state.sim_device:
        device = st.session_state.sim_device
        steps  = st.session_state.cascade_steps
        step   = st.session_state.sim_step

        if step < len(steps):
            delay,alarm_t,sev,desc = steps[step]
            status_ph.markdown(f'<div class="sim-step">⏱ STEP {step+1}/{len(steps)} &nbsp;|&nbsp; {alarm_t} &nbsp;|&nbsp; {desc}</div>', unsafe_allow_html=True)

            with st.spinner(f"AI Engine processing {alarm_t}..."):
                result = inject_alarm(device, alarm_t, sev)
                st.session_state.sim_result = result
                pred  = result.get("prediction",{})
                rca   = result.get("rca",{})
                blast = result.get("blast_radius",{})

                st.session_state.sim_log.append({
                    "STEP":  f"{step+1}/{len(steps)}",
                    "FAULT": alarm_t,
                    "SEV":   sev,
                    "EVENT": desc,
                    "PROB":  f"{pred.get('fault_probability',0):.1%}",
                    "RISK":  pred.get("risk","LOW"),
                    "ROOT":  rca.get("root_cause","?"),
                })

            all_impacted = []
            for nodes in blast.get("impacted",{}).values():
                all_impacted.extend(nodes)
            st.session_state.impacted_nodes = all_impacted

            root_cause = rca.get("root_cause")
            graph_html = build_graph(device, root_cause=root_cause,
                                     impacted=all_impacted, cascade_step=step)
            with graph_ph:
                st.components.v1.html(graph_html, height=440, scrolling=False)

            prob = pred.get("fault_probability",0)
            risk = pred.get("risk","LOW")
            risk_color = {"HIGH":"#E3001B","MEDIUM":"#FF6B00","LOW":"#00A878"}.get(risk,"#00A878")
            blast_sev_color = {"CRITICAL":"#E3001B","MAJOR":"#FF6B00","MINOR":"#FFD100"}.get(blast.get("severity",""),"#1B3A5C")

            with metrics_ph.container():
                st.markdown(f"""
                <div class="noc-panel">
                    <div class="noc-panel-title">PREDICTION METRICS</div>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">
                        <div class="noc-metric">
                            <div class="noc-metric-label">Fault Probability</div>
                            <div class="noc-metric-value" style="color:{risk_color}">{prob:.1%}</div>
                        </div>
                        <div class="noc-metric">
                            <div class="noc-metric-label">Risk Level</div>
                            <div class="noc-metric-value" style="color:{risk_color}">{risk}</div>
                        </div>
                        <div class="noc-metric">
                            <div class="noc-metric-label">Blast Radius</div>
                            <div class="noc-metric-value" style="color:{blast_sev_color}">{blast.get('total_impacted',0)}</div>
                            <div class="noc-metric-sub">{blast.get('severity','MINOR')}</div>
                        </div>
                    </div>
                    <div style="margin-top:12px">
                        <div class="noc-panel-title" style="margin-top:8px">ROOT CAUSE</div>
                        <div class="rca-root">🔴 {rca.get('root_cause','?')}<br><span style="color:#FFFFFF;font-size:11px">{rca.get('reason','?')}</span></div>
                    </div>
                    <div style="margin-top:8px">
                        <div class="rca-path">{'  →  '.join(rca.get('path',{}).get('path_nodes',[]))}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with log_ph.container():
                if st.session_state.sim_log:
                    log_df = pd.DataFrame(st.session_state.sim_log)
                    st.markdown('<div class="noc-panel-title">CASCADE EVENT LOG</div>', unsafe_allow_html=True)
                    st.dataframe(log_df, use_container_width=True, height=180, hide_index=True)

            with llm_ph.container():
                expl = result.get("explanation","")
                if expl:
                    st.markdown(f'<div class="noc-panel-title">AI NOC ANALYSIS</div><div class="llm-box">{expl}</div>', unsafe_allow_html=True)

            # Node selector for RCA tab
            st.markdown('<div style="font-size:11px;color:#FFFFFF;margin-top:8px;font-family:monospace">→ Go to NODE RCA DETAILS tab to inspect any node</div>', unsafe_allow_html=True)

            st.session_state.sim_step += 1
            if st.session_state.sim_step >= len(steps):
                st.session_state.sim_running = False
                status_ph.markdown('<div class="sim-step" style="border-left-color:#00A878">✅ SIMULATION COMPLETE — Full cascade observed</div>', unsafe_allow_html=True)
            else:
                time.sleep(2)
                st.rerun()

    elif st.session_state.sim_result and not st.session_state.sim_running:
        device     = st.session_state.sim_device
        result     = st.session_state.sim_result
        root_cause = result.get("rca",{}).get("root_cause")
        graph_html = build_graph(device, root_cause=root_cause,
                                 impacted=st.session_state.impacted_nodes,
                                 cascade_step=st.session_state.sim_step)
        with graph_ph:
            st.components.v1.html(graph_html, height=440, scrolling=False)

        pred  = result.get("prediction",{})
        rca   = result.get("rca",{})
        blast = result.get("blast_radius",{})
        prob  = pred.get("fault_probability",0)
        risk  = pred.get("risk","LOW")
        risk_color = {"HIGH":"#E3001B","MEDIUM":"#FF6B00","LOW":"#00A878"}.get(risk,"#00A878")
        blast_sev_color = {"CRITICAL":"#E3001B","MAJOR":"#FF6B00","MINOR":"#FFD100"}.get(blast.get("severity",""),"#1B3A5C")

        with metrics_ph.container():
            st.markdown(f"""
            <div class="noc-panel">
                <div class="noc-panel-title">PREDICTION METRICS</div>
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">
                    <div class="noc-metric">
                        <div class="noc-metric-label">Fault Probability</div>
                        <div class="noc-metric-value" style="color:{risk_color}">{prob:.1%}</div>
                    </div>
                    <div class="noc-metric">
                        <div class="noc-metric-label">Risk Level</div>
                        <div class="noc-metric-value" style="color:{risk_color}">{risk}</div>
                    </div>
                    <div class="noc-metric">
                        <div class="noc-metric-label">Blast Radius</div>
                        <div class="noc-metric-value" style="color:{blast_sev_color}">{blast.get('total_impacted',0)}</div>
                        <div class="noc-metric-sub">{blast.get('severity','MINOR')}</div>
                    </div>
                </div>
                <div style="margin-top:12px">
                    <div class="noc-panel-title" style="margin-top:8px">ROOT CAUSE</div>
                    <div class="rca-root">🔴 {rca.get('root_cause','?')}<br><span style="color:#FFFFFF;font-size:11px">{rca.get('reason','?')}</span></div>
                </div>
                <div style="margin-top:8px">
                    <div class="rca-path">{'  →  '.join(rca.get('path',{}).get('path_nodes',[]))}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with log_ph.container():
            if st.session_state.sim_log:
                log_df = pd.DataFrame(st.session_state.sim_log)
                st.markdown('<div class="noc-panel-title">CASCADE EVENT LOG</div>', unsafe_allow_html=True)
                st.dataframe(log_df, use_container_width=True, height=180, hide_index=True)

        with llm_ph.container():
            expl = result.get("explanation","")
            if expl:
                st.markdown(f'<div class="noc-panel-title">AI NOC ANALYSIS</div><div class="llm-box">{expl}</div>', unsafe_allow_html=True)

    else:
        graph_ph.markdown("""
        <div style="background:#0D1F3C;border:1px solid #1B3A5C;border-radius:2px;
                    height:420px;display:flex;align-items:center;justify-content:center;
                    flex-direction:column;gap:12px">
            <div style="font-size:48px">📡</div>
            <div style="font-family:monospace;color:#FFFFFF;font-size:13px">SELECT DEVICE AND FAULT TYPE</div>
            <div style="font-family:monospace;color:#0057A8;font-size:11px">THEN CLICK ▶ START TO RUN SIMULATION</div>
        </div>
        """, unsafe_allow_html=True)

# ═══ TAB 3 — Topology Explorer ═══════════════════════════════════════════════
with tab3:
    st.markdown('<div class="noc-panel-title">NETWORK TOPOLOGY EXPLORER</div>', unsafe_allow_html=True)
    c1,c2 = st.columns([2,1])
    with c1:
        t_device = st.selectbox("SELECT DEVICE", DEVICES, key="topo_device")
    with c2:
        st.markdown("<br>",unsafe_allow_html=True)
        show_topo = st.button("🔍 LOAD TOPOLOGY", type="primary", use_container_width=True)

    if show_topo:
        try:
            topo = requests.get(f"{API}/topology/{t_device}", timeout=10).json()
            graph_html = build_graph(t_device)
            st.components.v1.html(graph_html, height=460, scrolling=False)

            st.markdown("<br>",unsafe_allow_html=True)
            c1,c2,c3 = st.columns(3)
            with c1:
                st.markdown('<div class="noc-panel-title">UPSTREAM NODES</div>', unsafe_allow_html=True)
                if topo["upstream"]:
                    st.dataframe(pd.DataFrame(topo["upstream"]), use_container_width=True, hide_index=True)
                else:
                    st.markdown('<div style="color:#FFFFFF;font-size:12px;font-family:monospace">No upstream nodes</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="noc-panel-title">DOWNSTREAM NODES</div>', unsafe_allow_html=True)
                if topo["downstream"]:
                    st.dataframe(pd.DataFrame(topo["downstream"]), use_container_width=True, hide_index=True)
                else:
                    st.markdown('<div style="color:#FFFFFF;font-size:12px;font-family:monospace">No downstream nodes</div>', unsafe_allow_html=True)
            with c3:
                st.markdown('<div class="noc-panel-title">DIRECT NEIGHBOURS</div>', unsafe_allow_html=True)
                if topo["neighbours"]:
                    st.dataframe(pd.DataFrame(topo["neighbours"]), use_container_width=True, hide_index=True)
                else:
                    st.markdown('<div style="color:#FFFFFF;font-size:12px;font-family:monospace">None</div>', unsafe_allow_html=True)

            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="noc-panel-title">BLAST RADIUS ANALYSIS</div>', unsafe_allow_html=True)
            br = requests.get(f"{API}/impact/{t_device}").json()
            b1,b2,b3 = st.columns(3)
            b1.metric("Total Impacted", br["total_impacted"])
            b2.metric("Impact Severity", br["severity"])
            b3.metric("Direct Neighbours", len(br["neighbours"]))
            for dtype,nodes in br["impacted"].items():
                if nodes:
                    st.markdown(f'<div style="font-family:monospace;font-size:12px;color:#00A3E0;margin-top:4px"><b>{dtype}</b>: <span style="color:#E8EDF5">{", ".join(nodes)}</span></div>', unsafe_allow_html=True)

            # Save device for RCA tab
            st.session_state.rca_node = t_device
            st.markdown('<br><div style="font-family:monospace;font-size:11px;color:#FFFFFF">→ Go to NODE RCA DETAILS tab for full AI analysis of any node</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Topology error: {e}")

# ═══ TAB 4 — Node RCA Details ════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="noc-panel-title">NODE RCA DETAILS — FULL AI ANALYSIS</div>', unsafe_allow_html=True)

    c1,c2 = st.columns([2,1])
    with c1:
        rca_device = st.selectbox("SELECT NODE TO ANALYSE", DEVICES, key="rca_sel",
                                   index=DEVICES.index(st.session_state.rca_node) if st.session_state.rca_node in DEVICES else 0)
    with c2:
        st.markdown("<br>",unsafe_allow_html=True)
        run_rca = st.button("🧠 RUN FULL RCA", type="primary", use_container_width=True)

    if run_rca:
        with st.spinner("Running ML prediction → Neo4j RCA → Groq LLM analysis..."):
            try:
                r = requests.get(f"{API}/rca/{rca_device}", timeout=35)
                if r.status_code == 200:
                    rd = r.json()
                    st.session_state.rca_data = rd
                elif r.status_code == 404:
                    st.warning(f"No active alarms found for {rca_device}. Trigger an alarm first in the Simulation tab.")
                    st.session_state.rca_data = None
            except Exception as e:
                st.error(f"RCA error: {e}")
                st.session_state.rca_data = None

    if st.session_state.rca_data:
        rd    = st.session_state.rca_data
        pred  = rd.get("prediction",{})
        rca   = rd.get("rca",{})
        blast = rd.get("blast_radius",{})
        expl  = rd.get("explanation","")

        prob  = pred.get("fault_probability",0)
        risk  = pred.get("risk","LOW")
        risk_color = {"HIGH":"#E3001B","MEDIUM":"#FF6B00","LOW":"#00A878"}.get(risk,"#00A878")
        blast_sc   = {"CRITICAL":"#E3001B","MAJOR":"#FF6B00","MINOR":"#FFD100"}.get(blast.get("severity",""),"#1B3A5C")

        # Top metrics
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px">
            <div class="noc-metric" style="border-left-color:{risk_color}">
                <div class="noc-metric-label">Fault Probability</div>
                <div class="noc-metric-value" style="color:{risk_color}">{prob:.1%}</div>
            </div>
            <div class="noc-metric" style="border-left-color:{risk_color}">
                <div class="noc-metric-label">Risk Level</div>
                <div class="noc-metric-value" style="color:{risk_color}">{risk}</div>
            </div>
            <div class="noc-metric" style="border-left-color:{blast_sc}">
                <div class="noc-metric-label">Devices Impacted</div>
                <div class="noc-metric-value" style="color:{blast_sc}">{blast.get('total_impacted',0)}</div>
                <div class="noc-metric-sub">{blast.get('severity','MINOR')}</div>
            </div>
            <div class="noc-metric">
                <div class="noc-metric-label">Active Alarms</div>
                <div class="noc-metric-value">{pred.get('alarm_count',0)}</div>
                <div class="noc-metric-sub">{', '.join(pred.get('top_alarms',[]))[:30]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # RCA + Path
        col1,col2 = st.columns(2)
        with col1:
            st.markdown('<div class="noc-panel-title">ROOT CAUSE IDENTIFICATION</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="rca-root">
                <div style="font-size:14px;color:#E3001B;font-weight:600">🔴 {rca.get('root_cause','?')}</div>
                <div style="margin-top:6px;color:#E8EDF5">{rca.get('root_alarm','?')} on {rca.get('root_type','?')}</div>
                <div style="margin-top:4px;color:#FFFFFF;font-size:11px">{rca.get('reason','?')}</div>
            </div>
            """, unsafe_allow_html=True)

            # Upstream alarms
            upstream_alarms = rca.get("upstream_alarms",[])
            if upstream_alarms:
                st.markdown('<div class="noc-panel-title" style="margin-top:12px">UPSTREAM ALARM CHAIN</div>', unsafe_allow_html=True)
                for a in upstream_alarms[:5]:
                    sc = {"CRITICAL":"#E3001B","MAJOR":"#FF6B00","WARNING":"#FFD100"}.get(a.get("severity",""),"#1B3A5C")
                    st.markdown(f"""
                    <div style="background:#0D1F3C;border:1px solid #1B3A5C;border-left:3px solid {sc};
                                padding:6px 12px;margin-bottom:4px;font-family:monospace;font-size:11px">
                        L{a.get('level','?')} · {a.get('type','?')} · <b style="color:#00A3E0">{a.get('name','?')}</b>
                        <span style="float:right;color:{sc}">{a.get('alarm_type','?')}</span>
                    </div>
                    """, unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="noc-panel-title">FAULT PROPAGATION PATH</div>', unsafe_allow_html=True)
            path_nodes = rca.get("path",{}).get("path_nodes",[])
            for i,node in enumerate(path_nodes):
                is_root = node == rca.get("root_cause")
                is_src  = i == 0
                color   = "#E3001B" if is_root else "#00A3E0" if is_src else "#0057A8"
                icon    = "💥" if is_root else "🔵" if is_src else "🟡"
                st.markdown(f"""
                <div style="background:#0D1F3C;border:1px solid #1B3A5C;border-left:3px solid {color};
                            padding:8px 14px;margin-bottom:4px;font-family:monospace;font-size:12px;
                            color:#E8EDF5">
                    {icon} {node}
                    {"<span style='float:right;color:#E3001B;font-size:10px'>ROOT CAUSE</span>" if is_root else ""}
                </div>
                {"" if i==len(path_nodes)-1 else '<div style="text-align:center;color:#1B3A5C;font-size:16px;margin:-2px 0">↓</div>'}
                """, unsafe_allow_html=True)

            # Blast radius
            st.markdown('<div class="noc-panel-title" style="margin-top:12px">BLAST RADIUS</div>', unsafe_allow_html=True)
            for dtype,nodes in blast.get("impacted",{}).items():
                if nodes:
                    st.markdown(f'<div style="font-family:monospace;font-size:11px;color:#FF6B00;margin-bottom:4px"><b>{dtype}:</b> <span style="color:#E8EDF5">{", ".join(nodes)}</span></div>', unsafe_allow_html=True)

        # LLM Explanation
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div class="noc-panel-title">AI NOC ANALYSIS — GROQ LLM</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="llm-box">{expl}</div>', unsafe_allow_html=True)

        # Topology graph for this node
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div class="noc-panel-title">TOPOLOGY GRAPH</div>', unsafe_allow_html=True)
        graph_html = build_graph(rca_device, root_cause=rca.get("root_cause"),
                                  impacted=[n for nodes in blast.get("impacted",{}).values() for n in nodes])
        st.components.v1.html(graph_html, height=440, scrolling=False)

    else:
        st.markdown("""
        <div style="background:#0D1F3C;border:1px solid #1B3A5C;border-radius:2px;
                    padding:40px;text-align:center;margin-top:20px">
            <div style="font-size:36px">🧠</div>
            <div style="font-family:monospace;color:#FFFFFF;font-size:13px;margin-top:12px">
                SELECT A NODE AND CLICK RUN FULL RCA
            </div>
            <div style="font-family:monospace;color:#0057A8;font-size:11px;margin-top:8px">
                OR TRIGGER A SIMULATION IN TAB 2 FIRST TO GENERATE ACTIVE ALARMS
            </div>
        </div>
        """, unsafe_allow_html=True)