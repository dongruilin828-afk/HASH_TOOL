import os

from kivy.app import App
from kivy.core.clipboard import Clipboard
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ListProperty, StringProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.utils import platform

from config import (
    ALGORITHM_MAP,
    APP_AUTHOR,
    APP_NAME,
    APP_VERSION,
    DEFAULT_ALGORITHM,
    HASH_LENGTHS,
)
from hash_utils import calculate_hash, calculate_stream_hash


KV = r"""
#:import dp kivy.metrics.dp

<SectionLabel@Label>:
    size_hint_y: None
    height: dp(36)
    bold: True
    halign: "left"
    valign: "middle"
    text_size: self.size

<ActionButton@Button>:
    size_hint_y: None
    height: dp(52)
    font_size: "15sp"

ScrollView:
    do_scroll_x: False

    BoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(10)
        size_hint_y: None
        height: self.minimum_height

        Label:
            text: app.app_name + " v" + app.app_version
            size_hint_y: None
            height: dp(58)
            font_size: "26sp"

        Label:
            text: "Text and file hash calculator"
            size_hint_y: None
            height: dp(34)
            font_size: "14sp"

        SectionLabel:
            text: "Text hash"

        TextInput:
            id: input_text
            hint_text: "Enter text..."
            multiline: True
            size_hint_y: None
            height: dp(150)
            font_size: "16sp"

        SectionLabel:
            text: "File hash"

        Label:
            text: app.selected_file_name
            size_hint_y: None
            height: dp(48)
            halign: "left"
            valign: "middle"
            text_size: self.size
            shorten: True
            shorten_from: "center"

        ActionButton:
            text: "Select file"
            on_release: app.select_file()

        SectionLabel:
            text: "Hash algorithm"

        Spinner:
            id: algorithm_spinner
            text: app.default_algorithm
            values: app.algorithm_names
            size_hint_y: None
            height: dp(50)
            font_size: "16sp"

        BoxLayout:
            size_hint_y: None
            height: dp(52)
            spacing: dp(10)

            ActionButton:
                text: "Calculate text"
                on_release: app.generate_text_hash()

            ActionButton:
                text: "Calculate file"
                on_release: app.generate_file_hash()

        SectionLabel:
            text: app.output_caption

        TextInput:
            id: output_text
            readonly: True
            multiline: True
            size_hint_y: None
            height: dp(135)
            font_size: "15sp"

        BoxLayout:
            size_hint_y: None
            height: dp(52)
            spacing: dp(10)

            ActionButton:
                text: "Copy result"
                on_release: app.copy_result()

            ActionButton:
                text: "Clear"
                on_release: app.clear_all()

        SectionLabel:
            text: "File integrity verification"

        TextInput:
            id: expected_hash_input
            hint_text: "Expected hash"
            multiline: False
            size_hint_y: None
            height: dp(50)
            font_size: "15sp"

        ActionButton:
            text: "Verify file"
            on_release: app.verify_file_hash()

        Label:
            text: app.verification_text
            size_hint_y: None
            height: dp(44)
            halign: "center"
            valign: "middle"
            text_size: self.size

        Label:
            text: app.status_text
            size_hint_y: None
            height: max(dp(52), self.texture_size[1] + dp(12))
            halign: "left"
            valign: "middle"
            text_size: self.width, None
            font_size: "13sp"

        ActionButton:
            text: "About"
            on_release: app.show_about()
"""


