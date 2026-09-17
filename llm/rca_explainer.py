import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY not set in .env")
        _client = Groq(api_key=api_key)
    return _client

def explain_rca(prediction: dict, rca: dict, blast: dict) -> str:
    prompt = f"""You are a telecom network fault-management expert (NOC operator assistant).

ML Prediction:
- Device       : {prediction.get('device_name')}
- Fault Prob   : {prediction.get('fault_probability', 0):.1%}
- Risk Level   : {prediction.get('risk')}
- Active Alarms: {', '.join(prediction.get('top_alarms', []))}

Root Cause Analysis:
- Root Cause   : {rca.get('root_cause')}
- Root Alarm   : {rca.get('root_alarm', 'Unknown')}
- Root Type    : {rca.get('root_type', 'Unknown')}
- Reason       : {rca.get('reason')}
- Path to Core : {' → '.join(rca.get('path', {}).get('path_nodes', []))}

Blast Radius:
- Total Impacted : {blast.get('total_impacted')}
- Severity       : {blast.get('severity')}
- Impacted Nodes : {blast.get('impacted')}

In 4-5 sentences explain to a NOC operator:
1. Why this device is at risk
2. What is the most likely root cause
3. How many devices are impacted and which ones
4. What immediate action should be taken
Keep it clear, concise and actionable."""

    response = get_client().chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    prediction = {
        "device_name":       "BLR-ACC01-HW01",
        "fault_probability": 0.85,
        "risk":              "HIGH",
        "top_alarms":        ["PTP_SYNC_LOSS", "CELL_UNAVAILABLE", "PACKET_LOSS"],
    }
    rca = {
        "root_cause": "BLR-AGG01-NK01",
        "root_alarm": "LINK_DOWN",
        "root_type":  "Aggregation",
        "reason":     "LINK_DOWN on Aggregation BLR-AGG01-NK01",
        "path":       {"path_nodes": ["BLR-ACC01-HW01", "BLR-AGG01-NK01", "BLR-METRO02-NK01", "BLR-CORE01-CS01"]},
    }
    blast = {
        "total_impacted": 3,
        "severity":       "MAJOR",
        "impacted":       {"Access": ["BLR-ACC01-HW01", "BLR-ACC04-ER01", "BLR-MWRLY01-ER01"]},
    }

    print("\n=== LLM RCA Explanation ===\n")
    explanation = explain_rca(prediction, rca, blast)
    print(explanation)
