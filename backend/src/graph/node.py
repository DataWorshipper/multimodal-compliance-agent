import os
import time
from typing import Dict, Any
from backend.src.graph.state import AgentState, ComplianceIssue

def extract_video_data_node(state: AgentState) -> Dict[str, Any]:
    from backend.src.services.video_indexer import GeminiVideoProcessor
    import json
    
    url = state.video_url
    print(f"--> [Node: Extracting Video] Processing: {url}")
    
    processor = GeminiVideoProcessor()
    raw_context = processor.process_video(url)
    
    try:
        context_dict = json.loads(raw_context)
        transcript = context_dict.get("transcript", raw_context)
        ocr_text = context_dict.get("ocr_text", "")
    except:
        transcript = raw_context
        ocr_text = "OCR extraction unavailable."
    
    return {"transcript": transcript, "ocr_text": ocr_text}

def retrieve_compliance_rules_node(state: AgentState) -> Dict[str, Any]:
    from langchain_community.vectorstores import FAISS
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    
    print("--> [Node: Retrieving Rules] Querying FAISS knowledge base...")
    
    safe_transcript = str(state.transcript or "")
    safe_ocr = str(state.ocr_text or "")
    search_query = f"Transcript: {safe_transcript[:500]} | On-Screen: {safe_ocr[:200]}"
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    faiss_path = os.path.abspath(os.path.join(current_dir, "../../../backend/data/ftc_faiss_index"))
    
    try:
        vectorstore = FAISS.load_local(faiss_path, embeddings, allow_dangerous_deserialization=True)
        docs = vectorstore.similarity_search(search_query, k=4)
        rules = "\n\n".join([doc.page_content for doc in docs])
    except Exception as e:
        print(f"FAISS load error: {e}")
        rules = "Error loading local FTC rules."
        
    return {"compliance_rules": rules}
time.sleep(2)
def grade_documents_node(state: AgentState) -> Dict[str, Any]:
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    print("--> [Node: Grading Rules] Checking relevance...")
    
    safe_rules = str(state.compliance_rules or "")
    if "Error loading local FTC rules" in safe_rules:
        return {"needs_web_search": "yes"}
        
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", temperature=0)
    
    safe_transcript = str(state.transcript or "")
    safe_ocr = str(state.ocr_text or "")
    
    prompt = f"""
    You are a grader assessing relevance of retrieved compliance rules to a video's content.
    
    Spoken Transcript: {safe_transcript[:800]}
    On-Screen Text (OCR): {safe_ocr[:400]}
    
    Retrieved Rules: {safe_rules}
    
    If the rules cover topics related to the claims, sponsorships, or disclaimers present in EITHER the transcript or the on-screen text, grade it as 'yes'.
    If the rules are completely unrelated, grade it as 'no'.
    Respond ONLY with 'yes' or 'no'.
    """
    
    response = llm.invoke(prompt)
    grade = str(response.content).lower()
    
    return {"needs_web_search": "no" if "yes" in grade else "yes"}

def web_search_fallback_node(state: AgentState) -> Dict[str, Any]:
    from langchain_community.tools import DuckDuckGoSearchRun
    
    print("--> [Node: Web Search] Rules irrelevant. Searching DuckDuckGo...")
    search_tool = DuckDuckGoSearchRun()
    
    safe_transcript = str(state.transcript or "")
    query = f"FTC guidelines compliance for {safe_transcript[:100]} sponsorship disclosures"
    
    try:
        search_results = search_tool.invoke(query)
    except Exception:
        search_results = "Web search failed. Proceed with general FTC knowledge."
        
    return {"web_search_results": search_results}
time.sleep(2)
def crag_evaluation_node(state: AgentState) -> Dict[str, Any]:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from pydantic import BaseModel, Field
    
    print("--> [Node: Evaluation] Running final Gemini Audit...")
    
    safe_rules = str(state.compliance_rules or "")
    final_knowledge = safe_rules
    if state.needs_web_search == "yes":
        final_knowledge = f"Local Rules: {safe_rules}\n\nWeb Search Updates: {state.web_search_results}"
    
    class AuditResponse(BaseModel):
        status: str = Field(description="Must be 'PASS' or 'FAIL'")
        issues: list[ComplianceIssue] = Field(description="List of detected violations. Empty if PASS.")
        summary: str = Field(description="A concise final report of the audit.")

    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", temperature=0)
    structured_llm = llm.with_structured_output(AuditResponse)
    
    prompt = f"""
    You are an expert FTC Compliance Auditor.
    
    Spoken Transcript: {state.transcript}
    On-Screen Text (OCR): {state.ocr_text}
    
    Relevant FTC Guidelines & Knowledge: {final_knowledge}
    
    Task: Analyze the video context against the rules.
    1. Check if disclosures are clear, conspicuous, and upfront in BOTH audio and video.
    2. Flag any deceptive health claims or unsubstantiated guarantees.
    3. Output your findings precisely according to the required schema.
    """
    
    result = structured_llm.invoke(prompt)
    
    return {
        "final_status": result.status,
        "compliance_issues": result.issues,
        "final_report": result.summary
    }