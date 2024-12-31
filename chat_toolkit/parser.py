from enum import Enum
from typing import Optional, List, Tuple, Dict, Any
from pathlib import Path
import re
from chat_toolkit.cha import CHATFile, Utterance, MissingTimestampsUtterance


class LineType(Enum):
    HEADER = "HEADER"
    UTTERANCE = "UTTERANCE"
    DEPENDENT_TIER = "DEPENDENT_TIER"
    CONTINUATION = "CONTINUATION"
    EMPTY = "EMPTY"


class CHATParseError(Exception):
    pass


class CHATParser:
    REQUIRED_HEADERS = {'Begin', 'Languages', 'Participants', 'End'}

    def __init__(self, filename: str):
        self.filename = filename
        self.chat_file = CHATFile(filename)
        self.current_utterance = None
        self.current_tier_type = None
        self.pending_header = None
        self.found_headers = set()
        self.line_number = 0

    def _get_line_type(self, line: str) -> LineType:
        """Determine the type of a line in the CHAT file."""
        if not line.strip():
            return LineType.EMPTY
        if line.startswith('@'):
            return LineType.HEADER
        if line.startswith('*'):
            return LineType.UTTERANCE
        if line.startswith('%'):
            return LineType.DEPENDENT_TIER
        return LineType.CONTINUATION

    def parse(self) -> CHATFile:
        """Parse the CHAT file and return a CHATFile object."""
        if not Path(self.filename).exists():
            raise CHATParseError(f"File not found: {self.filename}")

        try:
            for line_number, line in enumerate(self._read_lines(), 1):
                self.line_number = line_number
                self._process_line(line)

            # Handle any remaining content
            if self.pending_header:
                self._parse_header(self.pending_header)
            if self.current_utterance:
                self.chat_file.add_utterance(self.current_utterance)

            self._validate_parse()
            return self.chat_file

        except Exception as e:
            raise CHATParseError(f"Error at line {self.line_number}: {str(e)}")

    def _read_lines(self) -> List[str]:
        """Read file with multiple encoding attempts."""
        for encoding in ['utf-8', 'utf-16', 'latin-1']:
            try:
                with open(self.filename, 'r', encoding=encoding) as f:
                    return [line.rstrip('\n') for line in f]
            except UnicodeDecodeError:
                continue
        raise CHATParseError("Failed to decode file")

    def _process_line(self, line: str) -> None:
        """Process a single line based on its type."""
        line_type = self._get_line_type(line)

        handlers = {
            LineType.EMPTY: lambda x: None,
            LineType.HEADER: self._handle_header_line,
            LineType.UTTERANCE: self._handle_utterance_line,
            LineType.DEPENDENT_TIER: self._handle_dependent_tier,
            LineType.CONTINUATION: self._handle_continuation
        }

        handler = handlers.get(line_type)
        if handler:
            handler(line)

    def _handle_header_line(self, line: str) -> None:
        """Handle a header line."""
        if not re.match(r'@[A-Za-z][A-Za-z0-9_\-]*:?\t?.*$', line):
            raise CHATParseError(f"Invalid header format: {line}")

        header = line[1:].split(':')[0].strip()
        if header in self.REQUIRED_HEADERS:
            self.found_headers.add(header)

        if self.pending_header:
            self._parse_header(self.pending_header)

        if not line.startswith(('@*', '@%')):
            self.pending_header = line
        else:
            self._parse_header(line)

    def _handle_utterance_line(self, line: str) -> None:
        """Handle an utterance line."""
        if not self.found_headers & {'Begin', 'Participants'}:
            raise CHATParseError("Utterance found before @Begin and @Participants")

        if self.pending_header:
            self._parse_header(self.pending_header)
            self.pending_header = None

        if self.current_utterance:
            self.chat_file.add_utterance(self.current_utterance)

        self.current_utterance = self._parse_utterance(line)
        self.current_tier_type = None

    def _handle_dependent_tier(self, line: str) -> None:
        """Handle a dependent tier line."""
        if not self.current_utterance:
            raise CHATParseError("Dependent tier found without preceding utterance")

        tier_type, content = self._parse_dependent_tier(line)
        self.current_tier_type = tier_type
        self.current_utterance.add_dependent_tier(tier_type, content)

    def _handle_continuation(self, line: str) -> None:
        """Handle continuation lines for both utterances and dependent tiers."""
        if self.current_tier_type and self.current_utterance:
            # Continue dependent tier
            content = line.strip()
            current = self.current_utterance.dependent_tiers.get(self.current_tier_type, '')
            self.current_utterance.dependent_tiers[self.current_tier_type] = f"{current} {content}".strip()
        elif self.current_utterance:
            # Check for timestamps in continuation
            timestamp_match = re.search(r'\x15(\d+)_(\d+)\x15', line)
            if timestamp_match:
                onset, offset = map(int, timestamp_match.groups())
                # Remove timestamps from continuation content
                content = re.sub(r'\s*\x15\d+_\d+\x15\s*', ' ', line).strip()

                # If current utterance is MissingTimestampsUtterance, convert it
                if isinstance(self.current_utterance, MissingTimestampsUtterance):
                    new_utterance = Utterance(
                        self.current_utterance.speaker,
                        self.current_utterance.content,
                        onset,
                        offset
                    )
                    # Copy over any dependent tiers
                    if hasattr(self.current_utterance, 'dependent_tiers'):
                        new_utterance.dependent_tiers = self.current_utterance.dependent_tiers
                    self.current_utterance = new_utterance

                # Add continuation content
                self.current_utterance.content += f" {content}"
            else:
                # No timestamps, just append content
                self.current_utterance.content += f" {line.strip()}"

        elif self.pending_header:
            # Continue header
            self.pending_header += ' ' + line.strip()
        else:
            raise CHATParseError("Continuation line without context")

    def _parse_utterance(self, line: str) -> Utterance:
        """Parse an utterance line including timestamps."""
        match = re.match(r'\*(\w+):\s*(.+)', line)
        if not match:
            raise CHATParseError(f"Invalid utterance format: {line}")

        speaker, content = match.groups()
        if speaker not in self.chat_file.participants:
            raise CHATParseError(f"Unknown speaker: {speaker}")

        # Extract timestamps if present
        timestamp_match = re.search(r'\x15(\d+)_(\d+)\x15', content)
        if timestamp_match:
            onset, offset = map(int, timestamp_match.groups())
            content = re.sub(r'\s*\x15\d+_\d+\x15', '', content).strip()
            return Utterance(speaker, content, onset, offset)
        else:
            return MissingTimestampsUtterance(speaker, content.strip())

    def _parse_dependent_tier(self, line: str) -> Tuple[str, str]:
        """Parse a dependent tier line."""
        if '%' not in line:
            raise CHATParseError("Missing % in dependent tier")

        parts = re.split(r':\s*', line.strip(), maxsplit=1)
        if len(parts) != 2:
            raise CHATParseError(f"Invalid dependent tier format: {line}")

        tier_type = parts[0].strip('%')
        content = parts[1].strip()

        return tier_type, content

    def _parse_header(self, line: str) -> None:
        """Parse a header line."""
        match = re.match(r'@([^:]+)(?::\s*(.+)|$)', line)
        if not match:
            raise CHATParseError("Invalid header format")

        key, value = match.groups()
        if key == 'End':
            return

        if key in ['Participants', 'Languages', 'ID', 'Types'] and not value:
            raise CHATParseError(f"Empty value for required header @{key}")

        header_parsers = {
            'Participants': self._parse_participants,
            'ID': self._parse_id,
            'Languages': self._parse_languages,
            'Types': self._parse_types
        }

        parser = header_parsers.get(key, lambda v: self.chat_file.add_header(key, v))
        if value:
            parser(value)

    def _parse_participants(self, value: str) -> None:
        """Parse the participants header."""
        parts = [p.strip() for p in value.split(',') if p.strip()]
        if not parts:
            raise CHATParseError("Empty participants list")

        for part in parts:
            words = part.split()
            if len(words) < 2:
                raise CHATParseError(f"Invalid participant format: {part}")

            code = words[0]
            if len(words) == 2:
                name = code
                role = words[1]
            else:
                name = words[1]
                role = ' '.join(words[2:])
            self.chat_file.add_participant(code, name, role)

    def _parse_id(self, value: str) -> None:
        """Parse an ID header."""
        parts = value.strip().split('|')
        if len(parts) < 9:
            raise CHATParseError(f"Invalid ID format: expected 9+ fields, got {len(parts)}")

        code = parts[2].strip()
        if code not in self.chat_file.participants:
            raise CHATParseError(f"ID entry for unknown participant: {code}")

        participant_info = {
            'language': parts[0].strip(),
            'corpus': parts[1].strip(),
            'age': parts[3].strip(),
            'gender': parts[4].strip(),
            'group': parts[5].strip(),
            'ses': parts[6].strip(),
            'role': parts[7].strip(),
            'education': parts[8].strip(),
            'custom': parts[9].strip() if len(parts) > 9 else ''
        }

        self.chat_file.participants[code].update(participant_info)

    def _parse_languages(self, value: str) -> None:
        """Parse the languages header."""
        languages = [lang.strip() for lang in value.split(',')]
        self.chat_file.set_languages(languages)

    def _parse_types(self, value: str) -> None:
        """Parse the types header."""
        parts = value.strip().split(', ')
        if len(parts) != 3:
            raise CHATParseError(f"Invalid Types format: expected 3 fields, got {len(parts)}")
        self.chat_file.set_types(parts[0], parts[1], parts[2])

    def _validate_parse(self) -> None:
        """Validate the parsed content."""
        missing_headers = self.REQUIRED_HEADERS - self.found_headers
        if missing_headers:
            raise CHATParseError(f"Missing required headers: {missing_headers}")
        if not self.chat_file.participants:
            raise CHATParseError("No participants found")


def parse_chat_file(filename: str) -> Optional[CHATFile]:
    """Convenience function to parse a CHAT file."""
    try:
        parser = CHATParser(filename)
        return parser.parse()
    except Exception as e:
        raise CHATParseError(f"Error parsing file: {str(e)}")