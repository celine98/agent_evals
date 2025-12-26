"""
Handoff evaluation: Store multi-agent conversations in OpenAI-hosted Sessions (Conversations API)
and evaluate whether the orchestrator handed off to the correct specialist.

Prereqs:
  pip install openai-agents
  export OPENAI_API_KEY="..."

Docs:
  Sessions (incl. OpenAIConversationsSession): https://openai.github.io/openai-agents-python/sessions/
  Results / HandoffOutputItem: https://openai.github.io/openai-agents-python/results/
"""
import asyncio
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from agents import Runner, OpenAIConversationsSession

from .agent_list import build_agents
from data.dataset import ROUTING_DATASET
from .utils import get_conversation_id, extract_routed_agent_name


def save_results_to_csv(results: List[Dict[str, Any]], output_dir: Optional[Path] = None) -> str:
    """
    Save handoff evaluation results to a CSV file.
    
    Args:
        results: List of result dictionaries with 'message', 'target', and 'output' keys
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
    filename = f"handoff_evals_{timestamp}.csv"
    filepath = output_dir / filename
    
    # Write CSV file
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['message', 'target', 'output']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow({
                'message': result.get('message', ''),
                'target': result.get('target', ''),
                'output': result.get('output', ''),
            })
    
    return str(filepath)


async def run_handoff_eval(model: str = "gpt-4.1-mini", verbose: bool = True) -> Dict[str, Any]:
    """
    Run the handoff evaluation.
    
    Returns:
        Dict with 'accuracy', 'correct', 'total', and 'results' (list of test cases)
    """
    orchestrator, _, _, _ = build_agents(model=model)

    # Phase 1: run dataset prompts, store each in OpenAI-hosted session
    stored_runs: List[Dict[str, Any]] = []

    if verbose:
        print("\n=== Phase 1: Generate conversations and store in OpenAI-hosted Sessions ===")
    for case in ROUTING_DATASET:
        session = OpenAIConversationsSession()  # OpenAI-hosted storage

        result = await Runner.run(
            orchestrator,
            case.prompt,
            session=session,
        )

        routed_to = extract_routed_agent_name(result)
        conv_id = await get_conversation_id(session)

        stored_runs.append(
            {
                "case_id": case.case_id,
                "expected": case.expected_agent,
                "actual": routed_to,
                "conversation_id": conv_id,
                "final_output": result.final_output,
            }
        )

        if verbose:
            print(f"- {case.case_id}: expected={case.expected_agent:11s} actual={routed_to:11s} conv_id={conv_id}")

    # Phase 2: reload sessions and run evaluation
    if verbose:
        print("\n=== Phase 2: Reload sessions and evaluate routing accuracy ===")
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
            "message": next((c.prompt for c in ROUTING_DATASET if c.case_id == row["case_id"]), ""),
            "target": row["expected"],
            "output": row["actual"],
            "correct": is_correct,
        })

        if verbose:
            status = "✅" if is_correct else "❌"
            print(
                f"{status} {row['case_id']} | expected={row['expected']}, actual={row['actual']} | "
                f"reloaded_items={n_items}"
            )

    total = len(stored_runs)
    acc = correct / total if total else 0.0
    
    # Save results to CSV
    csv_path = save_results_to_csv(results)
    if verbose:
        print(f"\nResults saved to: {csv_path}")
    
    if verbose:
        print(f"\nAccuracy: {correct}/{total} = {acc:.2%}")
        print("\nDone.")
        print("Tip: Open Traces to visualize handoffs and debug misroutes (Tracing is enabled by default).")
    
    return {
        "accuracy": acc,
        "correct": correct,
        "total": total,
        "results": results,
        "csv_path": csv_path,
    }


if __name__ == "__main__":
    asyncio.run(run_handoff_eval())

