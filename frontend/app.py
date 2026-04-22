import streamlit as st
import requests
import time

st.set_page_config(page_title="FTC Compliance Agent", page_icon="", layout="wide")

HF_API_URL = "https://swdqwewfw-ftc-compliance-agent.hf.space/stream_analyze"

st.sidebar.title("Agent Architecture")
st.sidebar.info(
    "**Backend:** Dockerized FastAPI on Hugging Face\n"
    "**Engine:** LangGraph CRAG Agent\n"
    "**Models:** Gemini 2.0 Flash + FAISS\n"
    "**Status:** Live via Streaming"
)

st.title("YouTube FTC Compliance Auditor")
st.markdown("Enter a YouTube URL to perform a multimodal audit of audio, OCR text, and metadata.")

video_url = st.text_input("YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Run Full Audit"):
    if not video_url:
        st.warning("Please enter a YouTube URL first.")
    else:
        with st.status("Agent Initializing...", expanded=True) as status:
            st.write("Connecting to Hugging Face backend...")
            
            try:
                with requests.post(
                    HF_API_URL, 
                    json={"url": video_url}, 
                    stream=True, 
                    timeout=600
                ) as response:
                    
                    if response.status_code == 200:
                        st.write("Connection established. Processing video...")
                        
                        log_container = st.empty()
                        full_log = ""
                        
                        for line in response.iter_lines():
                            if line:
                                decoded_line = line.decode('utf-8')
                                full_log += decoded_line + "\n"
                                st.write(decoded_line)
                        
                        status.update(label="Audit Complete", state="complete", expanded=False)
                        st.success("Analysis Finished")
                        
                        st.subheader("Audit Findings")
                        st.text_area("Final Report", value=full_log, height=300)
                        
                    else:
                        status.update(label="Error", state="error")
                        st.error(f"Backend Error {response.status_code}: {response.text}")
                        
            except requests.exceptions.Timeout:
                st.error("The audit took too long (over 10 minutes). Check the video length.")
            except Exception as e:
                st.error(f"Critical Connection Error: {e}")

st.divider()
