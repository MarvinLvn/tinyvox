import re
from typing import Dict, List

def extract_time_marks(content: str) -> List[Dict[str, int]]:
    pattern = r'·(\d+)_(\d+)·'
    matches = re.findall(pattern, content)
    return [{'start': int(start), 'end': int(end)} for start, end in matches]

def remove_time_marks(content: str) -> str:
    return re.sub(r'·\d+_\d+·', '', content)

def parse_special_form(word: str) -> Dict[str, str]:
    parts = word.split('@')
    if len(parts) == 2:
        return {'word': parts[0], 'marker': parts[1]}
    return {'word': word, 'marker': ''}

def is_utterance_terminator(char: str) -> bool:
    return char in '.?!'