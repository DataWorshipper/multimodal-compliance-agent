from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.src.graph.workflow import compliance_graph

app = FastAPI(title="FTC Compliance Agent API")

class VideoRequest(BaseModel):
    url: str

@app.get("/")
def health_check():
    return {"status": "Backend is alive and ready to audit!"}

@app.post("/analyze")
def analyze_video(request: VideoRequest):
    try:
        initial_state = {"video_url": request.url}
        
        print(f"\n Starting audit for: {request.url}")
        result = compliance_graph.invoke(initial_state)
        
        raw_issues = result.get("compliance_issues", [])
        serialized_issues = [
            issue.model_dump() if hasattr(issue, "model_dump") else issue
            for issue in raw_issues
        ]
        
        return {
            "status": "success",
            "final_status": result.get("final_status", "UNKNOWN"),
            "final_report": result.get("final_report", "No report generated."),
            "compliance_issues": serialized_issues
        }
        
    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))