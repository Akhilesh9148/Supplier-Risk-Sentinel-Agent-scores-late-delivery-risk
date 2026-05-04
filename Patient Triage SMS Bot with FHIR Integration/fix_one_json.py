import json

file_path = r'c:\Users\VICTUS\Downloads\Patient Triage SMS Bot with FHIR Integration (1).json'

with open(file_path, 'r', encoding='utf-8') as f:
    flow = json.load(f)

for node in flow['nodes']:
    if node['name'].startswith('Prepare') and 'FHIR' in node['name']:
        for assignment in node['parameters'].get('assignments', {}).get('assignments', []):
            name = assignment.get('name')
            val = assignment.get('value', '')
            
            if name == 'fhir_patient':
                assignment['value'] = '={{ { "resourceType": "Patient", "identifier": [{ "system": "webhook", "value": $(\'Webhook\').item.json.body.patient_id }], "name": [{ "text": $(\'Webhook\').item.json.body.patient_name }] } }}'
            elif name == 'fhir_service_request':
                if isinstance(val, str):
                    val = val.replace('$json.output.urgency_level', '$json.output.priority')
                    val = val.replace('symptoms_summary', 'reply')
                    assignment['value'] = val
            elif name == 'patient_phone':
                assignment['value'] = '={{ $(\'Webhook\').item.json.body.patient_id }}'

# Also ensure Slack node is fully updated with patient_id
for node in flow['nodes']:
    if node['type'] == 'n8n-nodes-base.slack':
        text = node['parameters'].get('text', '')
        if 'patient_id' not in text:
            node['parameters']['text'] = '={{ $(\'Webhook\').item.json.body.patient_name }} ({{ $(\'Webhook\').item.json.body.patient_id }}) routed to {{ $json.output.category }} with Priority: {{ $json.output.priority }}. ETA: {{ $json.estimated_wait_minutes }} minutes'

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(flow, f, indent=2)

print('Fixed (1).json successfully!')
