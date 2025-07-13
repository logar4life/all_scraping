from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import subprocess
import sys
import os
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import uvicorn

app = FastAPI(
    title="PDF Scraping and Analysis API",
    description="API for scraping PDFs from Loudoun County, PWCBA, and Fairfax websites and analyzing them",
    version="1.0.0"
)

# Global variables to track current process status for each service
loudoun_process_status = {
    "is_running": False,
    "current_step": None,
    "progress": 0,
    "start_time": None,
    "end_time": None,
    "error": None,
    "results": None
}

pwcba_process_status = {
    "is_running": False,
    "current_step": None,
    "progress": 0,
    "start_time": None,
    "end_time": None,
    "error": None,
    "results": None
}

fairfax_process_status = {
    "is_running": False,
    "current_step": None,
    "progress": 0,
    "start_time": None,
    "end_time": None,
    "error": None,
    "results": None
}

def run_script(script_path: str, step_name: str) -> Dict[str, Any]:
    """Run a Python script and return the result"""
    try:
        print(f"🚀 Starting {step_name}...")
        
        # Run the script
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(script_path)
        )
        
        if result.returncode == 0:
            print(f"✅ {step_name} completed successfully")
            return {
                "success": True,
                "output": result.stdout,
                "error": result.stderr
            }
        else:
            print(f"❌ {step_name} failed with return code {result.returncode}")
            return {
                "success": False,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
            
    except Exception as e:
        print(f"❌ Error running {step_name}: {str(e)}")
        return {
            "success": False,
            "output": "",
            "error": str(e)
        }

async def run_loudoun_process():
    """Run the complete Loudoun scraping and analysis process"""
    global loudoun_process_status
    
    try:
        loudoun_process_status["is_running"] = True
        loudoun_process_status["start_time"] = datetime.now().isoformat()
        loudoun_process_status["error"] = None
        loudoun_process_status["results"] = None
        
        # Get the absolute path to the loudoun directory
        loudoun_dir = Path(__file__).parent / "loudoun"
        
        # Step 1: Run loudoun.py (web scraping)
        print("📋 Step 1: Running web scraping...")
        loudoun_process_status["progress"] = 10
        loudoun_process_status["current_step"] = "Web Scraping (loudoun.py)"
        step1_result = run_script(
            str(loudoun_dir / "loudoun.py"),
            "Web Scraping (loudoun.py)"
        )
        
        if not step1_result["success"]:
            raise Exception(f"Web scraping failed: {step1_result['error']}")
        
        # Step 2: Run loudoun_pdf_processor.py (PDF processing)
        print("📋 Step 2: Running PDF processing...")
        loudoun_process_status["progress"] = 50
        loudoun_process_status["current_step"] = "PDF Processing (loudoun_pdf_processor.py)"
        step2_result = run_script(
            str(loudoun_dir / "loudoun_pdf_processor.py"),
            "PDF Processing (loudoun_pdf_processor.py)"
        )
        
        if not step2_result["success"]:
            raise Exception(f"PDF processing failed: {step2_result['error']}")
        
        # Step 3: Run loudoun_pdf_analyzer.py (PDF analysis)
        print("📋 Step 3: Running PDF analysis...")
        loudoun_process_status["progress"] = 90
        loudoun_process_status["current_step"] = "PDF Analysis (loudoun_pdf_analyzer.py)"
        step3_result = run_script(
            str(loudoun_dir / "loudoun_pdf_analyzer.py"),
            "PDF Analysis (loudoun_pdf_analyzer.py)"
        )
        
        if not step3_result["success"]:
            raise Exception(f"PDF analysis failed: {step3_result['error']}")
        
        # Process completed successfully
        loudoun_process_status["progress"] = 100
        loudoun_process_status["end_time"] = datetime.now().isoformat()
        loudoun_process_status["results"] = {
            "step1": step1_result,
            "step2": step2_result,
            "step3": step3_result
        }
        
        print("🎉 All Loudoun steps completed successfully!")
        
    except Exception as e:
        loudoun_process_status["error"] = str(e)
        loudoun_process_status["end_time"] = datetime.now().isoformat()
        print(f"❌ Loudoun process failed: {str(e)}")
        raise e
    finally:
        loudoun_process_status["is_running"] = False
        loudoun_process_status["current_step"] = None

async def run_pwcba_process():
    """Run the complete PWCBA scraping and analysis process"""
    global pwcba_process_status
    
    try:
        pwcba_process_status["is_running"] = True
        pwcba_process_status["start_time"] = datetime.now().isoformat()
        pwcba_process_status["error"] = None
        pwcba_process_status["results"] = None
        
        # Get the absolute path to the pwcba directory
        pwcba_dir = Path(__file__).parent / "pwcba"
        
        # Step 1: Run pwcba.py (web scraping)
        print("📋 Step 1: Running PWCBA web scraping...")
        pwcba_process_status["progress"] = 10
        pwcba_process_status["current_step"] = "Web Scraping (pwcba.py)"
        step1_result = run_script(
            str(pwcba_dir / "pwcba.py"),
            "Web Scraping (pwcba.py)"
        )
        
        if not step1_result["success"]:
            raise Exception(f"PWCBA web scraping failed: {step1_result['error']}")
        
        # Step 2: Run pwcba_pdf_processor.py (PDF processing)
        print("📋 Step 2: Running PWCBA PDF processing...")
        pwcba_process_status["progress"] = 50
        pwcba_process_status["current_step"] = "PDF Processing (pwcba_pdf_processor.py)"
        step2_result = run_script(
            str(pwcba_dir / "pwcba_pdf_processor.py"),
            "PDF Processing (pwcba_pdf_processor.py)"
        )
        
        if not step2_result["success"]:
            raise Exception(f"PWCBA PDF processing failed: {step2_result['error']}")
        
        # Step 3: Run pwcba_pdf_analyzer.py (PDF analysis)
        print("📋 Step 3: Running PWCBA PDF analysis...")
        pwcba_process_status["progress"] = 90
        pwcba_process_status["current_step"] = "PDF Analysis (pwcba_pdf_analyzer.py)"
        step3_result = run_script(
            str(pwcba_dir / "pwcba_pdf_analyzer.py"),
            "PDF Analysis (pwcba_pdf_analyzer.py)"
        )
        
        if not step3_result["success"]:
            raise Exception(f"PWCBA PDF analysis failed: {step3_result['error']}")
        
        # Process completed successfully
        pwcba_process_status["progress"] = 100
        pwcba_process_status["end_time"] = datetime.now().isoformat()
        pwcba_process_status["results"] = {
            "step1": step1_result,
            "step2": step2_result,
            "step3": step3_result
        }
        
        print("🎉 All PWCBA steps completed successfully!")
        
    except Exception as e:
        pwcba_process_status["error"] = str(e)
        pwcba_process_status["end_time"] = datetime.now().isoformat()
        print(f"❌ PWCBA process failed: {str(e)}")
        raise e
    finally:
        pwcba_process_status["is_running"] = False
        pwcba_process_status["current_step"] = None

async def run_fairfax_process():
    """Run the complete Fairfax scraping and analysis process"""
    global fairfax_process_status
    
    try:
        fairfax_process_status["is_running"] = True
        fairfax_process_status["start_time"] = datetime.now().isoformat()
        fairfax_process_status["error"] = None
        fairfax_process_status["results"] = None
        
        # Get the absolute path to the fairfax directory
        fairfax_dir = Path(__file__).parent / "fairfax"
        
        # Step 1: Run fairfax.py (web scraping)
        print("📋 Step 1: Running Fairfax web scraping...")
        fairfax_process_status["progress"] = 10
        fairfax_process_status["current_step"] = "Web Scraping (fairfax.py)"
        step1_result = run_script(
            str(fairfax_dir / "fairfax.py"),
            "Web Scraping (fairfax.py)"
        )
        
        if not step1_result["success"]:
            raise Exception(f"Fairfax web scraping failed: {step1_result['error']}")
        
        # Step 2: Run fairfax_pdf_processor.py (PDF processing)
        print("📋 Step 2: Running Fairfax PDF processing...")
        fairfax_process_status["progress"] = 50
        fairfax_process_status["current_step"] = "PDF Processing (fairfax_pdf_processor.py)"
        step2_result = run_script(
            str(fairfax_dir / "fairfax_pdf_processor.py"),
            "PDF Processing (fairfax_pdf_processor.py)"
        )
        
        if not step2_result["success"]:
            raise Exception(f"Fairfax PDF processing failed: {step2_result['error']}")
        
        # Step 3: Run fairfax_image_analyzer.py (Image analysis)
        print("📋 Step 3: Running Fairfax image analysis...")
        fairfax_process_status["progress"] = 90
        fairfax_process_status["current_step"] = "Image Analysis (fairfax_image_analyzer.py)"
        step3_result = run_script(
            str(fairfax_dir / "fairfax_image_analyzer.py"),
            "Image Analysis (fairfax_image_analyzer.py)"
        )
        
        if not step3_result["success"]:
            raise Exception(f"Fairfax image analysis failed: {step3_result['error']}")
        
        # Process completed successfully
        fairfax_process_status["progress"] = 100
        fairfax_process_status["end_time"] = datetime.now().isoformat()
        fairfax_process_status["results"] = {
            "step1": step1_result,
            "step2": step2_result,
            "step3": step3_result
        }
        
        print("🎉 All Fairfax steps completed successfully!")
        
    except Exception as e:
        fairfax_process_status["error"] = str(e)
        fairfax_process_status["end_time"] = datetime.now().isoformat()
        print(f"❌ Fairfax process failed: {str(e)}")
        raise e
    finally:
        fairfax_process_status["is_running"] = False
        fairfax_process_status["current_step"] = None

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "PDF Scraping and Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "/": "Home - API information",
            "/loudoun": "Run Loudoun County scraping and analysis process",
            "/pwcba": "Run PWCBA scraping and analysis process",
            "/fairfax": "Run Fairfax scraping and analysis process"
        }
    }

