import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_results_dir() -> Path:
    agent_evals_root = Path(__file__).parent.parent
    return agent_evals_root / "results"


def get_history_path() -> Path:
    return get_results_dir() / "history.json"


def load_history() -> List[Dict[str, Any]]:
    history_path = get_history_path()
    if not history_path.exists():
        return []
    with history_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def append_history(entry: Dict[str, Any]) -> None:
    history = load_history()
    history.append(entry)
    history_path = get_history_path()
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("w", encoding="utf-8") as file:
        json.dump(history, file, indent=2)


def get_git_commit_hash() -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def build_run_metadata(model: str, dataset: str, eval_type: str) -> Dict[str, Any]:
    timestamp = datetime.now().isoformat()
    return {
        "run_id": f"{eval_type}_{timestamp}",
        "timestamp": timestamp,
        "model": model,
        "dataset": dataset,
        "eval_type": eval_type,
        "git_commit": get_git_commit_hash(),
    }
