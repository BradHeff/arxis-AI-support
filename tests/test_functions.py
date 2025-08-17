from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path


func_path = (
    Path(__file__).resolve().parents[1]
    / "usr"
    / "lib"
    / "Arxis-AI-Support"
    / "Functions.py"
)
spec = spec_from_file_location("Functions", str(func_path))
functions = module_from_spec(spec)
spec.loader.exec_module(functions)

format_response_text = functions.format_response_text
split_text_for_streaming = functions.split_text_for_streaming


def run_tests():
    inp = "Line1\\nLine2"
    out = format_response_text(inp)
    assert "Line1\nLine2" == out

    inp = "1) Item one\\n- bullet item\\nNormal paragraph"
    out = format_response_text(inp)
    assert "1) Item one" in out
    assert "- bullet item" in out

    text = "This is a test line that will be chunked.\nNext line"
    chunks = split_text_for_streaming(text)
    assert "\n" in chunks
    reconstructed = "".join([c if c != "\n" else "\n" for c in chunks])
    assert "This is a test line" in reconstructed


if __name__ == "__main__":
    run_tests()
    print("All tests passed")
