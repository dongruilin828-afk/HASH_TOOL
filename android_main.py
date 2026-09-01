import os

from kivy.app import App
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.utils import platform

from config import (
    ALGORITHM_MAP,
    APP_AUTHOR,
    APP_VERSION,
    DEFAULT_ALGORITHM,
    HASH_LENGTHS,
)
from hash_utils import calculate_hash, calculate_stream_hash


FONT_PATH = "assets/NotoSansSC.ttf"

# 设置深色背景 (Slate-950)
Window.clearcolor = (0.043, 0.067, 0.125, 1)


class ResultTextInput(TextInput):
    def on_touch_down(self, touch):
        handles = (self._handle_left, self._handle_right, self._handle_middle)
        if self.collide_point(*touch.pos) and (
            self.selection_text
            or any(handle and handle.parent for handle in handles)
        ):
            self.cancel_selection()
            self._hide_cut_copy_paste()
            self._hide_handles()
            return True
        return super().on_touch_down(touch)


KV = r"""
#:import dp kivy.metrics.dp
#:set chinese_font "assets/NotoSansSC.ttf"

<Label>:
    font_name: chinese_font

<Button>:
    font_name: chinese_font

<TextInput>:
    font_name: chinese_font

<Spinner>:
    font_name: chinese_font

<SpinnerOption>:
    font_name: chinese_font
    background_color: (0, 0, 0, 0)
    background_normal: ""
    background_down: ""
    size_hint_y: None
    height: dp(46)
    font_size: "15sp"
    color: (0.94, 0.96, 0.98, 1)
    canvas.before:
        Color:
            rgba: (0.145, 0.514, 0.922, 1) if self.state == "down" else (0.118, 0.161, 0.231, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(6)]
        Color:
            rgba: (0.200, 0.255, 0.333, 1)
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(6)]
            width: dp(0.8)

<ModernCard@BoxLayout>:
    orientation: "vertical"
    size_hint_y: None
    height: self.minimum_height
    padding: [dp(16), dp(14), dp(16), dp(16)]
    spacing: dp(10)
    canvas.before:
        Color:
            rgba: (0.118, 0.161, 0.231, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]
        Color:
            rgba: (0.200, 0.255, 0.333, 0.75)
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(12)]
            width: dp(1)

<CardHeader@BoxLayout>:
    size_hint_y: None
    height: dp(26)
    spacing: dp(8)
    title_text: ""
    Widget:
        size_hint: None, None
        size: dp(4), dp(18)
        pos_hint: {"center_y": 0.5}
        canvas:
            Color:
                rgba: (0.231, 0.510, 0.965, 1)
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(2)]
    Label:
        text: root.title_text
        bold: True
        font_size: "15sp"
        color: (0.94, 0.96, 0.98, 1)
        halign: "left"
        valign: "middle"
        text_size: self.size

<ModernTextInput@TextInput>:
    font_name: chinese_font
    background_color: (0, 0, 0, 0)
    background_normal: ""
    background_active: ""
    foreground_color: (0.94, 0.96, 0.98, 1)
    cursor_color: (0.376, 0.647, 0.980, 1)
    hint_text_color: (0.450, 0.520, 0.620, 1)
    padding: [dp(12), dp(10), dp(12), dp(10)]
    canvas.before:
        Color:
            rgba: (0.059, 0.090, 0.165, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(8)]
        Color:
            rgba: (0.231, 0.510, 0.965, 1) if self.focus else (0.200, 0.255, 0.333, 1)
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(8)]
            width: dp(1.2) if self.focus else dp(1)

<ResultTextInput>:
    font_name: chinese_font
    background_color: (0, 0, 0, 0)
    background_normal: ""
    background_active: ""
    foreground_color: (0.220, 0.741, 0.973, 1)
    cursor_color: (0.376, 0.647, 0.980, 1)
    hint_text_color: (0.450, 0.520, 0.620, 1)
    padding: [dp(12), dp(10), dp(12), dp(10)]
    canvas.before:
        Color:
            rgba: (0.043, 0.067, 0.125, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(8)]
        Color:
            rgba: (0.200, 0.255, 0.333, 1)
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(8)]
            width: dp(1)

<PrimaryBtn@Button>:
    font_name: chinese_font
    background_color: (0, 0, 0, 0)
    background_normal: ""
    background_down: ""
    size_hint_y: None
    height: dp(48)
    font_size: "15sp"
    bold: True
    color: (1, 1, 1, 1)
    canvas.before:
        Color:
            rgba: (0.114, 0.392, 0.745, 1) if self.state == "down" else (0.145, 0.514, 0.922, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(8)]

<SecondaryBtn@Button>:
    font_name: chinese_font
    background_color: (0, 0, 0, 0)
    background_normal: ""
    background_down: ""
    size_hint_y: None
    height: dp(46)
    font_size: "14sp"
    color: (0.94, 0.96, 0.98, 1)
    canvas.before:
        Color:
            rgba: (0.150, 0.200, 0.280, 1) if self.state == "down" else (0.200, 0.255, 0.333, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(8)]
        Color:
            rgba: (0.280, 0.350, 0.450, 0.8)
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(8)]
            width: dp(1)

<SuccessBtn@Button>:
    font_name: chinese_font
    background_color: (0, 0, 0, 0)
    background_normal: ""
    background_down: ""
    size_hint_y: None
    height: dp(48)
    font_size: "15sp"
    bold: True
    color: (1, 1, 1, 1)
    canvas.before:
        Color:
            rgba: (0.016, 0.471, 0.341, 1) if self.state == "down" else (0.063, 0.725, 0.506, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(8)]

<DangerBtn@Button>:
    font_name: chinese_font
    background_color: (0, 0, 0, 0)
    background_normal: ""
    background_down: ""
    size_hint_y: None
    height: dp(46)
    font_size: "14sp"
    color: (0.98, 0.80, 0.80, 1)
    canvas.before:
        Color:
            rgba: (0.350, 0.120, 0.120, 1) if self.state == "down" else (0.250, 0.140, 0.160, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(8)]
        Color:
            rgba: (0.600, 0.200, 0.200, 0.6)
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(8)]
            width: dp(1)

<ModernSpinner@Spinner>:
    font_name: chinese_font
    background_color: (0, 0, 0, 0)
    background_normal: ""
    background_down: ""
    size_hint_y: None
    height: dp(46)
    font_size: "15sp"
    bold: True
    color: (0.94, 0.96, 0.98, 1)
    canvas.before:
        Color:
            rgba: (0.145, 0.204, 0.298, 1) if self.state == "down" else (0.059, 0.090, 0.165, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(8)]
        Color:
            rgba: (0.231, 0.306, 0.408, 1)
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(8)]
            width: dp(1)

ScrollView:
    do_scroll_x: False
    bar_width: dp(4)
    bar_color: (0.231, 0.510, 0.965, 0.5)

    BoxLayout:
        orientation: "vertical"
        padding: [dp(14), dp(16), dp(14), dp(24)]
        spacing: dp(14)
        size_hint_y: None
        height: self.minimum_height

        # =========================
        # 头部区域
        # =========================
        BoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: dp(72)
            spacing: dp(4)

            BoxLayout:
                size_hint_y: None
                height: dp(38)
                spacing: dp(10)

                Label:
                    text: "哈希工具"
                    size_hint_x: None
                    width: self.texture_size[0]
                    font_size: "24sp"
                    bold: True
                    color: (0.98, 0.98, 0.99, 1)
                    halign: "left"
                    valign: "middle"

                Widget:
                    size_hint_y: None
                    height: dp(22)
                    size_hint_x: None
                    width: version_label.texture_size[0] + dp(16)
                    pos_hint: {"center_y": 0.5}
                    canvas.before:
                        Color:
                            rgba: (0.118, 0.161, 0.231, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(6)]
                        Color:
                            rgba: (0.231, 0.510, 0.965, 0.8)
                        Line:
                            rounded_rectangle: [self.x, self.y, self.width, self.height, dp(6)]
                            width: dp(0.8)
                    Label:
                        id: version_label
                        text: "v" + app.app_version
                        font_size: "12sp"
                        bold: True
                        color: (0.376, 0.647, 0.980, 1)
                        center: self.parent.center

                Widget:
                    # 占位弹簧

            Label:
                text: "文本与文件哈希计算工具"
                size_hint_y: None
                height: dp(24)
                font_size: "13sp"
                color: (0.58, 0.64, 0.74, 1)
                halign: "left"
                valign: "middle"
                text_size: self.size

        # =========================
        # 卡片 1: 文本哈希
        # =========================
        ModernCard:
            CardHeader:
                title_text: "文本哈希"

            ModernTextInput:
                id: input_text
                hint_text: "请输入需要计算哈希的文本……"
                multiline: True
                size_hint_y: None
                height: dp(140)
                font_size: "15sp"

        # =========================
        # 卡片 2: 文件哈希
        # =========================
        ModernCard:
            CardHeader:
                title_text: "文件哈希"

            BoxLayout:
                size_hint_y: None
                height: dp(44)
                padding: [dp(12), dp(4)]
                canvas.before:
                    Color:
                        rgba: (0.059, 0.090, 0.165, 1)
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(8)]
                    Color:
                        rgba: (0.200, 0.255, 0.333, 0.8)
                    Line:
                        rounded_rectangle: [self.x, self.y, self.width, self.height, dp(8)]
                        width: dp(1)
                Label:
                    text: "📁 " + app.selected_file_name
                    color: (0.85, 0.90, 0.95, 1) if app.selected_file_name != "尚未选择文件" else (0.450, 0.520, 0.620, 1)
                    font_size: "14sp"
                    halign: "left"
                    valign: "middle"
                    text_size: self.size
                    shorten: True
                    shorten_from: "center"

            SecondaryBtn:
                text: "浏览选择文件"
                on_release: app.select_file()

        # =========================
        # 卡片 3: 哈希算法与计算
        # =========================
        ModernCard:
            CardHeader:
                title_text: "哈希算法"

            ModernSpinner:
                id: algorithm_spinner
                text: app.default_algorithm
                values: app.algorithm_names

            BoxLayout:
                size_hint_y: None
                height: dp(48)
                spacing: dp(10)

                PrimaryBtn:
                    text: "计算文本哈希"
                    on_release: app.generate_text_hash()

                PrimaryBtn:
                    text: "计算文件哈希"
                    on_release: app.generate_file_hash()

        # =========================
        # 卡片 4: 计算结果
        # =========================
        ModernCard:
            CardHeader:
                title_text: app.output_caption

            ResultTextInput:
                id: output_text
                readonly: True
                use_handles: True
                use_bubble: True
                unfocus_on_touch: True
                multiline: True
                size_hint_y: None
                height: dp(130)
                font_size: "14sp"

            BoxLayout:
                size_hint_y: None
                height: dp(46)
                spacing: dp(10)

                PrimaryBtn:
                    text: "复制结果"
                    height: dp(46)
                    on_release: app.copy_result()

                DangerBtn:
                    text: "清空"
                    on_release: app.clear_all()

        # =========================
        # 卡片 5: 文件完整性校验
        # =========================
        ModernCard:
            CardHeader:
                title_text: "文件完整性校验"

            ModernTextInput:
                id: expected_hash_input
                hint_text: "请输入官方或预期哈希值……"
                multiline: False
                size_hint_y: None
                height: dp(48)
                font_size: "14sp"

            SuccessBtn:
                text: "开始校验文件"
                on_release: app.verify_file_hash()

            BoxLayout:
                size_hint_y: None
                height: dp(46)
                padding: [dp(12), dp(4)]
                canvas.before:
                    Color:
                        rgba: (0.024, 0.235, 0.145, 0.9) if "✓" in app.verification_text else ((0.35, 0.08, 0.08, 0.9) if "✗" in app.verification_text else (0.059, 0.090, 0.165, 0.9))
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(8)]
                    Color:
                        rgba: (0.063, 0.725, 0.506, 0.8) if "✓" in app.verification_text else ((0.937, 0.267, 0.267, 0.8) if "✗" in app.verification_text else (0.200, 0.255, 0.333, 0.8))
                    Line:
                        rounded_rectangle: [self.x, self.y, self.width, self.height, dp(8)]
                        width: dp(1)
                Label:
                    text: app.verification_text
                    bold: True
                    font_size: "14sp"
                    color: (0.204, 0.827, 0.604, 1) if "✓" in app.verification_text else ((0.973, 0.443, 0.443, 1) if "✗" in app.verification_text else (0.580, 0.639, 0.722, 1))
                    halign: "center"
                    valign: "middle"
                    text_size: self.size

        # =========================
        # 底部状态与关于
        # =========================
        BoxLayout:
            size_hint_y: None
            height: max(dp(54), status_label.texture_size[1] + dp(16))
            padding: [dp(14), dp(8)]
            canvas.before:
                Color:
                    rgba: (0.059, 0.090, 0.165, 0.7)
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(8)]
                Color:
                    rgba: (0.200, 0.255, 0.333, 0.5)
                Line:
                    rounded_rectangle: [self.x, self.y, self.width, self.height, dp(8)]
                    width: dp(0.8)
            Label:
                id: status_label
                text: app.status_text
                color: (0.58, 0.64, 0.74, 1)
                halign: "left"
                valign: "middle"
                text_size: self.width, None
                font_size: "13sp"

        SecondaryBtn:
            text: "关于哈希工具"
            height: dp(44)
            on_release: app.show_about()
"""


