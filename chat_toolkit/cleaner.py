import re
from typing import List, Pattern

class TextCleaner:
    def clean(self, text: str) -> str:
        pass

class NumberPrefixCleaner(TextCleaner):
    def clean(self, text: str) -> str:
        """
        Removes '0' prefixes from words (e.g., '0word' -> 'word')
        """
        # Find and remove only '0' prefixes before words
        text = re.sub(r'0(\w+)', r'\1', text)
        return text

class FillerCleaner(TextCleaner):
    def clean(self, text: str) -> str:
        # Remove action markers (&=)
        text = re.sub(r'&=[^ ]*', '', text)
        # Remove filled pauses (&-)
        text = re.sub(r'&-[^ ]*', '', text)
        # Remove fragments (&+)
        text = re.sub(r'&\+[^ ]*', '', text)
        # Remove nonwords (&~)
        text = re.sub(r'&~[^ ]*', '', text)
        # Remove special form markers (@k, @p, @o etc)
        text = re.sub(r'@[a-z]', '', text)
        return text

class TextNormalizer(TextCleaner):
    def clean(self, text: str) -> str:
        # Handle multi-word underscored terms - improved pattern
        while re.search(r'\w+_\w+', text):
            text = re.sub(r'(\w+)_(\w+)',
                         lambda m: f"{m.group(1).lower()} {m.group(2).lower()}",
                         text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()



class SpecialCharactersCleaner(TextCleaner):
    def clean(self, text: str) -> str:
        # Remove timestamps with control characters
        text = re.sub(r'\.[^\s]*\d+_\d+[^\s]*', '', text)

        # Remove CHAT special characters
        text = re.sub(r'[„‡↑↓→↗↘⇗⇘∬≠↑≋≡∙⌈⌉⌊⌋∆∇◉▁▔☺♋Ϋ∲§∾↻]', '', text)

        # Remove stutter marks
        text = re.sub(r'↫\w+↫', '', text)

        # Remove any remaining control characters
        text = re.sub(r'\^[A-Z]', '', text)

        return text



class LineMarkerCleaner(TextCleaner):
    def clean(self, text: str) -> str:
        # Handle trailing off markers first
        text = re.sub(r'\+\.\.\?', '?', text)  # Question trailing off
        text = re.sub(r'\+…', '...', text)  # Unicode ellipsis
        text = re.sub(r'\+\.{3}', '...', text)  # Regular trailing off

        # Then other line markers
        text = re.sub(r'^\+<\s*', '', text)  # overlap
        text = re.sub(r'^\+,\s*', '', text)  # continuation
        text = re.sub(r'\+/[\.\?]', '.', text)  # interruption
        text = re.sub(r'\+//?', '', text)
        return text


class MarkupCleaner(TextCleaner):
    def clean(self, text: str) -> str:
        # Remove uncertainty markers and surrounding spaces
        text = re.sub(r'\s*\[\?\]\s*', ' ', text)

        # Remove repetition markers (but keep words)
        text = re.sub(r'\s*\[/+\]\s*', ' ', text)

        # Remove replacements (keep original word)
        text = re.sub(r'(\S+)\s*\[:[^\]]+\]', r'\1', text)

        # Remove other markup
        text = re.sub(r'\s*\[=\s*![^\]]*\]', '', text)  # exclamations
        text = re.sub(r'\s*\[\+\s*[^\]]+\]', '', text)  # postcodes
        text = re.sub(r'\s*\[[<>]\]', '', text)  # overlap

        # Remove any remaining content in square brackets
        text = re.sub(r'\s*\[[^\]]*\]', '', text)

        # Remove angle brackets
        text = re.sub(r'[<>]', '', text)

        # Normalize spaces
        text = re.sub(r'\s+', ' ', text)

        return text.strip()


class FragmentCleaner(TextCleaner):
    def clean(self, text: str) -> str:
        # Handle fragments anywhere in the word - iterative approach
        while re.search(r'\w*\(\w+\)\w*', text):
            text = re.sub(r'(\w*)\((\w+)\)(\w*)', r'\1\2\3', text)
        return text


class PauseMarkerCleaner(TextCleaner):
    def clean(self, text: str) -> str:
        # Remove pauses with surrounding spaces
        text = re.sub(r'\s*\(\.*\)\s*', ' ', text)
        text = re.sub(r'\s*\(\d*\.?\d*\)\s*', ' ', text)
        return text.strip()


class ChatCleaner:
    def __init__(self):
        self.cleaners = [
            LineMarkerCleaner(),  # Handle line markers first
            MarkupCleaner(),  # Then markup (including repetitions)
            PauseMarkerCleaner(),  # Then pauses
            FragmentCleaner(),  # Then word fragments
            SpecialCharactersCleaner(),  # Then special chars
            FillerCleaner(),  # Then fillers
            NumberPrefixCleaner(), # 0word --> word
            TextNormalizer()  # Finally normalize
        ]

    def clean(self, text: str) -> str:
        for cleaner in self.cleaners:
            text = cleaner.clean(text)
        return text