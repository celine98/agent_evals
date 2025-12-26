"""
Agent definitions: 1 orchestrator + 3 specialists.
"""
from typing import Tuple

from agents import Agent

from .tools import transfer_funds, pay_bill, update_account_info


def build_agents(model: str = "gpt-4.1-mini") -> Tuple[Agent, Agent, Agent, Agent]:
    """
    Build the orchestrator and specialist agents for banking operations.
    
    Returns:
        Tuple of (orchestrator, operational_agent, informational_agent, financial_coach_agent)
    """
    operational_agent = Agent(
        name="Operational",
        model=model,
        instructions=(
            "You are the Banking Operations Specialist.\n"
            "You handle: transfers between accounts, bill payments, account updates (address, phone, email),\n"
            "setting up automatic transfers, ordering checks, card replacements, account maintenance tasks,\n"
            "and executing specific banking transactions.\n"
            "Use the available tools to perform operations when the user requests them.\n"
            "If the user is asking general questions about banking services or seeking financial advice, hand off back to the Orchestrator."
        ),
        tools=[transfer_funds, pay_bill, update_account_info],
    )

    informational_agent = Agent(
        name="Informational",
        model=model,
        instructions=(
            "You are the Banking Information Specialist.\n"
            "You handle: branch hours, account types and features, product information, application processes,\n"
            "service descriptions, fees and rates, online banking capabilities, and answering general banking questions.\n"
            "If the user wants to perform a transaction or needs financial coaching/advice, hand off back to the Orchestrator."
        ),
    )

    financial_coach_agent = Agent(
        name="FinancialCoach",
        model=model,
        instructions=(
            "You are the Financial Coach Specialist.\n"
            "You handle: budgeting advice, saving strategies, debt payoff plans, retirement planning,\n"
            "investment guidance, financial goal setting, money management tips, and providing personalized financial coaching.\n"
            "If the user wants to perform a banking operation or ask about banking services/products, hand off back to the Orchestrator."
        ),
    )

    orchestrator = Agent(
        name="Orchestrator",
        model=model,
        instructions=(
            "You are the Orchestrator. Your ONLY job is to route the user to the correct specialist via handoff.\n"
            "Rules:\n"
            "- If the request is to perform a banking operation (transfer, payment, account update, set up automation) → handoff to Operational.\n"
            "- If the request is asking about banking services, products, hours, processes, or general information → handoff to Informational.\n"
            "- If the request is seeking financial advice, budgeting help, saving strategies, or financial coaching → handoff to FinancialCoach.\n"
            "- Do NOT answer the user directly unless absolutely necessary; prefer handing off.\n"
            "When uncertain, ask ONE short clarifying question, then handoff."
        ),
        handoffs=[operational_agent, informational_agent, financial_coach_agent],
    )

    return orchestrator, operational_agent, informational_agent, financial_coach_agent

