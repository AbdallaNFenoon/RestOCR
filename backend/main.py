import os
import sys

# Ensure base directory is in sys.path for backend package resolution
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import logging
import webbrowser
import threading
import time
from typing import Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.gemini_service import extract_menu_from_file
from backend.excel_service import generate_excel, generate_excel_in_memory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RestOCR")

# Determine base paths (crucial for PyInstaller compatibility)
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    logger.info(f"Running in PyInstaller bundle. Base Dir: {BASE_DIR}")
else:
    # Running in normal python environment
    logger.info(f"Running in dev mode. Base Dir: {BASE_DIR}")

# Define directories
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
TEMPLATE_PATH = os.path.join(BASE_DIR, "backend", "template.xlsx")
# Fallback path if running inside a bundle
if not os.path.exists(TEMPLATE_PATH):
    TEMPLATE_PATH = os.path.join(BASE_DIR, "template.xlsx")

logger.info(f"Template Excel Path configured to: {TEMPLATE_PATH}")

app = FastAPI(title="RestOCR API")

# Add CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/process")
async def process_menu(
    file: UploadFile = File(...),
    api_key: str = Form(...)
):
    """
    Endpoint to upload a menu document and extract structured JSON using Gemini API
    """
    logger.info(f"Received file: {file.filename}, size: {file.size} bytes")
    
    if not api_key:
        raise HTTPException(status_code=400, detail="Gemini API Key is required")
        
    try:
        content = await file.read()
        mime_type = file.content_type or "image/png"
        
        # Call Gemini extraction service
        extracted_data = extract_menu_from_file(api_key, content, mime_type, file.filename)
        return extracted_data
        
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error parsing document: {str(e)}"}
        )

@app.post("/api/export")
async def export_menu(menu_data: Dict[str, Any]):
    """
    Endpoint to export edited JSON menu data into the Excel spreadsheet template
    """
    logger.info("Received request to export menu to Excel")
    try:
        # Generate workbook in memory
        file_bytes = generate_excel_in_memory(menu_data, TEMPLATE_PATH)
        
        # Return generated file directly as Response attachment
        return Response(
            content=file_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=menu_extracted.xlsx"
            }
        )
        
    except Exception as e:
        logger.error(f"Export error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error generating Excel file: {str(e)}"}
        )

@app.post("/api/shutdown")
async def shutdown():
    """
    Gracefully shuts down the local FastAPI server
    """
    logger.info("Shutdown request received. Stopping server...")
    
    def stop_server():
        time.sleep(1)
        os._exit(0)
        
    threading.Thread(target=stop_server).start()
    return {"status": "shutting down"}

# Serve frontend static assets (must be registered last)
if os.path.exists(FRONTEND_DIR):
    logger.info(f"Serving frontend static files from: {FRONTEND_DIR}")
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    logger.warning(f"Frontend directory not found at: {FRONTEND_DIR}. API only mode.")

def open_browser():
    """Opens browser after server startup delay"""
    time.sleep(1.5)
    url = "http://127.0.0.1:8000"
    logger.info(f"Opening default browser at: {url}")
    webbrowser.open(url)

if __name__ == "__main__":
    # Autolaunch browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run server (passing the app object directly to avoid import issues inside the bundle)
    uvicorn.run(app, host="127.0.0.1", port=8000)
