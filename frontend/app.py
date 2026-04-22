import streamlit as st
import requests

st.set_page_config(page_title="FTC Compliance Agent", page_icon="🕵️‍♂️", layout="wide")

st.sidebar.title("About")
st.sidebar.info(
    "This multimodal CRAG agent uses Gemini 2.5 Flash to audit YouTube videos against FTC guidelines. "
    "It extracts spoken audio and on-screen OCR text, compares it against local FAISS rulebooks, "
    "and checks the live web for recent updates."
)

st.title(" YouTube FTC Compliance Auditor")

video_url = st.text_input(" Enter YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Run Compliance Audit"):
    if not video_url:
        st.warning(" Please enter a YouTube URL first.")
    else:
        with st.spinner("Downloading video, running Gemini OCR & Audio extraction, and executing CRAG rules..."):
            try:
                response = requests.post("http://127.0.0.1:8888/analyze", json={"url": video_url})
                
                if response.status_code == 200:
                    data = response.json()
                    
                    final_status = data.get("final_status", "UNKNOWN").upper()
                    if final_status == "PASS":
                        st.success(" **STATUS: PASS** - No major compliance violations detected.")
                    else:
                        st.error(" **STATUS: FAIL** - Compliance violations detected.")
                    
                    st.subheader(" Audit Summary")
                    st.write(data.get("final_report", "No summary provided."))
                    
                    issues = data.get("compliance_issues", [])
                    if issues:
                        st.subheader(" Detailed Violations")
                        for issue in issues:
                            severity = str(issue.get("severity", "Warning")).upper()
                            category = issue.get("category", "General")
                            desc = issue.get("description", "")
                            
                            if "CRITICAL" in severity or "HIGH" in severity:
                                st.error(f"**[{severity}] {category}**: {desc}")
                            elif "MINOR" in severity or "LOW" in severity:
                                st.info(f"**[{severity}] {category}**: {desc}")
                            else:
                                st.warning(f"**[{severity}] {category}**: {desc}")
                                
                    elif final_status == "FAIL":
                        st.warning("The system flagged this as a FAIL but no specific structured issues were parsed.")
                        
                else:
                    st.error(f"Backend Error {response.status_code}: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error(" Connection Refused: Your FastAPI backend isn't running. Start it on port 8000!")