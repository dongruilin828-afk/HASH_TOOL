from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from android_main import HashToolAndroidApp
from config import ALGORITHM_MAP, HASH_LENGTHS
from hash_utils import calculate_file_hash, calculate_hash


def main():
    app = HashToolAndroidApp()
    app.build()

    app.input_text.text = "abc"
    app.generate_text_hash()
    sha256 = calculate_hash("abc", "sha256")
    assert app.output_text.text == sha256

    app._selected_file_uri = "content://test/abc.txt"
    app.selected_file_name = "abc.txt"
    app.open_selected_file = lambda: BytesIO(b"abc")
    app.generate_file_hash()
    assert app.output_text.text == sha256

    app.expected_hash_input.text = sha256.upper()
    app.verify_file_hash()
    assert app.verification_text == "Verification passed: hashes match"

    app.expected_hash_input.text = "0" * HASH_LENGTHS["SHA-256"]
    app.verify_file_hash()
    assert app.verification_text == "Verification failed: hashes differ"

    messages = []
    app.show_message = lambda title, message: messages.append((title, message))
    app.expected_hash_input.text = "x" * HASH_LENGTHS["SHA-256"]
    app.verify_file_hash()
    assert messages[-1][0] == "Incorrect hash format"

    for name, algorithm in ALGORITHM_MAP.items():
        app.algorithm_spinner.text = name
        app.generate_text_hash()
        assert len(app.output_text.text) == HASH_LENGTHS[name]
        assert app.output_text.text == calculate_hash("abc", algorithm)

    app.clear_all()
    assert app.input_text.text == ""
    assert app.output_text.text == ""
    assert app.expected_hash_input.text == ""
    assert app.verification_text == "Verification: not checked"
    assert app.selected_file_name == "abc.txt"

    with TemporaryDirectory() as directory:
        file_path = Path(directory, "abc.txt")
        file_path.write_bytes(b"abc")
        assert calculate_file_hash(file_path) == sha256

    print("android parity checks: ok")


if __name__ == "__main__":
    main()
