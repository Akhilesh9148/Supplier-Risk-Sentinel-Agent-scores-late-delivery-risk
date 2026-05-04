import json
import uuid

json_file_path = r"c:\Users\VICTUS\Downloads\Patient Triage SMS Bot with FHIR Integration.json"

with open(json_file_path, "r", encoding="utf-8") as f:
    flow = json.load(f)

# IDs
webhook_id = str(uuid.uuid4())
respond_id = str(uuid.uuid4())
slack_id = str(uuid.uuid4())

telegram_trigger_name = "Telegram Trigger"
telegram_send_name = "Send a text message"
triage_agent_name = "Triage Agent"

# Find nodes
for node in flow["nodes"]:
    if node["name"] == telegram_trigger_name:
        node["name"] = "Webhook"
        node["id"] = webhook_id
        node["type"] = "n8n-nodes-base.webhook"
        node["typeVersion"] = 1.1
        node["parameters"] = {
            "httpMethod": "POST",
            "path": "triage",
            "responseMode": "responseNode",
            "options": {}
        }
    elif node["name"] == triage_agent_name:
        text = node["parameters"]["text"]
        text = text.replace("{{ $json.message.text }}", "{{ $json.body.user_input }}")
        node["parameters"]["text"] = text
    elif node["name"] == telegram_send_name:
        node["name"] = "Respond to Webhook"
        node["id"] = respond_id
        node["type"] = "n8n-nodes-base.respondToWebhook"
        node["typeVersion"] = 1.1
        node["parameters"] = {
            "respondWith": "json",
            "responseBody": "={\n  \"category\": \"{{ $json.output.category }}\",\n  \"priority\": \"{{ $json.output.priority }}\",\n  \"eta\": {{ $json.estimated_wait_minutes }},\n  \"reply\": \"{{ $json.output.reply }}\"\n}",
            "options": {}
        }

# Ensure all Prepare... Nodes keep fields
for node in flow["nodes"]:
    if node["name"].startswith("Prepare") and "FHIR" in node["name"]:
        node["parameters"]["includeOtherFields"] = True

# Create Slack node
slack_node = {
    "parameters": {
        "channel": "",
        "text": "={{ $('Webhook').item.json.body.patient_name }} routed to {{ $json.output.category }} with Priority: {{ $json.output.priority }}. ETA: {{ $json.estimated_wait_minutes }} minutes",
        "otherOptions": {}
    },
    "id": slack_id,
    "name": "Send Slack Notification",
    "type": "n8n-nodes-base.slack",
    "typeVersion": 2.1,
    "position": [1632, -150]
}
flow["nodes"].append(slack_node)

# Patch Connections
new_connections = {}
for src_node, connectionsObj in flow["connections"].items():
    new_src = "Webhook" if src_node == telegram_trigger_name else src_node
    new_connections[new_src] = {}
    for output_type, connections in connectionsObj.items():
        new_connections[new_src][output_type] = []
        for targets in connections:
            new_targets = []
            for t in targets:
                target_node = t["node"]
                if target_node == telegram_trigger_name:
                    target_node = "Webhook"
                if target_node == telegram_send_name:
                    target_node = "Respond to Webhook"
                new_t = dict(t)
                new_t["node"] = target_node
                new_targets.append(new_t)
            new_connections[new_src][output_type].append(new_targets)

# Now, wherever we are connected to Respond to Webhook, we ALSO connect to Slack Notification
for src_node, connectionsObj in new_connections.items():
    if "main" in connectionsObj:
        for i, targets in enumerate(connectionsObj["main"]):
            has_respond = False
            for t in targets:
                if t["node"] == "Respond to Webhook":
                    has_respond = True
            if has_respond:
                # Add connection to Slack
                connectionsObj["main"][i].append({"node": "Send Slack Notification", "type": "main", "index": 0})

flow["connections"] = new_connections

# Save the flow
with open(json_file_path, "w", encoding="utf-8") as f:
    json.dump(flow, f, indent=2)

print("Flow updated successfully!")
