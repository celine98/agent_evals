"""
Tool call evaluation: Evaluate whether the operational agent calls the correct tool
for banking operation requests.

Prereqs:
  pip install openai-agents
  export OPENAI_API_KEY="..."

Docs:
  Sessions (incl. OpenAIConversationsSession): https://openai.github.io/openai-agents-python/sessions/
  Results / Tool calls: https://openai.github.io/openai-agents-python/results/
"""
import asyncio
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from agents import Runner, OpenAIConversationsSession

from .agent_list import build_agents
from data.dataset import TOOL_CALL_DATASET
from .history import append_history, build_run_metadata
from .utils import get_conversation_id, extract_tool_calls


def save_results_to_csv(
    results: List[Dict[str, Any]],
    metadata: Dict[str, Any],
    output_dir: Optional[Path] = None,
) -> str:
    """
    Save tool call evaluation results to a CSV file.
    
    Args:
        results: List of result dictionaries with 'message', 'target', and 'output' keys
        metadata: Run metadata to include in the CSV rows
        output_dir: Directory to save the CSV file. If None, uses agent_evals/results directory.
    
    Returns:
        Path to the saved CSV file
    """
    if output_dir is None:
        # Get the agent_evals root directory (parent of backend)
        agent_evals_root = Path(__file__).parent.parent
        output_dir = agent_evals_root / "results"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tool_call_evals_{timestamp}.csv"
    filepath = output_dir / filename
    
    # Write CSV file
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'run_id',
            'timestamp',
            'model',
            'dataset',
            'eval_type',
            'message',
            'target',
            'output',
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow({
                'run_id': metadata.get('run_id', ''),
                'timestamp': metadata.get('timestamp', ''),
                'model': metadata.get('model', ''),
                'dataset': metadata.get('dataset', ''),
                'eval_type': metadata.get('eval_type', ''),
                'message': result.get('message', ''),
                'target': result.get('target', ''),
                'output': result.get('output', ''),
            })
    
    return str(filepath)


async def run_tool_eval(model: str = "gpt-4.1-mini", verbose: bool = True) -> Dict[str, Any]:
    """
    Run the tool call evaluation.
    
    Returns:
        Dict with 'accuracy', 'correct', 'total', and 'results' (list of test cases)
    """
    # Get the operational agent directly (we'll use it without the orchestrator)
    _, operational_agent, _, _ = build_agents(model=model)
    metadata = build_run_metadata(
        model=model,
        dataset="TOOL_CALL_DATASET",
        eval_type="tool",
    )

    # Phase 1: run dataset prompts, store each in OpenAI-hosted session
    stored_runs: List[Dict[str, Any]] = []

    if verbose:
        print("\n=== Phase 1: Generate conversations and store in OpenAI-hosted Sessions ===")
    for case in TOOL_CALL_DATASET:
        session = OpenAIConversationsSession()  # OpenAI-hosted storage

        result = await Runner.run(
            operational_agent,
            case.prompt,
            session=session,
        )

        if verbose:
            print(result.new_items)

        called_tools = extract_tool_calls(result)
        # Get the first tool called (or empty string if none)
        actual_tool = called_tools[0] if called_tools else "None"
        conv_id = await get_conversation_id(session)

        stored_runs.append(
            {
                "case_id": case.case_id,
                "expected": case.expected_tool,
                "actual": actual_tool,
                "all_tools_called": called_tools,
                "conversation_id": conv_id,
                "final_output": result.final_output,
            }
        )

        if verbose:
            print(f"- {case.case_id}: expected={case.expected_tool:20s} actual={actual_tool:20s} conv_id={conv_id}")

    # Phase 2: reload sessions and run evaluation
    if verbose:
        print("\n=== Phase 2: Reload sessions and evaluate tool call accuracy ===")
    correct = 0
    results = []

    for row in stored_runs:
        # Reload the session by conversation_id
        session2 = OpenAIConversationsSession(conversation_id=row["conversation_id"])

        # Demonstrate we can fetch stored history
        items = await session2.get_items()
        n_items = len(items)

        is_correct = (row["actual"] == row["expected"])
        correct += int(is_correct)

        # Build result for UI
        results.append({
            "message": next((c.prompt for c in TOOL_CALL_DATASET if c.case_id == row["case_id"]), ""),
            "target": row["expected"],
            "output": row["actual"],
            "correct": is_correct,
        })

        if verbose:
            status = "✅" if is_correct else "❌"
            all_tools_str = ", ".join(row["all_tools_called"]) if row["all_tools_called"] else "None"
            print(
                f"{status} {row['case_id']} | expected={row['expected']}, actual={row['actual']} | "
                f"all_tools=[{all_tools_str}] | reloaded_items={n_items}"
            )

    total = len(stored_runs)
    acc = correct / total if total else 0.0
    
    # Save results to CSV
    csv_path = save_results_to_csv(results, metadata)
    history_record = {
        **metadata,
        "accuracy": acc,
        "correct": correct,
        "total": total,
        "csv_path": csv_path,
    }
    append_history(history_record)
    if verbose:
        print(f"\nResults saved to: {csv_path}")
    
    if verbose:
        print(f"\nAccuracy: {correct}/{total} = {acc:.2%}")
        print("\nDone.")
        print("Tip: Open Traces to visualize tool calls and debug incorrect tool selections (Tracing is enabled by default).")
    
    return {
        "accuracy": acc,
        "correct": correct,
        "total": total,
        "results": results,
        "csv_path": csv_path,
        "metadata": metadata,
    }


if __name__ == "__main__":
    asyncio.run(run_tool_eval())
