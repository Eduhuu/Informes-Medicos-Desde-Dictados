from shared.constants.AsrConstants import INITIAL_PROMPT_WORD_SEPARATOR


def build_initial_prompt(prompt_words: list[str] | tuple[str, ...]) -> str | None:
    """Join configured prompt terms into a single initial_prompt string for Whisper."""
    normalized = [
        word.strip()
        for word in prompt_words
        if word is not None and str(word).strip()
    ]
    if not normalized:
        return None
    return INITIAL_PROMPT_WORD_SEPARATOR.join(normalized)
