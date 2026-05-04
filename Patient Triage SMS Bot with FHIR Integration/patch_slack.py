import json

json_file_path = r"c:\Users\VICTUS\Downloads\Patient Triage SMS Bot with FHIR Integration.json"

with open(json_file_path, "r", encoding="utf-8") as f:
    flow = json.load(f)

for node in flow["nodes"]:
    if node["type"] == "n8n-nodes-base.slack":
        text = node["parameters"].get("text", "")
        if "patient_name }}" in text and "patient_id" not in text:
            text = text.replace("patient_name }}", "patient_name }} ({{ $('Webhook').item.json.body.patient_id }})")
            node["parameters"]["text"] = text

with open(json_file_path, "w", encoding="utf-8") as f:
    json.dump(flow, f, indent=2)

print("Slack node successfully updated to include patient_id.")
