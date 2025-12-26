# Agent Evaluation Dashboard

A web UI for running and viewing agent evaluation results.

## Features

- **Run Handoff Evaluations**: Test whether the orchestrator routes to the correct specialist agent
- **Run Tool Call Evaluations**: Test whether the operational agent calls the correct tools
- **View Results**: See overall accuracy and detailed test case results in a table format
- **Export Results**: Both handoff and tool call evaluation results are automatically saved to CSV files with timestamps

## Setup

1. Navigate to the `agent_evals` folder:
```bash
cd agent_evals
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

4. Run the Flask app:
```bash
python run_app.py
```

Alternatively, you can run the app directly:
```bash
python -m frontend.app
```

5. Open your browser and navigate to:
```
http://127.0.0.1:5001
```

## Usage

### Web UI

1. Click "Run Handoff Evaluation" to test routing accuracy
2. Click "Run Tool Call Evaluation" to test tool call accuracy
3. View the results:
   - Overall accuracy percentage
   - Number of correct vs total test cases
   - Detailed table showing each test case with:
     - Message (the input prompt)
     - Target (expected output)
     - Output (actual output)
     - Status (correct/incorrect)

### Results Storage

When you run evaluations (either through the UI or command line), results are automatically saved to CSV files in the `results/` directory. Each evaluation run creates a new file with a timestamp:

#### Handoff Evaluations
- **File naming**: `handoff_evals_YYYYMMDD_HHMMSS.csv`
- **Columns**:
  - `message`: The input prompt/test case
  - `target`: Expected agent/routing target
  - `output`: Actual agent/routing result
- **Example**: `handoff_evals_20251226_162216.csv`

#### Tool Call Evaluations
- **File naming**: `tool_call_evals_YYYYMMDD_HHMMSS.csv`
- **Columns**:
  - `message`: The input prompt/test case
  - `target`: Expected tool name
  - `output`: Actual tool name that was called
- **Example**: `tool_call_evals_20251226_162216.csv`

**Location**: All CSV files are saved to `agent_evals/results/`

This allows you to track evaluation results over time and compare performance across different runs.

## Project Structure

```
agent_evals/
├── run_app.py              # Main entry point to run the Flask app
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── backend/                # Evaluation logic
│   ├── agent_list.py      # Agent definitions
│   ├── handoff_eval.py    # Handoff evaluation implementation
│   ├── tool_eval.py       # Tool call evaluation implementation
│   ├── tools.py           # Tool definitions
│   └── utils.py           # Utility functions
├── data/                   # Test datasets
│   ├── dataset.py         # Dataset loading logic
│   ├── routing_dataset.csv
│   └── tool_call_dataset.csv
├── results/                # Evaluation results (auto-generated)
│   ├── handoff_evals_*.csv # Timestamped CSV files with handoff evaluation results
│   └── tool_call_evals_*.csv # Timestamped CSV files with tool call evaluation results
└── frontend/               # Web UI
    ├── app.py             # Flask web application with API endpoints
    └── templates/
        └── index.html     # Frontend UI
```

## Running Evaluations from Command Line

You can also run evaluations directly from the command line:

```bash
# Run handoff evaluation
python -m backend.handoff_eval

# Run tool call evaluation
python -m backend.tool_eval
```

Make sure you're in the `agent_evals` directory when running these commands.

**Note**: When running evaluations from the command line, results are automatically saved to CSV files:
- Handoff evaluations: `results/handoff_evals_[timestamp].csv`
- Tool call evaluations: `results/tool_call_evals_[timestamp].csv`

The file path will be printed to the console when each evaluation completes.

