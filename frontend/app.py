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
from backend.history import load_history
from backend.tool_eval import run_tool_eval
from data.dataset import ROUTING_DATASET, TOOL_CALL_DATASET

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


@app.route("/api/history", methods=["GET"])
def api_history():
    """Return stored evaluation history."""
    try:
        history = load_history()
        history_sorted = sorted(
            history,
            key=lambda record: record.get("timestamp", ""),
            reverse=True,
        )
        return jsonify({
            "success": True,
            "data": history_sorted,
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500


@app.route("/api/examples", methods=["GET"])
def api_examples():
    """Return evaluation examples for the selected type."""
    try:
        eval_type = request.args.get("eval_type", "handoff")
        if eval_type == "tool":
            examples = [
                {
                    "case_id": case.case_id,
                    "prompt": case.prompt,
                    "expected": case.expected_tool,
                }
                for case in TOOL_CALL_DATASET
            ]
        else:
            examples = [
                {
                    "case_id": case.case_id,
                    "prompt": case.prompt,
                    "expected": case.expected_agent,
                }
                for case in ROUTING_DATASET
            ]
        return jsonify({
            "success": True,
            "data": examples,
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500


if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5001)
