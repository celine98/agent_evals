#!/usr/bin/env python
"""
Entry point script to run the Flask application.
This allows running the app directly without module path issues.
Run this from within the agent_evals folder.
"""
from pathlib import Path
import sys


# Ensure the current directory (agent_evals) is on sys.path
THIS_FILE = Path(__file__).resolve()
AGENT_EVALS_ROOT = THIS_FILE.parent

if str(AGENT_EVALS_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_EVALS_ROOT))

from frontend.app import app


if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5001)


