from typing import Optional
from .cha import CHATFile, Utterance


def parse_chat_file(filename: str) -> Optional[CHATFile]:
    try:
        chat_file = CHATFile(filename)

        with open(filename, 'r', encoding='utf-8') as file:
            current_utterance = None
            for line in file:
                line = line.strip()
                if not line:
                    continue

                if line.startswith('@'):
                    _parse_header(chat_file, line)
                elif line.startswith('*'):
                    if current_utterance:
                        chat_file.add_utterance(current_utterance)
                    current_utterance = Utterance(line)
                elif line.startswith('%'):
                    if current_utterance:
                        current_utterance.add_dependent_tier(line)
                else:
                    # Continuation of previous line
                    if current_utterance:
                        current_utterance.content += " " + line

            if current_utterance:
                chat_file.add_utterance(current_utterance)

        return chat_file
    except Exception as e:
        print(f"Error parsing file {filename}: {str(e)}")
        return None


def _parse_header(chat_file: CHATFile, line: str):
    parts = line.split(':', 1)
    if len(parts) == 2:
        key, value = parts[0].strip('@'), parts[1].strip()
        if key == 'Participants':
            _parse_participants(chat_file, value)
        else:
            chat_file.add_header(key, value)


def _parse_participants(chat_file: CHATFile, value: str):
    parts = value.split(',')
    for part in parts:
        participant_info = part.strip().split()
        if len(participant_info) >= 3:
            code, name, role = participant_info[0], participant_info[1], ' '.join(participant_info[2:])
            chat_file.add_participant(code, name, role)