"""
Flask web application for running agent evaluations.
"""
import asyncio
import sys
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# Ensure the agent_evals root is on sys.path for imports
agent_evals_root = Path(__file__).parent.parent
if str(agent_evals_root) not in sys.path:
    sys.path.insert(0, str(agent_evals_root))

from backend.handoff_eval import run_handoff_eval
from backend.tool_eval import run_tool_eval

# Set template folder explicitly to frontend/templates
template_dir = Path(__file__).parent / "templates"
app = Flask(__name__, template_folder=str(template_dir))
# Configure CORS to allow all origins (for local development)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/")
def index():
    """Serve the main UI page."""
    return render_template("index.html")


@app.route("/api/run-handoff-eval", methods=["POST"])
def api_run_handoff_eval():
    """Run handoff evaluation and return results."""
    try:
        data = request.get_json() or {}
        model = data.get("model", "gpt-4.1-mini")
        
        # Run the async evaluation
        result = asyncio.run(run_handoff_eval(model=model, verbose=False))
        
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/run-tool-eval", methods=["POST"])
def api_run_tool_eval():
    """Run tool call evaluation and return results."""
    try:
        data = request.get_json() or {}
        model = data.get("model", "gpt-4.1-mini")
        
        # Run the async evaluation
        result = asyncio.run(run_tool_eval(model=model, verbose=False))
        
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5001)

