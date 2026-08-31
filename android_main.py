from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from config import (
    ALGORITHM_MAP,
    DEFAULT_ALGORITHM,
)

from hash_utils import calculate_hash


class HashToolAndroidApp(App):

    def build(self):
        # 软件标题
        self.title = "Hash Tool"

        # =========================
        # 整个页面滚动区域
        # =========================

        scroll_view = ScrollView()

        self.content = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(15),
            size_hint_y=None,
        )

        # content 的高度根据里面的控件自动增长
        self.content.bind(
            minimum_height=self.content.setter("height")
        )

        scroll_view.add_widget(self.content)

        # =========================
        # 软件标题
        # =========================

        title_label = Label(
            text="Hash Tool",
            font_size=dp(28),
            size_hint_y=None,
            height=dp(60),
        )

        self.content.add_widget(title_label)

        subtitle_label = Label(
            text="Text hash calculator",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(40),
        )

        self.content.add_widget(subtitle_label)

        # =========================
        # 文本输入
        # =========================

        input_label = Label(
            text="Text to hash",
            size_hint_y=None,
            height=dp(35),
        )

        self.content.add_widget(input_label)

        self.input_text = TextInput(
            multiline=True,
            hint_text="Enter text...",
            size_hint_y=None,
            height=dp(180),
            font_size=dp(16),
        )

        self.content.add_widget(
            self.input_text
        )

        # =========================
        # 算法选择
        # =========================

        algorithm_label = Label(
            text="Hash algorithm",
            size_hint_y=None,
            height=dp(35),
        )

        self.content.add_widget(
            algorithm_label
        )

        self.algorithm_spinner = Spinner(
            text=DEFAULT_ALGORITHM,
            values=list(
                ALGORITHM_MAP.keys()
            ),
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16),
        )

        self.content.add_widget(
            self.algorithm_spinner
        )

        # =========================
        # 计算按钮
        # =========================

        calculate_button = Button(
            text="Calculate hash",
            size_hint_y=None,
            height=dp(55),
            font_size=dp(17),
        )

        calculate_button.bind(
            on_press=self.generate_hash
        )

        self.content.add_widget(
            calculate_button
        )

        # =========================
        # 输出标题
        # =========================

        self.output_label = Label(
            text=f"{DEFAULT_ALGORITHM} digest",
            size_hint_y=None,
            height=dp(40),
        )

        self.content.add_widget(
            self.output_label
        )

        # =========================
        # 输出框
        # =========================

        self.output_text = TextInput(
            text="",
            multiline=True,
            readonly=True,
            size_hint_y=None,
            height=dp(150),
            font_size=dp(15),
        )

        self.content.add_widget(
            self.output_text
        )

        return scroll_view

    # =============================================
    # 计算文本哈希
    # =============================================

    def generate_hash(self, instance):
        # 获取用户输入
        text = self.input_text.text

        # 获取当前算法名称
        selected_algorithm = (
            self.algorithm_spinner.text
        )

        # GUI 名称 → hashlib 名称
        algorithm = ALGORITHM_MAP[
            selected_algorithm
        ]

        # 调用 Windows / Android 共用的后端函数
        result = calculate_hash(
            text,
            algorithm
        )

        # 显示结果
        self.output_text.text = result

        # 更新结果标题
        self.output_label.text = (
            f"{selected_algorithm} digest"
        )


if __name__ == "__main__":
    HashToolAndroidApp().run()
