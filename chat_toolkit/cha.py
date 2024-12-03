from typing import Dict, List, Optional

class Utterance:
    def __init__(self, line: str):
        parts = line.split('\t', 1)
        self.speaker = parts[0].strip('*:')
        self.content = parts[1] if len(parts) > 1 else ""
        self.dependent_tiers: Dict[str, str] = {}

    def add_dependent_tier(self, line: str):
        parts = line.split(':', 1)
        if len(parts) == 2:
            tier_type, content = parts[0].strip('%'), parts[1].strip()
            self.dependent_tiers[tier_type] = content

class CHATFile:
    def __init__(self, filename: str):
        self.filename = filename
        self.headers: Dict[str, str] = {}
        self.participants: Dict[str, Dict[str, str]] = {}
        self.utterances: List[Utterance] = []

    def add_header(self, key: str, value: str):
        self.headers[key] = value

    def add_participant(self, code: str, name: str, role: str):
        self.participants[code] = {'name': name, 'role': role}

    def add_utterance(self, utterance: Utterance):
        self.utterances.append(utterance)