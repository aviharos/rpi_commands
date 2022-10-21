def decode_message(line: str):
    """Write your own implementation here. 
    
    This method will be imported into main, 
    and should decode Arduino serial messages 
    into event_ids and arguments. 

    Then the Raspberry Pi service will handle that 
    event specified in main.

    Args:
        line (str): the Arduino message sent on serial

    Returns:
        event_id: str, *args: any
    """
    return "1", None

