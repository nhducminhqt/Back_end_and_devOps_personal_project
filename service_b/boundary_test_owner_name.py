import re
from fastapi.responses import JSONResponse
import EXCEPTION_MESSAGE as msg

def boundary_test_owner_name(owner_name: str, min_length: int = 1, max_length: int = 50) -> JSONResponse:
    # Sanitize owner_name (remove leading/trailing spaces)
    owner_name = owner_name.strip()  # Loại bỏ khoảng trắng thừa đầu và cuối
    
    # Boundary check for owner_name length
    if len(owner_name) < min_length or len(owner_name) > max_length:
        error_message = msg.OWNER_NAME_LENGTH_ERROR.format(min_length=min_length, max_length=max_length)
        return JSONResponse(content={"message": error_message}, status_code=400)
    
    # Check if owner_name contains valid characters (letters, numbers, and spaces)
    if not re.match(r'^[a-zA-Z0-9 ]+$', owner_name):
        return JSONResponse(content={"message": msg.OWNER_NAME_CHAR_ERROR}, status_code=400)
    
    return None  # Return None if everything is fine