@app.post("/loudoun")
async def run_loudoun_scraping(background_tasks: BackgroundTasks):
    """Run the complete Loudoun scraping and analysis process"""
    
    if loudoun_process_status["is_running"]:
        raise HTTPException(
            status_code=409,
            detail="Loudoun process is already running. Please wait for completion."
        )
    
    # Start the process in background
    background_tasks.add_task(run_loudoun_process)
    
    return {
        "message": "Loudoun scraping process started",
        "status": "running"
    }

@app.post("/pwcba")
async def run_pwcba_scraping(background_tasks: BackgroundTasks):
    """Run the complete PWCBA scraping and analysis process"""
    
    if pwcba_process_status["is_running"]:
        raise HTTPException(
            status_code=409,
            detail="PWCBA process is already running. Please wait for completion."
        )
    
    # Start the process in background
    background_tasks.add_task(run_pwcba_process)
    
    return {
        "message": "PWCBA scraping process started",
        "status": "running"
    }

@app.post("/fairfax")
async def run_fairfax_scraping(background_tasks: BackgroundTasks):
    """Run the complete Fairfax scraping and analysis process"""
    
    if fairfax_process_status["is_running"]:
        raise HTTPException(
            status_code=409,
            detail="Fairfax process is already running. Please wait for completion."
        )
    
    # Start the process in background
    background_tasks.add_task(run_fairfax_process)
    
    return {
        "message": "Fairfax scraping process started",
        "status": "running"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
