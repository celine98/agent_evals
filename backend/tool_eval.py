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
from typing import List, Dict, Any

from agents import Runner, OpenAIConversationsSession

from .agent_list import build_agents
from data.dataset import TOOL_CALL_DATASET
from .utils import get_conversation_id, extract_tool_calls


async def run_tool_eval(model: str = "gpt-4.1-mini", verbose: bool = True) -> Dict[str, Any]:
    """
    Run the tool call evaluation.
    
    Returns:
        Dict with 'accuracy', 'correct', 'total', and 'results' (list of test cases)
    """
    # Get the operational agent directly (we'll use it without the orchestrator)
    _, operational_agent, _, _ = build_agents(model=model)

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
    
    if verbose:
        print(f"\nAccuracy: {correct}/{total} = {acc:.2%}")
        print("\nDone.")
        print("Tip: Open Traces to visualize tool calls and debug incorrect tool selections (Tracing is enabled by default).")
    
    return {
        "accuracy": acc,
        "correct": correct,
        "total": total,
        "results": results,
    }


if __name__ == "__main__":
    asyncio.run(run_tool_eval())

