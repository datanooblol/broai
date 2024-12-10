import re

def remove_escape_characters(text:str)->str:
    pattern = r'["]'
    return re.sub(pattern, "'", text)