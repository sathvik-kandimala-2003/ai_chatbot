# Compares the text of two documents and identifies similarities and differences.

def compare_texts(text1, text2):
    """
    Compares two pieces of text and returns similarities and differences.

    Args:
        text1 (str): The text from the first document.
        text2 (str): The text from the second document.

    Returns:
        tuple: A tuple containing two lists - similarities and differences.
    """
    # Split the text into lines and convert to sets
    text1_lines = set(text1.splitlines())
    text2_lines = set(text2.splitlines())

    # Find similarities (common lines)
    similarities = list(text1_lines & text2_lines)

    # Find differences (lines that are not common)
    differences = list(text1_lines ^ text2_lines)

    return similarities, differences