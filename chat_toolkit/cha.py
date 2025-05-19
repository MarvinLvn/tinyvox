from typing import Dict, List, Optional

class AbstractUtterance:
    def __init__(self, speaker: str, content: str):
        self.speaker = speaker
        self.content = content
        self.dependent_tiers = {}

    def add_dependent_tier(self, tier_type, content):
        self.dependent_tiers[tier_type] = content

class MissingTimestampsUtterance(AbstractUtterance):
   pass  # Inherits all functionality from parent

class Utterance(AbstractUtterance):
    def __init__(self, speaker:str, content: str, onset: int, offset: int):
        super().__init__(speaker, content)
        self.onset = onset
        self.offset = offset

class CHATFile:
    def __init__(self, filename: str):
        self.filename = filename
        self.headers: Dict[str, str] = {}
        self.participants: Dict[str, Dict[str, str]] = {}
        self.utterances: List[Utterance] = []
        self._languages: List[str] = []
        self.design: str = None
        self.activity: str = None
        self.group: str = None
        self.missing_timestamps = 0
        self.is_automatic = False
        self.found_tiers = set()
        self.automatic_keywords = {'LENA', 'Batchalign', 'ASR', 'This is a dummy file'}

    def add_header(self, key: str, value: str):
        if key == 'Comment' and any(keyword in value for keyword in self.automatic_keywords):
            self.is_automatic = True
        self.headers[key] = value

    def add_participant(self, code: str, name: str, role: str):
        if role == '':
            role = name
            name = ''
        if code not in self.participants:
            self.participants[code] = {}
        self.participants[code].update({'name': name, 'role': role})

    def set_types(self, design, activity, group):
        self.design = design
        self.activity = activity
        self.group = group

    def set_languages(self, languages):
        self._languages = languages

    def add_utterance(self, utterance: Utterance):
        if type(utterance) is MissingTimestampsUtterance:
            self.missing_timestamps += 1
        self.utterances.append(utterance)

    def __len__(self):
        return len(self.utterances)

    @property
    def languages(self) -> List[str]:
        return self._languages

    def get_primary_language(self) -> Optional[str]:
        return self.languages[0] if self.languages else None

    def get_participant_info(self, code: str) -> Optional[Dict[str, str]]:
        return self.participants.get(code)

    def print_content(self, with_dependent_tiers=False):
        for utt in self.utterances:
            print(utt.content, utt.onset, utt.offset)
            if with_dependent_tiers:
                for tier_type, content in utt.dependent_tiers:
                    print(tier_type, content)

    def print_header(self, key='all'):
        assert key in ['all', 'participants', 'languages', 'types', 'unused']
        if key == 'participants' or key == 'all':
            print('Participants:')
            for code, participant_dict in self.participants.items():
                info_keys = participant_dict.keys()
                participant_string = f'\t{code}: '
                for i, info_key in enumerate(info_keys):
                    if participant_dict[info_key] != '':
                        participant_string += participant_dict[info_key] + ', '
                participant_string = ", ".join(participant_string.rsplit(", ", 1)[0:-1])
                print(participant_string)

        if key == 'languages' or key == 'all':
            print('Languages:', end=' ')
            n_languages = len(self.languages)
            for i, lang in enumerate(self.languages):
                if i < n_languages - 1:
                    print(lang, end=', ')
                else:
                    print(lang)

        if key == 'types' or key == 'all':
            print(f"Types: {self.design}, {self.activity}, {self.group}")

        if key == 'unused' or key == 'all':
            print("Unused information:")
            for key, value in self.headers.items():
                if key not in ['Begin', 'End']:
                    print(f'\t{key}: {value}')

    def write(self, output_path: str, dependent_tier=True):
        """Write CHATFile content to a .cha file."""
        UNIT_MARKER = '\x15'  # ASCII control character for ^U
        TAB = '\t'  # ASCII tab for ^I
        CR = '\r'  # ASCII carriage return for $
        NL = '\n'  # ASCII newline

        with open(output_path, 'wb') as f:  # Open in binary mode to handle control chars
            if 'PID' in self.headers:
                f.write(f"@PID:{TAB}{self.headers['PID']}{CR}{NL}".encode('utf-8'))
            f.write(f"@Begin{CR}{NL}".encode('utf-8'))

            # Write Languages
            if self._languages:
                f.write(f"@Languages:{TAB}{', '.join(self._languages)}{CR}{NL}".encode('utf-8'))

            # Write Participants
            parts = []
            for code, info in self.participants.items():
                name = info['name'] if info['name'] else code
                role = info['role']
                parts.append(f"{code} {name} {role}")
            f.write(f"@Participants:{TAB}{', '.join(parts)}{CR}{NL}".encode('utf-8'))

            # Write Options
            if 'Options' in self.headers:
                f.write(f"@Options:{TAB}{self.headers['Options']}{CR}{NL}".encode('utf-8'))

            # Write IDs
            for code, info in self.participants.items():
                id_line = (
                    f"@ID:{TAB}{info.get('language', self.get_primary_language())}|"
                    f"{info.get('corpus', '')}|{code}|{info.get('age', '')}|"
                    f"{info.get('gender', '')}|{info.get('group', '')}|{info.get('ses', '')}|"
                    f"{info['role']}|{info.get('education', '')}|{info.get('custom', '')}|{CR}{NL}"
                )
                f.write(id_line.encode('utf-8'))

            # Write other headers
            for key in ['Media', 'Transcriber', 'Date']:
                if key in self.headers:
                    f.write(f"@{key}:{TAB}{self.headers[key]}{CR}{NL}".encode('utf-8'))

            # Write Types
            if any([self.design, self.activity, self.group]):
                types = [t for t in [self.design, self.activity, self.group] if t]
                f.write(f"@Types:{TAB}{', '.join(types)}{CR}{NL}".encode('utf-8'))

            f.write(f"{CR}{NL}".encode('utf-8'))

            # Write utterances with proper control characters
            for utt in self.utterances:
                if isinstance(utt, Utterance):
                    # Use actual control characters for tab, unit marker, and line ending
                    f.write(
                        f"*{utt.speaker}:{TAB}{utt.content} {UNIT_MARKER}{int(utt.onset)}_{int(utt.offset)}{UNIT_MARKER}{CR}{NL}".encode(
                            'utf-8'))
                else:
                    f.write(f"*{utt.speaker}:{TAB}{utt.content}{CR}{NL}".encode('utf-8'))

                # Write dependent tiers with proper control characters
                if dependent_tier:
                    for tier_type, content in utt.dependent_tiers.items():
                        f.write(f"%{tier_type}:{TAB}{content}{CR}{NL}".encode('utf-8'))

            f.write(f"@End{CR}{NL}".encode('utf-8'))