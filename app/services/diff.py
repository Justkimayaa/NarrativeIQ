import difflib
from typing import List


def compute_diff(original: str, enhanced: str) -> List[dict]:
    """
    Computes a word-level diff between original and enhanced text.
    Returns a list of {type, content} objects the frontend uses
    to highlight changes in red/green.

    type: "added" | "removed" | "unchanged"
    """
    original_words = original.split()
    enhanced_words = enhanced.split()

    matcher = difflib.SequenceMatcher(None, original_words, enhanced_words, autojunk=False)
    result = []

    for opcode, i1, i2, j1, j2 in matcher.get_opcodes():
        if opcode == "equal":
            result.append({
                "type": "unchanged",
                "content": " ".join(original_words[i1:i2]),
            })
        elif opcode == "replace":
            result.append({
                "type": "removed",
                "content": " ".join(original_words[i1:i2]),
            })
            result.append({
                "type": "added",
                "content": " ".join(enhanced_words[j1:j2]),
            })
        elif opcode == "delete":
            result.append({
                "type": "removed",
                "content": " ".join(original_words[i1:i2]),
            })
        elif opcode == "insert":
            result.append({
                "type": "added",
                "content": " ".join(enhanced_words[j1:j2]),
            })

    return result