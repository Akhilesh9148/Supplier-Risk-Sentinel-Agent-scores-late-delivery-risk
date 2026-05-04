import json

json_file_path = r"c:\Users\VICTUS\Downloads\Patient Triage SMS Bot with FHIR Integration.json"

with open(json_file_path, "r", encoding="utf-8") as f:
    flow = json.load(f)

for node in flow["nodes"]:
    if node["type"] == "n8n-nodes-base.set":
        # Look in assignments
        if "assignments" in node["parameters"] and "assignments" in node["parameters"]["assignments"]:
            for assignment in node["parameters"]["assignments"]["assignments"]:
                val = assignment.get("value")
                if isinstance(val, str):
                    if "Telegram Trigger" in val:
                        val = val.replace('$node["Telegram Trigger"].json.message.chat.id', "$('Webhook').item.json.body.patient_name")
                        assignment["value"] = val
                    if "Telegram Patient" in val:
                        assignment["value"] = val.replace("Telegram Patient", "Webhook Patient")
                    if "\"system\": \"telegram\"" in val:
                        assignment["value"] = val.replace('"system": "telegram"', '"system": "webhook"')

with open(json_file_path, "w", encoding="utf-8") as f:
    json.dump(flow, f, indent=2)

print("Expressions successfully fixed.")
