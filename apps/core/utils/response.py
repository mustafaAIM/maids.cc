from typing import Any, Dict, Optional


def create_response(
    success: bool = True,
    message: str = "",
    data: Optional[Any] = None,
    errors: Optional[Dict] = None,
    status_code: int = 200,
) -> Dict:
    """
    Create a standardized response format.
    
    Args:
        success: Boolean indicating if the request was successful
        message: A human-readable message about the response
        data: The actual response data
        errors: Any errors that occurred
        status_code: HTTP status code
        
    Returns:
        Dict containing the formatted response
    """
    response = {
        "success": success,
        "message": message,
        "status_code": status_code,
    }

    if data is not None:
        response["data"] = data
    
    if errors is not None:
        response["errors"] = errors

    return response