class HashToolAndroidApp(App):
    FILE_PICKER_REQUEST = 5001

    app_version = StringProperty(APP_VERSION)
    default_algorithm = StringProperty(DEFAULT_ALGORITHM)
    algorithm_names = ListProperty(list(ALGORITHM_MAP))
    selected_file_name = StringProperty("尚未选择文件")
    output_caption = StringProperty(f"{DEFAULT_ALGORITHM} 哈希值")
    verification_text = StringProperty("校验结果：尚未校验")
    status_text = StringProperty("")

    def build(self):
        self.title = f"哈希工具 {APP_VERSION}"
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
            f"{name} 文本哈希值",
        )

    def select_file(self, *_):
        if platform != "android":
            self.show_message(
                "仅限 Android",
                "系统文件选择器仅在 Android 安装包中可用。",
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
            self.show_message("文件选择失败", str(error))

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
        self.verification_text = "校验结果：尚未校验"

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
            raise OSError("当前环境无法读取 Android 文件 URI")

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
                raise OSError("无法打开所选文件")
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
            self.show_message("文件读取失败", str(error))
            return

        name, _ = self.selected_algorithm()
        self.show_hash_result(result, f"{name} 文件哈希值")

    def verify_file_hash(self, *_):
        if not self.require_selected_file():
            return

        expected = self.expected_hash_input.text.strip()
        name, _ = self.selected_algorithm()

        if not expected:
            self.show_message(
                "缺少预期哈希值",
                "请先输入官方或预期哈希值。",
            )
            return

        required_length = HASH_LENGTHS[name]
        if len(expected) != required_length:
            self.show_message(
                "哈希长度不正确",
                f"{name} 的十六进制哈希值应包含 {required_length} 个字符；"
                f"当前输入 {len(expected)} 个字符。",
            )
            return

        try:
            int(expected, 16)
        except ValueError:
            self.show_message(
                "哈希格式不正确",
                "哈希值只能包含十六进制字符 0-9 和 A-F。",
            )
            return

        try:
            actual = self.calculate_selected_file_hash()
        except OSError as error:
            self.show_message("文件读取失败", str(error))
            return

        self.show_hash_result(actual, f"{name} 文件哈希值")
        self.verification_text = (
            "✓ 校验通过：哈希值一致"
            if actual.lower() == expected.lower()
            else "✗ 校验失败：哈希值不一致"
        )

    def require_selected_file(self):
        if self._selected_file_uri:
            return True

        self.show_message(
            "尚未选择文件",
            "请先选择需要计算或校验哈希值的文件。",
        )
        return False

    def show_hash_result(self, result, caption):
        self.output_text.text = result
        self.output_caption = caption
        self.update_status()

    def copy_result(self, *_):
        if not self.output_text.text:
            self.show_message(
                "没有可复制的内容",
                "请先计算一个哈希值。",
            )
            return
        Clipboard.copy(self.output_text.text)

    def clear_all(self, *_):
        self.input_text.text = ""
        self.output_text.text = ""
        self.algorithm_spinner.text = DEFAULT_ALGORITHM
        self.expected_hash_input.text = ""
        self.output_caption = f"{DEFAULT_ALGORITHM} 哈希值"
        self.verification_text = "校验结果：尚未校验"
        self.input_text.focus = False
        self.update_status()

    def update_status(self, *_):
        if not hasattr(self, "input_text"):
            return

        text = self.input_text.text
        self.status_text = (
            f"输入：{len(text)} 字符 / "
            f"{len(text.encode('utf-8'))} 字节\n"
            f"算法：{self.algorithm_spinner.text} | "
            f"输出：{len(self.output_text.text)} 字符"
        )

    def on_algorithm_changed(self, *_):
        self.verification_text = "校验结果：尚未校验"
        self.update_status()

    def on_expected_hash_changed(self, *_):
        self.verification_text = "校验结果：尚未校验"

    def show_about(self, *_):
        self.show_message(
            "关于哈希工具",
            "哈希工具\n\n"
            f"版本：{APP_VERSION}\n\n"
            "文本与文件哈希计算工具\n\n"
            f"作者：{APP_AUTHOR}\n\n"
            "支持算法：MD5、SHA-1、SHA-256、SHA-512",
            popup_height=330,
        )

    @staticmethod
    def show_message(title, message, popup_height=250):
        content_box = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=[dp(12), dp(10), dp(12), dp(6)],
        )
        msg_label = Label(
            text=message,
            font_name=FONT_PATH,
            halign="center",
            valign="middle",
            text_size=(dp(270), None),
            font_size="14sp",
            color=(0.92, 0.94, 0.97, 1),
        )
        content_box.add_widget(msg_label)

        close_btn = Button(
            text="确定",
            font_name=FONT_PATH,
            size_hint_y=None,
            height=dp(42),
            font_size="14sp",
            bold=True,
            color=(1, 1, 1, 1),
            background_color=(0.145, 0.514, 0.922, 1),
        )
        popup = Popup(
            title=title,
            title_font=FONT_PATH,
            title_size="16sp",
            title_align="center",
            content=content_box,
            size_hint=(0.88, None),
            height=dp(popup_height),
            separator_color=(0.231, 0.510, 0.965, 0.8),
        )
        close_btn.bind(on_release=popup.dismiss)
        content_box.add_widget(close_btn)
        popup.open()


if __name__ == "__main__":
    HashToolAndroidApp().run()
