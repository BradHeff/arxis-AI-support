Version_Number = "1.0.0.8"
Version = "".join(["v", Version_Number])
DEBUG = False


def format_response_text(text: str) -> str:
    """Format the response text for proper display in the GUI.

    - Replace literal "\\n" escapes with real newlines.
    - Preserve list and numbered-line formatting.
    """
    if not text:
        return text

    formatted = text.replace("\\n", "\n")

    lines = formatted.split("\n")
    processed_lines = []

    for line in lines:

        if line.strip() and line.strip()[0].isdigit() and ")" in line[:5]:
            processed_lines.append(line)

        elif line.strip().startswith("-"):
            processed_lines.append(line)

        else:
            processed_lines.append(line)

    return "\n".join(processed_lines)


def split_text_for_streaming(text: str) -> list:
    """Split text into chunks for streaming while preserving formatting.

    Returns a list of string chunks; newline boundaries are preserved as separate entries.
    """
    chunks = []
    lines = text.split("\n")

    for i, line in enumerate(lines):
        if line.strip():

            words = line.split()
            current_chunk = ""

            for word in words:
                if current_chunk:
                    current_chunk += " " + word
                else:
                    current_chunk = word

                if len(current_chunk) > 20 or word == words[-1]:
                    chunks.append(current_chunk)
                    current_chunk = ""

        if i < len(lines) - 1:

            chunks.append("\n")

    return chunks
