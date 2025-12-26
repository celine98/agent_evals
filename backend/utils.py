"""
Utility functions for agent evaluation.
"""
from typing import List

from agents import OpenAIConversationsSession

# Optional: types for introspection (best-effort; SDK exports may vary by version)
try:
    from agents.items import HandoffOutputItem, FunctionCallOutputItem, ToolCallItem  # type: ignore
except Exception:
    HandoffOutputItem = None  # fallback
    FunctionCallOutputItem = None  # fallback
    ToolCallItem = None  # fallback


async def get_conversation_id(session: OpenAIConversationsSession) -> str:
    """
    OpenAIConversationsSession supports resuming via conversation_id (see Sessions docs).
    SDK versions differ slightly; this tries a few ways.
    """
    # Common patterns across SDK versions:
    if hasattr(session, "_session_id") and getattr(session, "_session_id"):
        return getattr(session, "_session_id")
    
    # Otherwise, call _get_session_id() which will get/create the session ID
    return await session._get_session_id()  # type: ignore


def extract_routed_agent_name(run_result) -> str:
    """
    Detect which agent was selected by inspecting RunResult.new_items.
    HandoffOutputItem contains source/target agent info.
    """
    # Preferred: look for HandoffOutputItem in new_items
    for item in getattr(run_result, "new_items", []) or []:
        # If we can import HandoffOutputItem, use isinstance
        if HandoffOutputItem is not None:
            if isinstance(item, HandoffOutputItem):
                # The SDK exposes source/target agents on the item.
                target = getattr(item, "target_agent", None)
                if target is not None:
                    return getattr(target, "name", "Unknown")
                # fallback
                return "Unknown"

        # Best-effort fallback: check attributes that look like a handoff item
        if hasattr(item, "target_agent"):
            target = getattr(item, "target_agent")
            return getattr(target, "name", "Unknown")

    # If no handoff, the last_agent is the one that answered.
    last_agent = getattr(run_result, "last_agent", None)
    return getattr(last_agent, "name", "Unknown")


def extract_tool_calls(run_result) -> List[str]:
    """
    Extract the names of tools that were called during the run.
    
    Returns:
        List of tool names that were called (e.g., ["transfer_funds", "pay_bill"])
    """
    tool_calls = []
    seen_tools = set()  # Track to avoid duplicates
    
    # Check new_items for tool calls
    for item in getattr(run_result, "new_items", []) or []:
        tool_name = None
        
        # First, check for ToolCallItem (new format with raw_item)
        if ToolCallItem is not None:
            if isinstance(item, ToolCallItem):
                raw_item = getattr(item, "raw_item", None)
                if raw_item:
                    tool_name = getattr(raw_item, "name", None)
        
        # Fallback: check for type attribute indicating tool_call_item
        if not tool_name:
            item_type = getattr(item, "type", None)
            if item_type == "tool_call_item":
                raw_item = getattr(item, "raw_item", None)
                if raw_item:
                    tool_name = getattr(raw_item, "name", None)
        
        # Preferred: use FunctionCallOutputItem if available
        if not tool_name and FunctionCallOutputItem is not None:
            if isinstance(item, FunctionCallOutputItem):
                # The SDK exposes function/tool info on the item
                tool_name = getattr(item, "function_name", None) or getattr(item, "name", None)
        
        # Fallback: check for function_call or tool_call attributes
        if not tool_name and (hasattr(item, "function_call") or hasattr(item, "tool_call")):
            func_call = getattr(item, "function_call", None) or getattr(item, "tool_call", None)
            if func_call:
                tool_name = getattr(func_call, "name", None)
        
        # Alternative: check for function_name directly on the item
        if not tool_name and hasattr(item, "function_name"):
            tool_name = getattr(item, "function_name")
        
        # Last resort: check for name attribute on callable items
        if not tool_name and hasattr(item, "name") and not hasattr(item, "target_agent"):
            # Avoid picking up handoff items
            tool_name = getattr(item, "name", None)
        
        if tool_name and tool_name not in seen_tools:
            tool_calls.append(tool_name)
            seen_tools.add(tool_name)
    
    # Also check all_items if available (for completeness)
    for item in getattr(run_result, "all_items", []) or []:
        tool_name = None
        
        # First, check for ToolCallItem (new format with raw_item)
        if ToolCallItem is not None:
            if isinstance(item, ToolCallItem):
                raw_item = getattr(item, "raw_item", None)
                if raw_item:
                    tool_name = getattr(raw_item, "name", None)
        
        # Fallback: check for type attribute indicating tool_call_item
        if not tool_name:
            item_type = getattr(item, "type", None)
            if item_type == "tool_call_item":
                raw_item = getattr(item, "raw_item", None)
                if raw_item:
                    tool_name = getattr(raw_item, "name", None)
        
        if not tool_name and FunctionCallOutputItem is not None:
            if isinstance(item, FunctionCallOutputItem):
                tool_name = getattr(item, "function_name", None) or getattr(item, "name", None)
        
        if not tool_name and (hasattr(item, "function_call") or hasattr(item, "tool_call")):
            func_call = getattr(item, "function_call", None) or getattr(item, "tool_call", None)
            if func_call:
                tool_name = getattr(func_call, "name", None)
        
        if not tool_name and hasattr(item, "function_name"):
            tool_name = getattr(item, "function_name")
        
        if tool_name and tool_name not in seen_tools:
            tool_calls.append(tool_name)
            seen_tools.add(tool_name)
    
    return tool_calls

