
from typing import Optional


def validate_int(
        value: str,
        lower_bound: Optional[int] = None,
        upper_bound: Optional[int] = None,
    ):
    """
    Validates that a string contains an integer
    
    Validates that a string variable can be converted to an integer and is within the given bounds
    
    Args:
        lower_bound: Minimum integer value to allow(Inclusive)
        upper_bound: Maximum integer value to allow(Inclusive)

    Returns:
        True if the value can be converted to integer between the bounds False otherwise
    """
    value = value.strip()
    try:
        value_as_int = int(value)
        if lower_bound and lower_bound > value_as_int:
            return False
        if upper_bound and upper_bound < value_as_int:
            return False
        return True
    except Exception:
        return False

def validate_int_format(
        value: str,
        lower_bound: Optional[int] = None,
        upper_bound: Optional[int] = None
    ):
    """
    Validates that a string contains an integer or formatting to enter an integer
    
    Validates that a string variable can be converted to integer between the given bounds.
        Validates that the string contains only whitespace or a negative symbol if the conversion isn't possible
    
    Args:
        lower_bound: Minimum integer value to allow(Inclusive)
        upper_bound: Maximum integer value to allow(Inclusive)

    Returns:
        True if the value is within an integer format and between the bounds
    """
    value = value.strip()
    return value == "" or value == "-" or validate_int(value, lower_bound, upper_bound)

def validate_float(
        value: str,
        lower_bound: Optional[float] = None,
        upper_bound: Optional[float] = None
    ):
    """
    Validates that a string contains an float
    
    Validates that a string variable can be converted to an float and is within the given bounds
    
    Args:
        lower_bound: Minimum float value to allow(Inclusive)
        upper_bound: Maximum float value to allow(Inclusive)

    Returns:
        True if the value can be converted to float between the bounds False otherwise
    """
    value = value.strip()
    try :
        value_as_float = float(value)
        if lower_bound and lower_bound > value_as_float:
            return False
        if upper_bound and upper_bound < value_as_float:
            return False
        return True
    except Exception:
        return False

def validate_float_format(
        value: str,
        lower_bound: Optional[float]=None,
        upper_bound: Optional[float]=None
    ):
    """
    Validates that a string contains an float or formatting to enter an float
    
    Validates that a string variable can be converted to float between the given bounds.
        Validates that the string contains only whitespace or a combination of '.' and '-' symbols
    
    Args:
        lower_bound: Minimum float value to allow(Inclusive)
        upper_bound: Maximum float value to allow(Inclusive)

    Returns:
        True if the value is within an integer format and between the bounds
    """
    value = value.strip()
    return value == "" or value == "-" or value == "." or value == "-." or validate_float(value, lower_bound, upper_bound)