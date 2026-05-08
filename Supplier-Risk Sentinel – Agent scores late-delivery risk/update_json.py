import json

filepath = r'c:/Users/VICTUS/Downloads/Supplier Risk Sentinel.json'
with open(filepath, 'r') as f:
    data = json.load(f)

slack_node = {
    'parameters': {
        'resource': 'message',
        'operation': 'post',
        'channel': 'general',
        'text': '=\ud83d\udea8 *High Risk Supplier Alert* \ud83d\udea8\n\n*Vendor ID:* {{$json["Vendor ID"]}}\n*Risk Score:* {{$json["Risk Score"]}}\n*Late Deliveries:* {{$json["Late Deliveries"]}} out of {{$json["Total Orders"]}}\n\nPlease review and take action.',
        'otherOptions': {}
    },
    'id': 'slack-1234',
    'name': 'Slack',
    'type': 'n8n-nodes-base.slack',
    'typeVersion': 2.2,
    'position': [2160, 1160]
}

data['nodes'].append(slack_node)
data['connections']['If']['main'][0].append({
    'node': 'Slack',
    'type': 'main',
    'index': 0
})

with open(filepath, 'w') as f:
    json.dump(data, f, indent=2)
print("Updated successfully")
