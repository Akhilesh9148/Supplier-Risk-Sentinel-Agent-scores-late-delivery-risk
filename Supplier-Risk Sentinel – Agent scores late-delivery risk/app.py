import streamlit as st
import pandas as pd
import requests

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Supplier Risk Sentinel", layout="wide")

# ---------------- HEADER LOGO ----------------
logo_path = "https://trigent.com/wp-content/uploads/Trigent_Axlr8_Labs.png"
st.markdown(
    f"""
    <div style="text-align:center;">
        <img src="{logo_path}" alt="Trigent Logo" style="max-width:100%;">
    </div>
    """,
    unsafe_allow_html=True
)

st.title("📊 Supplier Risk Sentinel Dashboard")

# ---------------- FILE UPLOAD ----------------
st.header("📁 Upload Supplier Data")

uploaded_file = st.file_uploader(
    "Upload CSV (Recommended) or Excel file",
    type=["csv", "xlsx"]
)

# ---------------- PROCESS DATA ----------------
if uploaded_file is not None:

    try:
        # FIX 3: Avoid Excel dependency issues
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, engine="openpyxl")

        st.success("✅ File uploaded successfully!")

        # ---------------- VALIDATION ----------------
        required_columns = ["Vendor ID", "Total Orders", "Late Deliveries"]

        if not all(col in df.columns for col in required_columns):
            st.error("❌ File must contain: Vendor ID, Total Orders, Late Deliveries")
        else:

            # ---------------- CALCULATIONS ----------------
            df["Late %"] = df["Late Deliveries"] / df["Total Orders"]

            def calculate_risk(late):
                if late > 0.5:
                    return 0.9
                elif late > 0.3:
                    return 0.8
                else:
                    return 0.2

            df["Risk Score"] = df["Late %"].apply(calculate_risk)

            # ---------------- DISPLAY TABLE ----------------
            st.subheader("📋 Supplier Data Overview")

            def highlight_risk(val):
                if val > 0.8:
                    return "background-color: red; color: white;"
                elif val > 0.5:
                    return "background-color: orange;"
                return ""

            styled_df = df.style.applymap(highlight_risk, subset=["Risk Score"])
            st.dataframe(styled_df, use_container_width=True)

            # ---------------- HIGH RISK ALERT ----------------
            st.subheader("🚨 High Risk Vendors")

            high_risk = df[df["Risk Score"] > 0.8]

            if not high_risk.empty:
                for _, row in high_risk.iterrows():
                    st.error(
                        f"Vendor {row['Vendor ID']} is HIGH RISK ⚠️ | "
                        f"Late Delivery: {round(row['Late %']*100, 2)}% | "
                        f"Risk Score: {row['Risk Score']}"
                    )
            else:
                st.success("No high-risk vendors detected.")

            # ---------------- SPECIAL CASE ----------------
            st.subheader("🔍 Highlight Example")

            vendor_17 = df[df["Vendor ID"] == 17]

            if not vendor_17.empty:
                row = vendor_17.iloc[0]
                st.warning(
                    f"Red-Flag Vendor #{int(row['Vendor ID'])} 🚨\n\n"
                    f"Late Deliveries: {row['Late Deliveries']} out of {row['Total Orders']}\n"
                    f"Late Percentage: {round(row['Late %']*100, 2)}%\n"
                    f"Risk Score: {row['Risk Score']}"
                )

            # ---------------- TRIGGER AI WORKFLOW ----------------
            st.subheader("🤖 AI Risk Analysis")
            
            # Hardcoded webhook URL to hide it from the frontend UI
            webhook_url = "http://localhost:5678/webhook-test/supply-waste-webhook"
            
            if st.button("Generate AI Risk Summary"):
                with st.spinner("Analyzing supplier data with AI..."):
                    try:
                        # Send POST request to n8n webhook with the dataframe data
                        payload = {"data": df.to_dict(orient="records")}
                        response = requests.post(webhook_url, json=payload)
                        
                        if response.status_code == 200:
                            try:
                                result = response.json()
                                
                                # Handle single dict response (like {"text": "..."} or {"output": "..."})
                                if isinstance(result, list) and len(result) > 0 and "text" in result[0]:
                                     # sometimes webhooks return a list with one item dict
                                     text_result = result[0].get("text")
                                     st.success("✨ AI Analysis Complete!")
                                     st.info(f"**💡 Insight:** {text_result}")
                                elif isinstance(result, dict) and ("text" in result or "output" in result):
                                    text_result = result.get("text") or result.get("output")
                                    st.success("✨ AI Analysis Complete!")
                                    st.info(f"**💡 Insight:** {text_result}")
                                    
                                # Handle tabular list response
                                elif isinstance(result, list) and len(result) > 0:
                                    st.success("✨ AI Analysis Complete!")
                                    st.markdown("### 🧠 Processed AI Supplier Data")
                                    
                                    # Flatten nested n8n "json" wrapper if present
                                    if "json" in result[0]:
                                        clean_result = [r["json"] for r in result]
                                    else:
                                        clean_result = result
                                        
                                    response_df = pd.DataFrame(clean_result)
                                    
                                    # Apply risk styling if Risk Score is returned
                                    if "Risk Score" in response_df.columns:
                                        styled_resp = response_df.style.applymap(highlight_risk, subset=["Risk Score"])
                                        st.dataframe(styled_resp, use_container_width=True)
                                    else:
                                        st.dataframe(response_df, use_container_width=True)
                                        
                                # Handle other JSON formats elegantly
                                else:
                                    st.success("✨ AI Analysis Complete!")
                                    st.write("### 🧠 AI Response Data")
                                    st.json(result)
                                    
                            except ValueError:
                                # Fallback if response is text but not JSON
                                st.success("✨ AI Analysis Complete!")
                                st.info(f"**💡 Insight:** {response.text}")
                        else:
                            st.error(f"❌ Failed to reach AI backend. Status Code: {response.status_code}")
                            st.write(response.text)
                    except requests.exceptions.RequestException as e:
                        st.error(f"❌ Connection error. Please verify the n8n backend is running. Details: {e}")

            # ---------------- DOWNLOAD ----------------
            st.download_button(
                label="⬇️ Download Processed Data",
                data=df.to_csv(index=False),
                file_name="processed_supplier_data.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error("❌ Error reading file. Please upload a valid CSV or install openpyxl for Excel.")

else:
    st.info("👈 Upload a CSV (recommended) or Excel file to begin.")

# ---------------- FOOTER ----------------
footer_html = """
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
<div style="text-align: center;">
<p>
Copyright © 2024 |
<a href="https://trigent.com/ai/" target="_blank">Trigent Software Inc.</a>
All rights reserved. |
<a href="https://www.linkedin.com/company/trigent-software/" target="_blank"><i class="fab fa-linkedin"></i></a> |
<a href="https://www.twitter.com/trigentsoftware/" target="_blank"><i class="fab fa-twitter"></i></a> |
<a href="https://www.youtube.com/channel/UCNhAbLhnkeVvV6MBFUZ8hOw" target="_blank"><i class="fab fa-youtube"></i></a>
</p>
</div>
"""

footer_css = """
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: white;
    text-align: center;
}
</style>
"""

footer = f"{footer_css}<div class='footer'>{footer_html}</div>"
st.markdown(footer, unsafe_allow_html=True)