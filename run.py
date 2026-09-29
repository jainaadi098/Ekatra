# run.py
import uvicorn
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("===================================================================")
    print("  PM-AJAY Livelihood Voice Assistant & NSQF Matching System        ")
    print("  Department of Social Justice and Empowerment (MoSJE) - Prototype ")
    print("===================================================================")
    print("[*] Running local server on http://127.0.0.1:8000")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)