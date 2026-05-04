import streamlit as st
import pandas as pd
import requests
import json

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="AI Triage System", layout="centered")

# -----------------------------
# SESSION STATE (DATABASE)
# -----------------------------
if "patients" not in st.session_state:
    st.session_state.patients = []

if "service_requests" not in st.session_state:
    st.session_state.service_requests = []

if "patient_counter" not in st.session_state:
    st.session_state.patient_counter = 1

if "request_counter" not in st.session_state:
    st.session_state.request_counter = 1

# -----------------------------
# ID GENERATORS (SHORT & SIMPLE) ✅
# -----------------------------
def generate_patient_id():
    pid = f"P{st.session_state.patient_counter:03d}"
    st.session_state.patient_counter += 1
    return pid

def generate_request_id():
    rid = f"SR{st.session_state.request_counter:03d}"
    st.session_state.request_counter += 1
    return rid

# -----------------------------
# TITLE
# -----------------------------
st.title("🏥 Intake-Bot Triage System")

# -----------------------------
# PATIENT INPUT
# -----------------------------
st.subheader("👤 Patient Details")

patient_name = st.text_input("Enter Patient Name")
patient_phone = st.text_input("Enter Patient Phone Number (Optional)")
user_input = st.text_area("📝 Describe your symptoms:")

# -----------------------------
# N8N WEBHOOK URL
# -----------------------------
N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/triage"

# -----------------------------
# BUTTON ACTION
# -----------------------------
if st.button("🚀 Analyze"):

    if not patient_name or not user_input:
        st.warning("Please enter patient name and symptoms")
    else:
        # -----------------------------
        # GENERATE PATIENT ID
        # -----------------------------
        patient_id = generate_patient_id()
        
        with st.spinner("Analyzing symptoms..."):
            try:
                payload = {
                    "patient_id": patient_id,
                    "patient_name": patient_name,
                    "patient_phone": patient_phone,
                    "user_input": user_input
                }
                response = requests.post(N8N_WEBHOOK_URL, json=payload)
                response.raise_for_status()
                result = response.json()
            except Exception as e:
                st.error(f"Error connecting to n8n webhook: {e}")
                st.stop()

        # -----------------------------
        # CREATE PATIENT ✅
        # -----------------------------
        
        patient = {
            "Patient ID": patient_id,
            "Name": patient_name
        }

        st.session_state.patients.append(patient)

        # -----------------------------
        # CREATE SERVICE REQUEST ✅
        # -----------------------------
        request_id = generate_request_id()

        service_request = {
            "Request ID": request_id,
            "Patient ID": patient_id,
            "Patient Name": patient_name,
            "Category": result["category"],
            "Priority": result["priority"],
            "ETA (min)": result["eta"],
            "Notes": result["reply"]
        }

        st.session_state.service_requests.append(service_request)

        # -----------------------------
        # RESULT DISPLAY
        # -----------------------------
        st.success("✅ Triage Completed")

        st.subheader("📊 Result")
        st.write(f"**Patient ID:** {patient_id}")
        st.write(f"**Request ID:** {request_id}")
        st.write(f"**Category:** {result['category']}")
        st.write(f"**Priority:** {result['priority']}")
        st.write(f"**ETA:** {result['eta']} minutes")

        st.info(result["reply"])

# -----------------------------
# SHOW PATIENT LIST ✅
# -----------------------------
st.subheader("👥 Patient List")

if st.session_state.patients:
    df_patients = pd.DataFrame(st.session_state.patients)
    st.dataframe(df_patients, use_container_width=True)
else:
    st.write("No patients added yet")

# -----------------------------
# SHOW SERVICE REQUESTS ✅
# -----------------------------
st.subheader("📄 Service Requests")

if st.session_state.service_requests:
    df_requests = pd.DataFrame(st.session_state.service_requests)
    st.dataframe(df_requests, use_container_width=True)
else:
    st.write("No service requests available")
