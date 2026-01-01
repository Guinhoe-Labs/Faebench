from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import glob
import json

app = FastAPI()
OUTPUT_DIR = "/Users/derekzhu/Guinhoe Labs/Faebench/output"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/api/runs")
async def get_runs():
    try:
        # List all json files in output directory
        files = glob.glob(os.path.join(OUTPUT_DIR, "*.json"))
        # Sort by modification time, newest first
        files.sort(key=os.path.getmtime, reverse=True)
        
        runs = []
        for f in files:
            filename = os.path.basename(f)
            runs.append({
                "filename": filename,
                "created": os.path.getmtime(f)
            })
        return JSONResponse(content=runs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs/{filename}")
async def get_log(filename: str):
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Security check: ensure file is in output dir (prevent directory traversal)
    if not os.path.abspath(filepath).startswith(os.path.abspath(OUTPUT_DIR)):
         raise HTTPException(status_code=403, detail="Access denied")
         
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Log not found")
        
    return FileResponse(filepath)

@app.get("/")
async def serve_viewer():
    return FileResponse(os.path.join(os.path.dirname(os.path.abspath(__file__)), "viewer.html"))

# Serve other static files if needed (like if we had a css/js folder, but viewer.html is standalone for now)
# app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    print(f"Starting FastAPI server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
