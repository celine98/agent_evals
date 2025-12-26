"""
Dataset for routing evaluation and tool call evaluation.
"""
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class RoutingCase:
    case_id: str
    prompt: str
    expected_agent: str  # "Operational", "Informational", or "FinancialCoach"


@dataclass(frozen=True)
class ToolCallCase:
    case_id: str
    prompt: str
    expected_tool: str  # "transfer_funds", "pay_bill", or "update_account_info"


def _get_dataset_dir() -> Path:
    """Get the directory where dataset CSV files are located."""
    return Path(__file__).parent


def _load_routing_dataset(csv_path: Path) -> List[RoutingCase]:
    """Load routing dataset from CSV file."""
    cases = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cases.append(
                RoutingCase(
                    case_id=row["case_id"],
                    prompt=row["prompt"],
                    expected_agent=row["expected_agent"],
                )
            )
    return cases


def _load_tool_call_dataset(csv_path: Path) -> List[ToolCallCase]:
    """Load tool call dataset from CSV file."""
    cases = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cases.append(
                ToolCallCase(
                    case_id=row["case_id"],
                    prompt=row["prompt"],
                    expected_tool=row["expected_tool"],
                )
            )
    return cases


# Load datasets from CSV files
_dataset_dir = _get_dataset_dir()
ROUTING_DATASET: List[RoutingCase] = _load_routing_dataset(
    _dataset_dir / "routing_dataset.csv"
)
TOOL_CALL_DATASET: List[ToolCallCase] = _load_tool_call_dataset(
    _dataset_dir / "tool_call_dataset.csv"
)

