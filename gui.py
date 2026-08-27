import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from config import (
    APP_NAME,
    APP_VERSION,
    APP_DESCRIPTION,
    APP_AUTHOR,
    ALGORITHM_MAP,
    HASH_LENGTHS,
    DEFAULT_ALGORITHM,
)

from hash_utils import (
    calculate_hash,
    calculate_file_hash,
)


class HashToolApp:
    """
    Hash Tool 图形界面。
    """

    def __init__(self, root: tk.Tk):
        self.root = root

        # =========================
        # 主窗口
        # =========================

        self.root.title(
            f"{APP_NAME} {APP_VERSION}"
        )

        icon_path = resource_path(
            "assets/icon.ico"
        )

        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        self.root.geometry("900x760")

        self.root.minsize(
            700,
            550
        )

        # =========================
        # GUI 状态变量
        # =========================

        self.selected_file_path = tk.StringVar(
            value="尚未选择文件"
        )

        self.algorithm_var = tk.StringVar(
            value=DEFAULT_ALGORITHM
        )

        self.expected_hash_var = tk.StringVar()

        self.verify_result_var = tk.StringVar(
            value="校验结果：尚未校验"
        )

        self.status_var = tk.StringVar()

        # =========================
        # 配置整体样式
        # =========================

        self.configure_styles()

        # =========================
        # 创建 GUI
        # =========================

        self.create_scrollable_page()

        self.create_header()

        self.create_input_area()

        self.create_file_area()

        self.create_algorithm_area()

        self.create_output_area()

        self.create_verify_area()

        self.create_action_buttons()

        self.create_status_bar()

        self.bind_events()

        # 初始化状态栏
        self.update_status()

        # 默认焦点
        self.input_text.focus_set()

    # =====================================================
    # 样式
    # =====================================================

    def configure_styles(self):
        self.style = ttk.Style()

        # Windows 上优先使用 vista 主题
        if "vista" in self.style.theme_names():
            self.style.theme_use("vista")

        # 软件主标题
        self.style.configure(
            "Title.TLabel",
            font=(
                "Microsoft YaHei UI",
                20,
                "bold"
            )
        )

        # 副标题
        self.style.configure(
            "Subtitle.TLabel",
            font=(
                "Microsoft YaHei UI",
                10
            )
        )

        # 区域标题
        self.style.configure(
            "Section.TLabelframe.Label",
            font=(
                "Microsoft YaHei UI",
                11,
                "bold"
            )
        )

        # 普通按钮
        self.style.configure(
            "TButton",
            font=(
                "Microsoft YaHei UI",
                10
            ),
            padding=(12, 6)
        )

        # 主要操作按钮
        self.style.configure(
            "Primary.TButton",
            font=(
                "Microsoft YaHei UI",
                10,
                "bold"
            ),
            padding=(16, 8)
        )

        # 普通标签
        self.style.configure(
            "TLabel",
            font=(
                "Microsoft YaHei UI",
                10
            )
        )

        # 状态栏
        self.style.configure(
            "Status.TLabel",
            font=(
                "Microsoft YaHei UI",
                9
            )
        )

        # 下拉框
        self.style.configure(
            "TCombobox",
            font=(
                "Microsoft YaHei UI",
                10
            )
        )

    # =====================================================
    # 页面整体滚动
    # =====================================================

    def create_scrollable_page(self):
        self.main_frame = ttk.Frame(
            self.root
        )

        self.main_frame.pack(
            fill="both",
            expand=True
        )

        self.canvas = tk.Canvas(
            self.main_frame,
            highlightthickness=0
        )

        self.canvas.pack(
            side=tk.LEFT,
            fill="both",
            expand=True
        )

        self.page_scrollbar = ttk.Scrollbar(
            self.main_frame,
            orient="vertical",
            command=self.canvas.yview
        )

        self.page_scrollbar.pack(
            side=tk.RIGHT,
            fill="y"
        )

        self.canvas.configure(
            yscrollcommand=self.page_scrollbar.set
        )

        self.content_frame = ttk.Frame(
            self.canvas
        )

        self.content_window = (
            self.canvas.create_window(
                (0, 0),
                window=self.content_frame,
                anchor="nw"
            )
        )

        self.content_frame.bind(
            "<Configure>",
            self.update_scroll_region
        )

        self.canvas.bind(
            "<Configure>",
            self.resize_content_frame
        )

        self.canvas.bind_all(
            "<MouseWheel>",
            self.on_mousewheel
        )

    def update_scroll_region(
        self,
        event=None
    ):
        self.canvas.configure(
            scrollregion=self.canvas.bbox(
                "all"
            )
        )

    def resize_content_frame(
        self,
        event
    ):
        self.canvas.itemconfigure(
            self.content_window,
            width=event.width
        )

    def on_mousewheel(
        self,
        event
    ):
        # 如果鼠标位于 Text 文本框上，
        # 让 Text 自己处理滚轮事件，
        # 不滚动整个页面
        if isinstance(event.widget, tk.Text):
            return

        # 其他位置滚动整个页面
        self.canvas.yview_scroll(
            int(
                -1 * (
                    event.delta / 120
                )
            ),
            "units"
        )

    # =====================================================
    # 顶部标题
    # =====================================================

    def create_header(self):
        header_frame = ttk.Frame(
            self.content_frame
        )

        header_frame.pack(
            fill="x",
            padx=50,
            pady=(30, 20)
        )

        title_label = ttk.Label(
            header_frame,
            text=APP_NAME,
            style="Title.TLabel"
        )

        title_label.pack(
            anchor="w"
        )

        subtitle_label = ttk.Label(
            header_frame,
            text=APP_DESCRIPTION,
            style="Subtitle.TLabel"
        )

        subtitle_label.pack(
            anchor="w",
            pady=(5, 0)
        )

    # =====================================================
    # 文本输入区域
    # =====================================================

    def create_input_area(self):
        section = ttk.LabelFrame(
            self.content_frame,
            text="文本哈希",
            style="Section.TLabelframe"
        )

        section.pack(
            fill="x",
            padx=50,
            pady=10
        )

        description = ttk.Label(
            section,
            text="输入需要计算哈希值的文本："
        )

        description.pack(
            anchor="w",
            padx=20,
            pady=(15, 8)
        )

        input_frame = ttk.Frame(
            section
        )

        input_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 15)
        )

        self.input_text = tk.Text(
            input_frame,
            height=7,
            wrap="word",
            font=(
                "Consolas",
                10
            ),
            undo=True
        )

        self.input_text.pack(
            side=tk.LEFT,
            fill="both",
            expand=True
        )

        input_scrollbar = ttk.Scrollbar(
            input_frame,
            orient="vertical",
            command=self.input_text.yview
        )

        input_scrollbar.pack(
            side=tk.RIGHT,
            fill="y"
        )

        self.input_text.config(
            yscrollcommand=input_scrollbar.set
        )

    # =====================================================
    # 文件区域
    # =====================================================

    def create_file_area(self):
        section = ttk.LabelFrame(
            self.content_frame,
            text="文件哈希",
            style="Section.TLabelframe"
        )

        section.pack(
            fill="x",
            padx=50,
            pady=10
        )

        description = ttk.Label(
            section,
            text="选择需要计算或校验哈希值的文件："
        )

        description.pack(
            anchor="w",
            padx=20,
            pady=(15, 8)
        )

        file_frame = ttk.Frame(
            section
        )

        file_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 15)
        )

        self.file_path_label = ttk.Label(
            file_frame,
            textvariable=self.selected_file_path,
            anchor="w"
        )

        self.file_path_label.pack(
            side=tk.LEFT,
            fill="x",
            expand=True
        )

        self.select_file_button = ttk.Button(
            file_frame,
            text="选择文件",
            command=self.select_file
        )

        self.select_file_button.pack(
            side=tk.RIGHT,
            padx=(15, 0)
        )

    # =====================================================
    # 算法与计算
    # =====================================================

    def create_algorithm_area(self):
        section = ttk.LabelFrame(
            self.content_frame,
            text="哈希算法",
            style="Section.TLabelframe"
        )

        section.pack(
            fill="x",
            padx=50,
            pady=10
        )

        algorithm_frame = ttk.Frame(
            section
        )

        algorithm_frame.pack(
            pady=(15, 10)
        )

        algorithm_label = ttk.Label(
            algorithm_frame,
            text="算法："
        )

        algorithm_label.pack(
            side=tk.LEFT,
            padx=(0, 8)
        )

        self.algorithm_box = ttk.Combobox(
            algorithm_frame,
            textvariable=self.algorithm_var,
            values=list(
                ALGORITHM_MAP.keys()
            ),
            state="readonly",
            width=18
        )

        self.algorithm_box.pack(
            side=tk.LEFT
        )

        button_frame = ttk.Frame(
            section
        )

        button_frame.pack(
            pady=(5, 15)
        )

        self.generate_button = ttk.Button(
            button_frame,
            text="计算文本哈希",
            command=self.generate_text_hash,
            style="Primary.TButton"
        )

        self.generate_button.pack(
            side=tk.LEFT,
            padx=8
        )

        self.generate_file_button = ttk.Button(
            button_frame,
            text="计算文件哈希",
            command=self.generate_file_hash,
            style="Primary.TButton"
        )

        self.generate_file_button.pack(
            side=tk.LEFT,
            padx=8
        )

    # =====================================================
    # 输出区域
    # =====================================================

    def create_output_area(self):
        section = ttk.LabelFrame(
            self.content_frame,
            text="计算结果",
            style="Section.TLabelframe"
        )

        section.pack(
            fill="x",
            padx=50,
            pady=10
        )

        self.output_label = ttk.Label(
            section,
            text=(
                f"{DEFAULT_ALGORITHM} "
                "哈希值："
            )
        )

        self.output_label.pack(
            anchor="w",
            padx=20,
            pady=(15, 8)
        )

        output_frame = ttk.Frame(
            section
        )

        output_frame.pack(
            fill="both",
            padx=20,
            pady=(0, 10)
        )

        self.output_text = tk.Text(
            output_frame,
            height=4,
            wrap="char",
            state="disabled",
            font=(
                "Consolas",
                10
            )
        )

        self.output_text.pack(
            side=tk.LEFT,
            fill="both",
            expand=True
        )

        output_scrollbar = ttk.Scrollbar(
            output_frame,
            orient="vertical",
            command=self.output_text.yview
        )

        output_scrollbar.pack(
            side=tk.RIGHT,
            fill="y"
        )

        self.output_text.config(
            yscrollcommand=(
                output_scrollbar.set
            )
        )

        result_button_frame = ttk.Frame(
            section
        )

        result_button_frame.pack(
            pady=(0, 15)
        )

        self.copy_button = ttk.Button(
            result_button_frame,
            text="复制结果",
            command=self.copy_result
        )

        self.copy_button.pack(
            side=tk.LEFT,
            padx=8
        )

        self.clear_button = ttk.Button(
            result_button_frame,
            text="清空",
            command=self.clear_all
        )

        self.clear_button.pack(
            side=tk.LEFT,
            padx=8
        )

    # =====================================================
    # 哈希校验区域
    # =====================================================

    def create_verify_area(self):
        section = ttk.LabelFrame(
            self.content_frame,
            text="文件完整性校验",
            style="Section.TLabelframe"
        )

        section.pack(
            fill="x",
            padx=50,
            pady=10
        )

        description = ttk.Label(
            section,
            text=(
                "输入官方或可信来源提供的"
                "预期哈希值："
            )
        )

        description.pack(
            anchor="w",
            padx=20,
            pady=(15, 8)
        )

        self.expected_hash_entry = ttk.Entry(
            section,
            textvariable=self.expected_hash_var
        )

        self.expected_hash_entry.pack(
            fill="x",
            padx=20,
            pady=(0, 10)
        )

        self.verify_button = ttk.Button(
            section,
            text="校验文件",
            command=self.verify_file_hash,
            style="Primary.TButton"
        )

        self.verify_button.pack(
            pady=8
        )

        self.verify_result_label = ttk.Label(
            section,
            textvariable=self.verify_result_var
        )

        self.verify_result_label.pack(
            pady=(5, 15)
        )

    # =====================================================
    # 操作按钮区域
    # =====================================================

    def create_action_buttons(self):
        """
        目前复制与清空按钮已经放在结果区域。

        保留这个方法，方便以后继续加入
        全局操作按钮。
        """
        pass

    # =====================================================
    # 状态栏
    # =====================================================

    def create_status_bar(self):
        separator = ttk.Separator(
            self.content_frame,
            orient="horizontal"
        )

        separator.pack(
            fill="x",
            padx=50,
            pady=(15, 8)
        )

        bottom_frame = ttk.Frame(
            self.content_frame
        )

        bottom_frame.pack(
            fill="x",
            padx=50,
            pady=(0, 25)
        )

        self.status_label = ttk.Label(
            bottom_frame,
            textvariable=self.status_var,
            style="Status.TLabel",
            anchor="w"
        )

        self.status_label.pack(
            side=tk.LEFT,
            fill="x",
            expand=True
        )

        about_button = ttk.Button(
            bottom_frame,
            text="关于",
            command=self.show_about
        )

        about_button.pack(
            side=tk.RIGHT
        )

    # =====================================================
    # 事件绑定
    # =====================================================

    def bind_events(self):
        self.input_text.bind(
            "<<Modified>>",
            self.on_input_modified
        )

        self.algorithm_box.bind(
            "<<ComboboxSelected>>",
            self.on_algorithm_changed
        )

        self.expected_hash_var.trace_add(
            "write",
            self.on_expected_hash_changed
        )

        self.input_text.edit_modified(
            False
        )

    # =====================================================
    # 文本哈希
    # =====================================================

    def generate_text_hash(self):
        text = self.input_text.get(
            "1.0",
            "end-1c"
        )

        selected_algorithm = (
            self.algorithm_var.get()
        )

        algorithm = ALGORITHM_MAP[
            selected_algorithm
        ]

        result = calculate_hash(
            text,
            algorithm
        )

        self.show_hash_result(
            result,
            f"{selected_algorithm} 哈希值："
        )

    # =====================================================
    # 选择文件
    # =====================================================

    def select_file(self):
        file_path = (
            filedialog.askopenfilename(
                title="选择要计算哈希的文件"
            )
        )

        if not file_path:
            return

        self.selected_file_path.set(
            file_path
        )

        self.verify_result_var.set(
            "校验结果：尚未校验"
        )

    # =====================================================
    # 文件哈希
    # =====================================================

    def generate_file_hash(self):
        file_path = (
            self.selected_file_path.get()
        )

        if file_path == "尚未选择文件":
            messagebox.showwarning(
                "尚未选择文件",
                "请先选择需要计算哈希值的文件。"
            )
            return

        selected_algorithm = (
            self.algorithm_var.get()
        )

        algorithm = ALGORITHM_MAP[
            selected_algorithm
        ]

        try:
            result = calculate_file_hash(
                file_path,
                algorithm
            )

        except FileNotFoundError:
            messagebox.showerror(
                "文件不存在",
                "找不到该文件。\n\n"
                "文件可能已经被移动、"
                "重命名或删除。"
            )
            return

        except PermissionError:
            messagebox.showerror(
                "无法读取文件",
                "没有权限读取该文件。"
            )
            return

        except OSError as error:
            messagebox.showerror(
                "文件读取失败",
                f"读取文件时发生错误："
                f"\n\n{error}"
            )
            return

        self.show_hash_result(
            result,
            f"{selected_algorithm} "
            "文件哈希值："
        )

    # =====================================================
    # 文件校验
    # =====================================================

    def verify_file_hash(self):
        file_path = (
            self.selected_file_path.get()
        )

        if file_path == "尚未选择文件":
            messagebox.showwarning(
                "尚未选择文件",
                "请先选择需要校验的文件。"
            )
            return

        expected_hash = (
            self.expected_hash_var
            .get()
            .strip()
        )

        if not expected_hash:
            messagebox.showwarning(
                "缺少预期哈希值",
                "请输入官方 / 预期哈希值。"
            )
            return

        selected_algorithm = (
            self.algorithm_var.get()
        )

        required_length = HASH_LENGTHS[
            selected_algorithm
        ]

        if (
            len(expected_hash)
            != required_length
        ):
            messagebox.showwarning(
                "哈希长度不正确",
                f"{selected_algorithm} "
                f"的十六进制哈希值"
                f"应当包含 "
                f"{required_length} 个字符。"
                f"\n\n当前输入："
                f"{len(expected_hash)} 个字符。"
            )
            return

        try:
            int(expected_hash, 16)

        except ValueError:
            messagebox.showwarning(
                "哈希格式不正确",
                "哈希值只能包含"
                "十六进制字符：0-9、A-F。"
            )
            return

        algorithm = ALGORITHM_MAP[
            selected_algorithm
        ]

        try:
            actual_hash = (
                calculate_file_hash(
                    file_path,
                    algorithm
                )
            )

        except FileNotFoundError:
            messagebox.showerror(
                "文件不存在",
                "找不到该文件。\n\n"
                "文件可能已经被移动、"
                "重命名或删除。"
            )
            return

        except PermissionError:
            messagebox.showerror(
                "无法读取文件",
                "没有权限读取该文件。"
            )
            return

        except OSError as error:
            messagebox.showerror(
                "文件读取失败",
                f"读取文件时发生错误："
                f"\n\n{error}"
            )
            return

        self.show_hash_result(
            actual_hash,
            f"{selected_algorithm} "
            "文件哈希值："
        )

        if (
            actual_hash.lower()
            == expected_hash.lower()
        ):
            self.verify_result_var.set(
                "✓ 校验通过：哈希值一致"
            )

        else:
            self.verify_result_var.set(
                "✗ 校验失败：哈希值不一致"
            )

    # =====================================================
    # 统一显示结果
    # =====================================================

    def show_hash_result(
        self,
        result: str,
        label_text: str
    ):
        self.output_text.config(
            state="normal"
        )

        self.output_text.delete(
            "1.0",
            tk.END
        )

        self.output_text.insert(
            "1.0",
            result
        )

        self.output_text.config(
            state="disabled"
        )

        self.output_label.config(
            text=label_text
        )

        self.update_status()

    # =====================================================
    # 复制
    # =====================================================

    def copy_result(self):
        result = self.output_text.get(
            "1.0",
            "end-1c"
        )

        if not result:
            messagebox.showwarning(
                "没有可复制的内容",
                "请先计算一个哈希值。"
            )
            return

        self.root.clipboard_clear()

        self.root.clipboard_append(
            result
        )

        self.root.update()

    # =====================================================
    # 清空
    # =====================================================

    def clear_all(self):
        self.input_text.delete(
            "1.0",
            tk.END
        )

        self.output_text.config(
            state="normal"
        )

        self.output_text.delete(
            "1.0",
            tk.END
        )

        self.output_text.config(
            state="disabled"
        )

        self.algorithm_var.set(
            DEFAULT_ALGORITHM
        )

        self.expected_hash_var.set("")

        self.verify_result_var.set(
            "校验结果：尚未校验"
        )

        self.output_label.config(
            text=(
                f"{DEFAULT_ALGORITHM} "
                "哈希值："
            )
        )

        self.input_text.focus_set()

        self.update_status()

    # =====================================================
    # 状态栏
    # =====================================================

    def update_status(self):
        text = self.input_text.get(
            "1.0",
            "end-1c"
        )

        char_count = len(text)

        byte_count = len(
            text.encode("utf-8")
        )

        selected_algorithm = (
            self.algorithm_var.get()
        )

        result = self.output_text.get(
            "1.0",
            "end-1c"
        )

        output_length = len(result)

        self.status_var.set(
            f"输入：{char_count} 字符 / "
            f"{byte_count} 字节"
            f"   |   算法："
            f"{selected_algorithm}"
            f"   |   输出："
            f"{output_length} 字符"
        )

    # =====================================================
    # GUI 事件
    # =====================================================

    def on_input_modified(
        self,
        event=None
    ):
        if self.input_text.edit_modified():
            self.update_status()

            self.input_text.edit_modified(
                False
            )

    def on_algorithm_changed(
        self,
        event=None
    ):
        self.verify_result_var.set(
            "校验结果：尚未校验"
        )

        self.update_status()

    def on_expected_hash_changed(
        self,
        *args
    ):
        self.verify_result_var.set(
            "校验结果：尚未校验"
        )

    def show_about(self):
        messagebox.showinfo(
            f"关于 {APP_NAME}",
            f"{APP_NAME}\n\n"
            f"版本：{APP_VERSION}\n\n"
            f"{APP_DESCRIPTION}\n\n"
            f"作者：{APP_AUTHOR}\n\n"
            "支持算法：MD5、SHA-1、SHA-256、SHA-512"
        )

def resource_path(relative_path: str) -> str:
    """
    获取资源文件的正确路径。

    开发环境和 PyInstaller 打包后的程序
    都可以使用。
    """

    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(
        base_path,
        relative_path
    )


def run_app():
    root = tk.Tk()

    HashToolApp(root)

    root.mainloop()