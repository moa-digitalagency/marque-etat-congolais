"""
Text splitting algorithm for logo generation.

Splits institution names according to these rules:
1. Articles and prepositions (de, la, du, le, l', etc.) are NOT counted as words
2. If 2 "real" words total: split into 2 lines (1 word per line)
3. If 3+ "real" words: split into at least 3 lines (1 word per line for short names, up to 2 words per line)
4. Maximum 5 lines total
5. All text converted to UPPERCASE
6. Special rule: "secrétariat général" must never be split across lines - if detected, ensure it's on its own line

Examples:
    "Ministère de la Défense" = 2 real words (Ministère, Défense)
    "Ministère de l'économie numérique" = 3 real words (Ministère, économie, numérique)
    "Ministère du Secrétariat Général" → SECRÉTARIAT GÉNÉRAL stays together on new line
"""

# Articles and prepositions to ignore when counting words
ARTICLES_AND_PREPOSITIONS = {
    'DE', 'LA', 'DU', 'LE', 'L', "L'", 'UN', 'UNE', 'DES',
    'AU', 'AUX', 'ET', 'OU', 'D', "D'", 'EN', 'POUR', 'AVEC',
    'SANS', 'SOUS', 'SUR', 'ENTRE', 'DANS', 'PAR', 'VERS',
    'PENDANT', 'DEPUIS', 'JUSQU', "À", 'A', 'PRÈS',
}


def split_unit_name_ambassade(nom: str) -> list:
    """
    Special splitting algorithm for Ambassade RDC model.
    - First real word (with articles) goes alone on line 1
    - Remaining groups are combined to max 3 real words per line

    Example:
        "Ambassade de la République Démocratique du Congo près le Royaume du Maroc"
        becomes:
        ['AMBASSADE', 'DE LA RÉPUBLIQUE DÉMOCRATIQUE', 'DU CONGO PRÈS LE ROYAUME', 'DU MAROC']
    """
    if not nom or not nom.strip():
        return []

    words = nom.upper().split()
    words = [w for w in words if w]

    if not words:
        return []

    # First pass: group each real word with its preceding articles/prepositions
    word_groups = []
    current_group = []

    for word in words:
        current_group.append(word)

        if word not in ARTICLES_AND_PREPOSITIONS:
            # This is a real word, so commit the group
            word_groups.append(' '.join(current_group))
            current_group = []

    # Handle any trailing articles (shouldn't normally happen with well-formed input)
    if current_group:
        word_groups.append(' '.join(current_group))

    if not word_groups:
        return []

    # Second pass: first group alone, then combine remaining groups
    split_lines = []

    # First real word group goes alone on first line
    split_lines.append(word_groups[0])

    # Combine remaining groups: aim for 2 real words per line, max 3
    current_line_groups = []
    real_words_in_line = 0

    for group in word_groups[1:]:
        # Count real words in this group
        real_word_count = sum(1 for w in group.split() if w not in ARTICLES_AND_PREPOSITIONS)

        # If we already have 2 real words, start a new line (unless next would be 3 or fewer total)
        if real_words_in_line >= 2 and real_words_in_line + real_word_count > 2:
            # Commit current line and start new one
            if current_line_groups:
                split_lines.append(' '.join(current_line_groups))
            current_line_groups = [group]
            real_words_in_line = real_word_count
        elif real_words_in_line + real_word_count > 3:
            # Would exceed max of 3, so commit and start new
            if current_line_groups:
                split_lines.append(' '.join(current_line_groups))
            current_line_groups = [group]
            real_words_in_line = real_word_count
        else:
            # Add to current line
            current_line_groups.append(group)
            real_words_in_line += real_word_count

    # Handle remaining groups
    if current_line_groups:
        split_lines.append(' '.join(current_line_groups))

    return split_lines


def split_unit_name(nom: str, max_lines: int = 5) -> list:
    """
    Split unit/institution name into lines for logo generation.

    Articles and prepositions (de, la, du, etc.) are not counted as "real" words.

    Special rule: If "secrétariat" and "général" are both present, ensure they are never
    split across different lines. They will be combined on the same line.

    Args:
        nom: Institution name (any case)
        max_lines: Maximum number of lines (default 5)

    Returns:
        List of strings, each representing one line of the logo text
        Each string is UPPERCASE

    Examples:
        >>> split_unit_name("Ministère de la Défense")
        ['MINISTÈRE', 'DE LA DÉFENSE']

        >>> split_unit_name("Ministère du Secrétariat Général")
        ['MINISTÈRE DU', 'SECRÉTARIAT GÉNÉRAL']  # Secrétariat Général kept together on new line
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

        split_lines = combined_lines[:practical_max_lines]
    else:
        split_lines = split_lines[:practical_max_lines]

    # Post-processing: Handle "secrétariat général" special rule
    # "Secrétariat général" must ALWAYS be on its own separate line
    # If it's mixed with other text on the same line, split it out
    # Handles spelling variations (with/without accents, typos, etc.)

    def normalize_for_match(text: str) -> str:
        """Normalize text for matching (remove accents, uppercase)"""
        replacements = {
            'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
            'À': 'A', 'Â': 'A', 'Ô': 'O', 'Ù': 'U', 'Û': 'U', 'Ç': 'C',
        }
        text = text.upper()
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        return text

    # Check if both SECRÉTARIAT and GÉNÉRAL exist (with spelling variations)
    joined_text = ' '.join(split_lines)
    normalized = normalize_for_match(joined_text)

    if 'SECRETARIAT' in normalized and 'GENERAL' in normalized:
        new_lines = []

        for line in split_lines:
            line_norm = normalize_for_match(line)
            words = line.split()

            # Check if this line contains SECRÉTARIAT
            if 'SECRETARIAT' in line_norm:
                # Find the index of the word containing SECRÉTARIAT
                secretariat_word_idx = None
                for i, word in enumerate(words):
                    if 'SECRETARIAT' in normalize_for_match(word):
                        secretariat_word_idx = i
                        break

                if secretariat_word_idx is not None:
                    # If there are words BEFORE secrétariat, split them
                    if secretariat_word_idx > 0:
                        before = ' '.join(words[:secretariat_word_idx])
                        from_secretariat = ' '.join(words[secretariat_word_idx:])
                        new_lines.append(before)
                        new_lines.append(from_secretariat)
                    else:
                        # SECRÉTARIAT is at the start of the line, keep as is
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            else:
                # Line doesn't contain SECRÉTARIAT, keep as is
                new_lines.append(line)

        split_lines = new_lines

    return split_lines
