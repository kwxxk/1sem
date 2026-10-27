"""python serve.py --port 8000 (Git Bash / PowerShell 공통)"""
import argparse
import uvicorn
from movielab.webapi.app import create_app

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    options = parser.parse_args()
    uvicorn.run(create_app(), host="127.0.0.1", port=options.port, access_log=False, log_level="warning")
