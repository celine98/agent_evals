"""
Tools (functions) available to the operational agent for banking operations.
"""
from typing import Dict, Any
from agents import function_tool


@function_tool
def transfer_funds(amount: float, from_account: str, to_account: str) -> Dict[str, Any]:
    """
    Transfer funds from one account to another.
    
    Args:
        amount: The amount to transfer
        from_account: Source account identifier
        to_account: Destination account identifier
    
    Returns:
        Dictionary with transfer confirmation details
    """
    # In a real implementation, this would perform the actual transfer
    return {
        "status": "success",
        "transaction_id": f"TXN_{amount}_{from_account}_{to_account}",
        "amount": amount,
        "from_account": from_account,
        "to_account": to_account,
        "message": f"Successfully transferred ${amount:.2f} from {from_account} to {to_account}",
    }


@function_tool
def pay_bill(amount: float, payee: str, account_number: str = None) -> Dict[str, Any]:
    """
    Pay a bill to a specified payee.
    
    Args:
        amount: The amount to pay
        payee: Name or identifier of the payee
        account_number: Optional account number for the payee
    
    Returns:
        Dictionary with payment confirmation details
    """
    # In a real implementation, this would process the bill payment
    return {
        "status": "success",
        "payment_id": f"PAY_{amount}_{payee}",
        "amount": amount,
        "payee": payee,
        "account_number": account_number,
        "message": f"Successfully paid ${amount:.2f} to {payee}",
    }


@function_tool
def update_account_info(field: str, new_value: str) -> Dict[str, Any]:
    """
    Update account information such as address, phone number, or email.
    
    Args:
        field: The field to update (e.g., "address", "phone", "email")
        new_value: The new value for the field
    
    Returns:
        Dictionary with update confirmation details
    """
    # In a real implementation, this would update the account information
    return {
        "status": "success",
        "field": field,
        "new_value": new_value,
        "message": f"Successfully updated {field} to {new_value}",
    }

