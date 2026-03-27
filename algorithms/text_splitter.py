"""
Text splitting algorithm for logo generation.

Splits institution names according to these rules:
1. Articles and prepositions (de, la, du, le, l', etc.) are NOT counted as words
2. If 2 "real" words total: split into 2 lines (1 word per line)
3. If 3+ "real" words: split into at least 3 lines (1 word per line for short names, up to 2 words per line)
4. Maximum 5 lines total
5. All text converted to UPPERCASE

Examples:
    "Ministère de la Défense" = 2 real words (Ministère, Défense)
    "Ministère de l'économie numérique" = 3 real words (Ministère, économie, numérique)
"""

# Articles and prepositions to ignore when counting words
ARTICLES_AND_PREPOSITIONS = {
    'DE', 'LA', 'DU', 'LE', 'L', "L'", 'UN', 'UNE', 'DES',
    'AU', 'AUX', 'ET', 'OU', 'D', "D'", 'EN', 'POUR', 'AVEC',
    'SANS', 'SOUS', 'SUR', 'ENTRE', 'DANS', 'PAR', 'VERS',
    'PENDANT', 'DEPUIS', 'JUSQU', "À", 'A',
}


def split_unit_name(nom: str, max_lines: int = 5) -> list:
    """
    Split unit/institution name into lines for logo generation.

    Articles and prepositions (de, la, du, etc.) are not counted as "real" words.

    Args:
        nom: Institution name (any case)
        max_lines: Maximum number of lines (default 5)

    Returns:
        List of strings, each representing one line of the logo text
        Each string is UPPERCASE

    Examples:
        >>> split_unit_name("Ministère de la Défense")
        ['MINISTÈRE', 'DE LA DÉFENSE']  # 2 real words = 2 lines

        >>> split_unit_name("Ministère de l'économie numérique")
        ['MINISTÈRE', 'DE L'ÉCONOMIE', 'NUMÉRIQUE']  # 3 real words

        >>> split_unit_name("Ambassade de la République Démocratique du Congo")
        ['AMBASSADE', 'DE LA RÉPUBLIQUE', 'DÉMOCRATIQUE DU CONGO']  # 4 real words
    """
    # Validate input
    if not nom or not nom.strip():
        return []

    # Convert to uppercase and split into words
    words = nom.upper().split()
    words = [w for w in words if w]  # Remove empty strings

    if not words:
        return []

    # Count "real" words (excluding articles and prepositions)
    real_word_count = sum(1 for w in words if w not in ARTICLES_AND_PREPOSITIONS)

    # If no real words, return original words
    if real_word_count == 0:
        return words[:max_lines]

    # If only 1 real word, return as is
    if real_word_count == 1:
        return words

    # Split into lines: 1 real word per line (with articles/prepositions attached)
    # Then combine final lines if needed to stay within max_lines
    split_lines = []
    current_line = []

    for word in words:
        current_line.append(word)
        if word not in ARTICLES_AND_PREPOSITIONS:
            # This is a real word, commit the line
            split_lines.append(' '.join(current_line))
            current_line = []

    # Handle any remaining words (shouldn't happen if input is clean)
    if current_line:
        split_lines.append(' '.join(current_line))

    # Limit lines: if 4+ real words, try to limit to 3 lines max for better presentation
    # Otherwise keep up to max_lines
    practical_max_lines = 3 if real_word_count >= 4 else max_lines

    # If we have more lines than practical_max_lines, combine final lines
    if len(split_lines) > practical_max_lines:
        combined_lines = split_lines[:practical_max_lines-1]  # Keep first (practical_max_lines-1) lines

        # Combine remaining lines
        remaining = split_lines[practical_max_lines-1:]
        combined_lines.append(' '.join(remaining))

        return combined_lines[:practical_max_lines]

    return split_lines[:practical_max_lines]
