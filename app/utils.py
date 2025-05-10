def compare_texts(text1, text2):
    text1_lines = set(text1.splitlines())
    text2_lines = set(text2.splitlines())

    similarities = list(text1_lines & text2_lines)  # Common lines
    differences = list(text1_lines ^ text2_lines)  # Different lines

    return similarities, differences