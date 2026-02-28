"""Start both backend and frontend dev servers."""

import subprocess
import sys
import os
import signal

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    processes = []

    try:
        # Start backend
        print("Starting backend (FastAPI) on http://localhost:8000 ...")
        backend = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000"],
            cwd=ROOT_DIR,
        )
        processes.append(backend)

        # Start frontend
        print("Starting frontend (Vite) on http://localhost:5173 ...")
        frontend = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=os.path.join(ROOT_DIR, "frontend"),
            shell=True,
        )
        processes.append(frontend)

        print("\nBoth servers running. Press Ctrl+C to stop.\n")

        # Wait for either process to exit
        for p in processes:
            p.wait()

    except KeyboardInterrupt:
        print("\nShutting down...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.wait()


if __name__ == "__main__":
    main()
