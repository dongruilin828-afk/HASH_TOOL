from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import ImageFont

from android_main import HashToolAndroidApp
from config import ALGORITHM_MAP, HASH_LENGTHS
from hash_utils import calculate_file_hash, calculate_hash


def main():
    app = HashToolAndroidApp()
    root = app.build()

    font_widgets = [
        widget
        for widget in root.walk()
        if hasattr(widget, "font_name")
    ]
    assert font_widgets
    assert app.output_text.use_handles is True
    assert app.output_text.use_bubble is True
    assert app.output_text.unfocus_on_touch is True
    app.output_text.text = "abcdef"
    app.output_text.focus = True
    app.output_text.select_all()
    assert app.output_text.selection_text == "abcdef"
    touch = type("Touch", (), {"pos": app.output_text.center})()
    assert app.output_text.on_touch_down(touch) is True
    assert app.output_text.selection_text == ""
    app.output_text.select_all()
    assert app.output_text.selection_text == "abcdef"
    app.output_text.focus = False
    assert all(
        str(widget.font_name).replace("\\", "/").endswith(
            "assets/NotoSansSC.ttf"
        )
        for widget in font_widgets
    )

    app.input_text.text = "中文测试"
    app.generate_text_hash()
    text_sha256 = calculate_hash("中文测试", "sha256")
    assert app.output_text.text == text_sha256

    font_path = Path("assets/NotoSansSC.ttf")
    assert font_path.stat().st_size > 10_000_000
    font = ImageFont.truetype(font_path, 32)
    assert bytes(font.getmask("中文")) != bytes(font.getmask(chr(0x10FFFF)))

    app._selected_file_uri = "content://test/abc.txt"
    app.selected_file_name = "abc.txt"
    app.open_selected_file = lambda: BytesIO(b"abc")
    app.generate_file_hash()
    file_sha256 = calculate_hash("abc", "sha256")
    assert app.output_text.text == file_sha256

    app.expected_hash_input.text = file_sha256.upper()
    app.verify_file_hash()
    assert app.verification_text == "✓ 校验通过：哈希值一致"

    app.expected_hash_input.text = "0" * HASH_LENGTHS["SHA-256"]
    app.verify_file_hash()
    assert app.verification_text == "✗ 校验失败：哈希值不一致"

    messages = []
    app.show_message = lambda title, message: messages.append((title, message))
    app.expected_hash_input.text = "x" * HASH_LENGTHS["SHA-256"]
    app.verify_file_hash()
    assert messages[-1][0] == "哈希格式不正确"

    about = []
    app.show_message = lambda title, message, popup_height=250: about.append(
        (title, message, popup_height)
    )
    app.show_about()
    assert about[-1][0] == "关于哈希工具"
    assert about[-1][2] == 330

    for name, algorithm in ALGORITHM_MAP.items():
        app.algorithm_spinner.text = name
        app.generate_text_hash()
        assert len(app.output_text.text) == HASH_LENGTHS[name]
        assert app.output_text.text == calculate_hash("中文测试", algorithm)

    app.clear_all()
    assert app.input_text.text == ""
    assert app.input_text.focus is False
    assert app.output_text.text == ""
    assert app.expected_hash_input.text == ""
    assert app.verification_text == "校验结果：尚未校验"
    assert app.selected_file_name == "abc.txt"

    with TemporaryDirectory() as directory:
        file_path = Path(directory, "abc.txt")
        file_path.write_bytes(b"abc")
        assert calculate_file_hash(file_path) == file_sha256

    print("android Chinese UI checks: ok")


if __name__ == "__main__":
    main()