class HashToolAndroidApp(App):
    FILE_PICKER_REQUEST = 5001

    app_name = StringProperty(APP_NAME)
    app_version = StringProperty(APP_VERSION)
    default_algorithm = StringProperty(DEFAULT_ALGORITHM)
    algorithm_names = ListProperty(list(ALGORITHM_MAP))
    selected_file_name = StringProperty("No file selected")
    output_caption = StringProperty(f"{DEFAULT_ALGORITHM} digest")
    verification_text = StringProperty("Verification: not checked")
    status_text = StringProperty("")

    def build(self):
        self.title = f"{APP_NAME} {APP_VERSION}"
        self._selected_file_uri = None
        self._picker_bound = False

        root = Builder.load_string(KV)
        self.input_text = root.ids.input_text
        self.algorithm_spinner = root.ids.algorithm_spinner
        self.output_text = root.ids.output_text
        self.expected_hash_input = root.ids.expected_hash_input

        self.input_text.bind(text=self.update_status)
        self.output_text.bind(text=self.update_status)
        self.algorithm_spinner.bind(text=self.on_algorithm_changed)
        self.expected_hash_input.bind(text=self.on_expected_hash_changed)
        self.update_status()
        return root

    def selected_algorithm(self):
        name = self.algorithm_spinner.text
        return name, ALGORITHM_MAP[name]

    def generate_text_hash(self, *_):
        name, algorithm = self.selected_algorithm()
        self.show_hash_result(
            calculate_hash(self.input_text.text, algorithm),
            f"{name} text digest",
        )

    def select_file(self, *_):
        if platform != "android":
            self.show_message(
                "Android only",
                "The system file picker is available in the APK.",
            )
            return

        from android import activity
        from jnius import autoclass

        Intent = autoclass("android.content.Intent")
        PythonActivity = autoclass(
            "org.kivy.android.PythonActivity"
        )

        intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
        intent.addCategory(Intent.CATEGORY_OPENABLE)
        intent.setType("*/*")
        intent.addFlags(
            Intent.FLAG_GRANT_READ_URI_PERMISSION
            | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION
        )

        if not self._picker_bound:
            activity.bind(
                on_activity_result=self.on_activity_result
            )
            self._picker_bound = True

        try:
            PythonActivity.mActivity.startActivityForResult(
                intent,
                self.FILE_PICKER_REQUEST,
            )
        except Exception as error:
            self.unbind_file_picker()
            self.show_message("File picker failed", str(error))

    def on_activity_result(
        self,
        request_code,
        result_code,
        intent,
    ):
        if request_code != self.FILE_PICKER_REQUEST:
            return

        self.unbind_file_picker()

        from jnius import autoclass

        Activity = autoclass("android.app.Activity")
        Intent = autoclass("android.content.Intent")
        PythonActivity = autoclass(
            "org.kivy.android.PythonActivity"
        )

        if result_code != Activity.RESULT_OK or intent is None:
            return

        uri = intent.getData()
        if uri is None:
            return

        resolver = PythonActivity.mActivity.getContentResolver()
        flags = intent.getFlags() & (
            Intent.FLAG_GRANT_READ_URI_PERMISSION
            | Intent.FLAG_GRANT_WRITE_URI_PERMISSION
        )

        try:
            resolver.takePersistableUriPermission(uri, flags)
        except Exception:
            pass

        self._selected_file_uri = str(uri.toString())
        self.selected_file_name = self.android_display_name(
            resolver,
            uri,
        )
        self.verification_text = "Verification: not checked"

    def unbind_file_picker(self):
        if not self._picker_bound:
            return

        from android import activity

        activity.unbind(
            on_activity_result=self.on_activity_result
        )
        self._picker_bound = False

    @staticmethod
    def android_display_name(resolver, uri):
        try:
            cursor = resolver.query(uri, None, None, None, None)
        except Exception:
            return str(uri.getLastPathSegment() or uri.toString())

        try:
            if cursor is not None and cursor.moveToFirst():
                index = cursor.getColumnIndex("_display_name")
                if index >= 0:
                    return str(cursor.getString(index))
        finally:
            if cursor is not None:
                cursor.close()

        return str(uri.getLastPathSegment() or uri.toString())

    def open_selected_file(self):
        if platform != "android":
            raise OSError("Android content URI is unavailable")

        from jnius import autoclass

        PythonActivity = autoclass(
            "org.kivy.android.PythonActivity"
        )
        Uri = autoclass("android.net.Uri")
        resolver = PythonActivity.mActivity.getContentResolver()

        try:
            descriptor = resolver.openFileDescriptor(
                Uri.parse(self._selected_file_uri),
                "r",
            )
            if descriptor is None:
                raise OSError("The selected file cannot be opened")
            return os.fdopen(descriptor.detachFd(), "rb")
        except OSError:
            raise
        except Exception as error:
            raise OSError(str(error)) from error

    def calculate_selected_file_hash(self):
        _, algorithm = self.selected_algorithm()
        with self.open_selected_file() as stream:
            return calculate_stream_hash(stream, algorithm)

    def generate_file_hash(self, *_):
        if not self.require_selected_file():
            return

        try:
            result = self.calculate_selected_file_hash()
        except OSError as error:
            self.show_message("File read failed", str(error))
            return

        name, _ = self.selected_algorithm()
        self.show_hash_result(result, f"{name} file digest")

    def verify_file_hash(self, *_):
        if not self.require_selected_file():
            return

        expected = self.expected_hash_input.text.strip()
        name, _ = self.selected_algorithm()

        if not expected:
            self.show_message(
                "Expected hash required",
                "Enter the expected hash before verification.",
            )
            return

        required_length = HASH_LENGTHS[name]
        if len(expected) != required_length:
            self.show_message(
                "Incorrect hash length",
                f"{name} requires {required_length} hexadecimal characters; "
                f"received {len(expected)}.",
            )
            return

        try:
            int(expected, 16)
        except ValueError:
            self.show_message(
                "Incorrect hash format",
                "A hash may contain only hexadecimal characters 0-9 and A-F.",
            )
            return

        try:
            actual = self.calculate_selected_file_hash()
        except OSError as error:
            self.show_message("File read failed", str(error))
            return

        self.show_hash_result(actual, f"{name} file digest")
        self.verification_text = (
            "Verification passed: hashes match"
            if actual.lower() == expected.lower()
            else "Verification failed: hashes differ"
        )

    def require_selected_file(self):
        if self._selected_file_uri:
            return True

        self.show_message(
            "No file selected",
            "Select a file before calculating or verifying its hash.",
        )
        return False

    def show_hash_result(self, result, caption):
        self.output_text.text = result
        self.output_caption = caption
        self.update_status()

    def copy_result(self, *_):
        if not self.output_text.text:
            self.show_message(
                "Nothing to copy",
                "Calculate a hash first.",
            )
            return
        Clipboard.copy(self.output_text.text)

    def clear_all(self, *_):
        self.input_text.text = ""
        self.output_text.text = ""
        self.algorithm_spinner.text = DEFAULT_ALGORITHM
        self.expected_hash_input.text = ""
        self.output_caption = f"{DEFAULT_ALGORITHM} digest"
        self.verification_text = "Verification: not checked"
        self.input_text.focus = True
        self.update_status()

    def update_status(self, *_):
        if not hasattr(self, "input_text"):
            return

        text = self.input_text.text
        self.status_text = (
            f"Input: {len(text)} characters / "
            f"{len(text.encode('utf-8'))} bytes\n"
            f"Algorithm: {self.algorithm_spinner.text} | "
            f"Output: {len(self.output_text.text)} characters"
        )

    def on_algorithm_changed(self, *_):
        self.verification_text = "Verification: not checked"
        self.update_status()

    def on_expected_hash_changed(self, *_):
        self.verification_text = "Verification: not checked"

    def show_about(self, *_):
        self.show_message(
            f"About {APP_NAME}",
            f"{APP_NAME}\n\n"
            f"Version: {APP_VERSION}\n\n"
            "Text and file hash calculator\n\n"
            f"Author: {APP_AUTHOR}\n\n"
            "Algorithms: MD5, SHA-1, SHA-256, SHA-512",
        )

    @staticmethod
    def show_message(title, message):
        Popup(
            title=title,
            content=Label(
                text=message,
                halign="center",
                valign="middle",
                text_size=(dp(280), None),
            ),
            size_hint=(0.9, None),
            height=dp(260),
        ).open()


if __name__ == "__main__":
    HashToolAndroidApp().run()
