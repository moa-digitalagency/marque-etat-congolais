"""
Text splitting algorithm for logo generation.

Splits institution names according to these rules:
1. First line = first word only
2. Following lines = max 3 words per line
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
        >>> split_unit_name("Ambassade de France")
        ['AMBASSADE', 'DE FRANCE']

        >>> split_unit_name("Ambassade de la RDC en France")
        ['AMBASSADE', 'DE LA RDC', 'EN FRANCE']
    """
    # Validate input
    if not nom or not nom.strip():
        return []

    # Convert to uppercase and split into words
    words = nom.upper().split()
    words = [w for w in words if w]  # Remove empty strings

    if not words:
        return []

    # Start with first word on first line
    lines = [words[0]]
    current_line_words = []

    # Process remaining words
    for word in words[1:]:
        current_line_words.append(word)

        # If we've reached 3 words, commit this line
        if len(current_line_words) == 3:
            lines.append(' '.join(current_line_words))
            current_line_words = []

            # Stop if we've reached max lines
            if len(lines) >= max_lines:
                break

    # Add any remaining words as final line
    if current_line_words and len(lines) < max_lines:
        lines.append(' '.join(current_line_words))

    # Return first max_lines entries
    return lines[:max_lines]
