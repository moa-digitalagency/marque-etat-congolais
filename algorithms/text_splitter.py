"""
Text splitting algorithm for logo generation.

Splits institution names according to these rules:
1. If 2 words total: split into 2 lines (1 word per line)
2. If 3+ words: split into at least 3 lines (1 word per line for short names, up to 2 words per line)
3. Maximum 5 lines total
4. All text converted to UPPERCASE
"""


def split_unit_name(nom: str, max_lines: int = 5) -> list:
    """
    Split unit/institution name into lines for logo generation.

    Args:
        nom: Institution name (any case)
        max_lines: Maximum number of lines (default 5)

    Returns:
        List of strings, each representing one line of the logo text
        Each string is UPPERCASE

    Examples:
        >>> split_unit_name("Ministère de Santé")
        ['MINISTÈRE', 'DE SANTÉ']

        >>> split_unit_name("Ministère de l'économie numérique")
        ['MINISTÈRE', 'DE L'ÉCONOMIE', 'NUMÉRIQUE']

        >>> split_unit_name("Ambassade de la République Démocratique du Congo")
        ['AMBASSADE', 'DE LA', 'RÉPUBLIQUE', 'DÉMOCRATIQUE DU', 'CONGO']
    """
    # Validate input
    if not nom or not nom.strip():
        return []

    # Convert to uppercase and split into words
    words = nom.upper().split()
    words = [w for w in words if w]  # Remove empty strings

    if not words:
        return []

    word_count = len(words)

    # If only 1 word, return as is
    if word_count == 1:
        return words

    # If 2 words total: put 1 word per line
    if word_count == 2:
        return words[:max_lines]

    # If 3+ words: distribute across lines
    # First word on line 1, then max 2 words per subsequent line
    lines = [words[0]]
    current_line_words = []

    for word in words[1:]:
        current_line_words.append(word)

        # Commit line when we have 2 words, or on last word
        if len(current_line_words) == 2:
            lines.append(' '.join(current_line_words))
            current_line_words = []

            # Stop if we've reached max lines
            if len(lines) >= max_lines:
                break

    # Add any remaining words as final line
    if current_line_words and len(lines) < max_lines:
        lines.append(' '.join(current_line_words))

    return lines[:max_lines]
