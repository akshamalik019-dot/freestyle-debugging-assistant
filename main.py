import json
import os
import subprocess
import tempfile
from datetime import datetime

import tkinter as tk
from tkinter import ttk

try:
    import cv2
    from PIL import Image, ImageTk
except Exception:
    cv2 = None
    Image = None
    ImageTk = None

try:
    from google import genai
except Exception:
    genai = None


class DebugrApp:
    def __init__(self, root):
        self.root = root
        self.root.title("< debugr /> - synthwave terminal")
        self.root.geometry("1320x840")
        self.root.minsize(980, 640)

        self.history_file = "debugr_history.json"
        self.video_path = r"c:\Users\Dell\OneDrive\Documents\Video Project 11.mp4"
        self.cap = None
        self.video_loop_id = None
        self.photo = None
        self.video_image_id = None
        self.saved_sessions = []

        self.themes = {
            "Synthwave Terminal": {
                "bg_main": "#071108",
                "panel_bg": "#0d1c10",
                "accent": "#f6d365",
                "accent_alt": "#fff1a8",
                "text_main": "#fff6c7",
                "text_muted": "#a59a65",
                "border": "#24432a",
                "font_title": ("Consolas", 28, "bold"),
                "font_body": ("Consolas", 11),
                "insert_color": "#f6d365",
                "trace_fg": "#fff1a8",
                "gold": "#f6d365",
                "btn_primary_bg": "#f6d365",
                "btn_primary_fg": "#071108",
                "btn_secondary_bg": "#24432a",
                "btn_secondary_fg": "#fff1a8",
                "pip_colors": ["#f6d365", "#fff1a8", "#7fa36d", "#f6d365"],
                "lbl_colors": ["#f6d365", "#fff1a8", "#7fa36d", "#f6d365"],
            },
            "Deep Space IDE": {
                "bg_main": "#040810",
                "panel_bg": "#07101e",
                "accent": "#3d9bff",
                "accent_alt": "#b44dff",
                "text_main": "#c8dcff",
                "text_muted": "#6c7fa8",
                "border": "#0d1830",
                "font_title": ("Consolas", 28, "bold"),
                "font_body": ("Consolas", 11),
                "insert_color": "#3d9bff",
                "trace_fg": "#3d9bff",
                "gold": "#b44dff",
                "btn_primary_bg": "#3d9bff",
                "btn_primary_fg": "#040810",
                "btn_secondary_bg": "#0d1830",
                "btn_secondary_fg": "#9aadd8",
                "pip_colors": ["#3d9bff", "#b44dff", "#3d9bff", "#b44dff"],
                "lbl_colors": ["#3d9bff", "#b44dff", "#3d9bff", "#b44dff"],
            },
            "Emerald Void": {
                "bg_main": "#030e06",
                "panel_bg": "#06180a",
                "accent": "#00e676",
                "accent_alt": "#1de9b6",
                "text_main": "#d0f0e0",
                "text_muted": "#65a880",
                "border": "#0a2a14",
                "font_title": ("Consolas", 28, "bold"),
                "font_body": ("Consolas", 11),
                "insert_color": "#00e676",
                "trace_fg": "#00e676",
                "gold": "#1de9b6",
                "btn_primary_bg": "#00e676",
                "btn_primary_fg": "#030e06",
                "btn_secondary_bg": "#0a2a14",
                "btn_secondary_fg": "#82c89a",
                "pip_colors": ["#00e676", "#1de9b6", "#00e676", "#1de9b6"],
                "lbl_colors": ["#00e676", "#1de9b6", "#00e676", "#1de9b6"],
            },
        }
        self.current_theme_name = "Synthwave Terminal"
        self.t = self.themes[self.current_theme_name]

        self.ai_client = None
        if genai is not None:
            try:
                self.ai_client = genai.Client()
            except Exception:
                self.ai_client = None

        self.templates = {
            "Python": "def compute():\n    x = 10\n    y = 0\n    return x / y\n\nprint(compute())",
            "JavaScript": "function compute() {\n    let x = 10;\n    let y = undefined_variable;\n    return x;\n}\n\nconsole.log(compute());",
            "Java": "public class Main {\n    public static void main(String[] args) {\n        int[] arr = {1, 2};\n        System.out.println(arr[5]);\n    }\n}",
            "C++": "#include <iostream>\nusing namespace std;\n\nint main() {\n    int* ptr = nullptr;\n    *ptr = 42;\n    return 0;\n}",
        }

        self.main_container = tk.Frame(self.root, bg=self.t["bg_main"])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.build_splash_screen()

    def build_splash_screen(self):
        self.splash_frame = tk.Frame(self.main_container, bg=self.t["bg_main"])
        self.splash_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.splash_frame, bg=self.t["bg_main"], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_splash_resize)

        self.launch_btn = tk.Button(
            self.splash_frame,
            text="LET'S DEBUG",
            font=("Consolas", 14, "bold"),
            bg=self.t["accent"],
            fg=self.t["bg_main"],
            activebackground=self.t["accent_alt"],
            activeforeground=self.t["bg_main"],
            bd=0,
            padx=40,
            pady=16,
            cursor="hand2",
            command=self.transition_to_workspace,
        )
        self.launch_btn.bind("<Enter>", lambda _event: self.launch_btn.config(bg=self.t["accent_alt"]))
        self.launch_btn.bind("<Leave>", lambda _event: self.launch_btn.config(bg=self.t["accent"]))
        self.launch_btn.place(relx=0.5, rely=0.75, anchor=tk.CENTER)
        self.launch_btn.lift()

        if cv2 is not None and Image is not None and ImageTk is not None and os.path.exists(self.video_path):
            self.cap = cv2.VideoCapture(self.video_path)
            if self.cap.isOpened():
                self.stream_video()
                return

        self.draw_static_splash()

    def draw_static_splash(self):
        w = max(self.canvas.winfo_width(), 900)
        h = max(self.canvas.winfo_height(), 600)
        self.canvas.delete("all")
        self.canvas.create_text(
            w // 2,
            int(h * 0.38),
            text="debugr",
            fill=self.t["text_main"],
            font=("Consolas", 72, "bold"),
            tags="fallback",
        )
        self.canvas.create_text(
            w // 2,
            int(h * 0.50),
            text="compiler / runtime / ai diagnostics",
            fill=self.t["accent_alt"],
            font=("Consolas", 13),
            tags="fallback",
        )
        self.launch_btn.place(relx=0.5, rely=0.68, anchor=tk.CENTER)
        self.launch_btn.lift()
        self.canvas.bind("<Configure>", self.on_splash_resize)

    def on_splash_resize(self, _event):
        if self.cap is None:
            self.draw_static_splash()

    def stream_video(self):
        if self.cap is None:
            self.draw_static_splash()
            return

        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        if ret and canvas_w > 10 and canvas_h > 10:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = img.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(image=img)
            if self.video_image_id is None:
                self.video_image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            else:
                self.canvas.itemconfig(self.video_image_id, image=self.photo)
            self.launch_btn.place(relx=0.5, rely=0.75, anchor=tk.CENTER)
            self.launch_btn.lift()

        self.video_loop_id = self.root.after(25, self.stream_video)

    def transition_to_workspace(self):
        self.launch_btn.config(state=tk.DISABLED)

        if self.video_loop_id is not None:
            try:
                self.root.after_cancel(self.video_loop_id)
            except tk.TclError:
                pass
            self.video_loop_id = None
        if self.cap is not None:
            self.cap.release()
            self.cap = None

        self.canvas.delete("all")
        self.splash_frame.destroy()

        self.build_ui_layout()
        self.apply_theme_styles()
        self.handle_language_change()
        self.load_history_from_file()
        self.root.update_idletasks()

    def build_ui_layout(self):
        self.top_canvas = tk.Canvas(self.main_container, height=4, bd=0, highlightthickness=0)
        self.top_canvas.pack(fill=tk.X, side=tk.TOP)
        self.top_canvas.bind("<Configure>", lambda _event: self._redraw_gradient())

        self.header = tk.Frame(self.main_container)
        self.header.pack(fill=tk.X, padx=28, pady=(20, 6))

        self._brand_frame = tk.Frame(self.header)
        self._brand_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.title_lbl = tk.Label(self._brand_frame, text="< debugr />")
        self.title_lbl.pack(side=tk.LEFT, anchor=tk.W)

        self.subtitle_lbl = tk.Label(
            self._brand_frame,
            text="   // compiler - runtime - ai diagnostics",
            font=("Consolas", 9),
        )
        self.subtitle_lbl.pack(side=tk.LEFT, padx=(6, 0), pady=10, anchor=tk.W)

        self._drop_bar = tk.Frame(self.header)
        self._drop_bar.pack(side=tk.RIGHT, pady=4)

        self.theme_box = ttk.Combobox(
            self._drop_bar, values=list(self.themes.keys()), state="readonly", width=20
        )
        self.theme_box.set(self.current_theme_name)
        self.theme_box.pack(side=tk.RIGHT, padx=(8, 0))
        self.theme_box.bind("<<ComboboxSelected>>", self.switch_theme_trigger)

        self.lang_box = ttk.Combobox(
            self._drop_bar,
            values=["Python", "JavaScript", "Java", "C++"],
            state="readonly",
            width=13,
        )
        self.lang_box.set("Python")
        self.lang_box.pack(side=tk.RIGHT, padx=8)
        self.lang_box.bind("<<ComboboxSelected>>", lambda _event: self.handle_language_change())

        self.header_sep = tk.Frame(self.main_container, height=1)
        self.header_sep.pack(fill=tk.X)

        self.status_bar = tk.Frame(self.main_container, height=28)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)

        self._sb_left = tk.Frame(self.status_bar)
        self._sb_left.pack(side=tk.LEFT, fill=tk.Y)
        self._sb_dot = tk.Frame(self._sb_left, width=8, height=8)
        self._sb_dot.pack(side=tk.LEFT, padx=(14, 6), pady=10)
        self._sb_dot.pack_propagate(False)
        self._sb_lang_lbl = tk.Label(self._sb_left, text="< PYTHON />", font=("Consolas", 8, "bold"))
        self._sb_lang_lbl.pack(side=tk.LEFT, pady=7)
        self._sb_mid = tk.Label(self.status_bar, text="  -  debugr v2.0  -  ", font=("Consolas", 8))
        self._sb_mid.pack(side=tk.LEFT, pady=7)
        self._sb_right = tk.Frame(self.status_bar)
        self._sb_right.pack(side=tk.RIGHT, fill=tk.Y)
        self._sb_ready_lbl = tk.Label(self._sb_right, text="READY  ", font=("Consolas", 8))
        self._sb_ready_lbl.pack(side=tk.RIGHT, pady=7)

        self.workspace = tk.Frame(self.main_container)
        self.workspace.pack(fill=tk.BOTH, expand=True, padx=28, pady=(14, 6))

        self.left_col = tk.Frame(self.workspace)
        self.left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.editor_tab_bar = tk.Frame(self.left_col)
        self.editor_tab_bar.pack(fill=tk.X)
        self.editor_label = tk.Label(
            self.editor_tab_bar,
            text="  >  RUNTIME EDITOR",
            font=("Consolas", 8, "bold"),
            padx=14,
            pady=9,
            anchor=tk.W,
        )
        self.editor_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self._editor_status_dot = tk.Frame(self.editor_tab_bar, width=8, height=8)
        self._editor_status_dot.pack(side=tk.RIGHT, padx=(0, 14), pady=11)
        self._editor_status_dot.pack_propagate(False)

        self.editor_border = tk.Frame(self.left_col, bd=0)
        self.editor_border.pack(fill=tk.BOTH, expand=True)
        self._editor_inner = tk.Frame(self.editor_border)
        self._editor_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        self._ed_vscroll = tk.Scrollbar(self._editor_inner, orient=tk.VERTICAL, width=10)
        self._ed_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.code_editor = tk.Text(
            self._editor_inner,
            bd=0,
            padx=18,
            pady=16,
            font=self.t["font_body"],
            undo=True,
            relief=tk.FLAT,
            yscrollcommand=self._ed_vscroll.set,
            wrap=tk.NONE,
        )
        self.code_editor.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self._ed_vscroll.config(command=self.code_editor.yview)

        self.right_col = tk.Frame(self.workspace)
        self.right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self.btn_bar = tk.Frame(self.right_col)
        self.btn_bar.pack(fill=tk.X, pady=(0, 14))
        self.run_btn = tk.Button(
            self.btn_bar,
            text="> EXECUTE",
            font=("Consolas", 10, "bold"),
            bd=0,
            relief=tk.FLAT,
            padx=22,
            pady=10,
            cursor="hand2",
            command=self.execute_user_code,
        )
        self.run_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.clear_btn = tk.Button(
            self.btn_bar,
            text="CLEAR",
            font=("Consolas", 10),
            bd=0,
            relief=tk.FLAT,
            padx=22,
            pady=10,
            cursor="hand2",
            command=self.clear_output_panels,
        )
        self.clear_btn.pack(side=tk.LEFT)

        self._panel_pips = []
        self._panel_lbl_rows = []

        self.v_lbl, v_wrap = self.create_panel_slot(self.right_col, "RUNTIME SCOPE", "#")
        self.var_table = ttk.Treeview(v_wrap, columns=("Variable", "Value"), show="headings", height=2)
        self.var_table.heading("Variable", text="Token")
        self.var_table.heading("Value", text="Resolved Value")
        self.var_table.pack(fill=tk.X)

        self.t_lbl, t_wrap = self.create_panel_slot(self.right_col, "STDOUT / STDERR", ">")
        self.trace_banner = tk.Text(t_wrap, font=("Consolas", 10), height=3, bd=0, padx=12, pady=10)
        self.trace_banner.pack(fill=tk.X)

        self.ai_lbl, ai_wrap = self.create_panel_slot(self.right_col, "GEMINI NEURAL ANALYSIS", "*")
        self.ai_panel = tk.Text(ai_wrap, font=("Consolas", 9), height=4, bd=0, padx=12, pady=10, wrap=tk.WORD)
        self.ai_panel.pack(fill=tk.X)

        self.h_lbl, h_wrap = self.create_panel_slot(self.right_col, "EXECUTION ARCHIVE", "@")
        self.history_feed = tk.Listbox(h_wrap, font=("Consolas", 9), height=3, bd=0, relief=tk.FLAT)
        self.history_feed.pack(fill=tk.BOTH, expand=True)
        self.history_feed.bind("<<ListboxSelect>>", self.load_selected_history_item)

    def create_panel_slot(self, parent, title, icon):
        lbl_row = tk.Frame(parent)
        lbl_row.pack(fill=tk.X, pady=(10, 0))
        self._panel_lbl_rows.append(lbl_row)

        pip = tk.Frame(lbl_row, width=3)
        pip.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        pip.pack_propagate(False)
        self._panel_pips.append(pip)

        lbl = tk.Label(lbl_row, text=f"{icon}  {title}", font=("Consolas", 8, "bold"))
        lbl.pack(side=tk.LEFT, anchor=tk.W, pady=4)

        wrap_box = tk.Frame(parent, bd=0, padx=1, pady=1)
        wrap_box.pack(fill=tk.X, pady=(2, 0))
        return lbl, wrap_box

    def _redraw_gradient(self):
        t = self.t
        w = self.top_canvas.winfo_width()
        if w < 2:
            return
        self.top_canvas.delete("all")
        c1, c2 = t["accent"], t["accent_alt"]
        try:
            r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
            r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
        except (ValueError, IndexError):
            return
        steps = 80
        for i in range(steps):
            ratio = i / steps
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            x1 = int(i * w / steps)
            x2 = int((i + 1) * w / steps) + 1
            self.top_canvas.create_rectangle(x1, 0, x2, 4, fill=f"#{r:02x}{g:02x}{b:02x}", outline="")

    def apply_theme_styles(self):
        self.t = self.themes[self.current_theme_name]
        t = self.t

        for widget in [
            self.root,
            self.main_container,
            self.header,
            self.workspace,
            self.left_col,
            self.right_col,
            self.btn_bar,
            self._brand_frame,
            self._drop_bar,
        ]:
            widget.configure(bg=t["bg_main"])

        self.top_canvas.configure(bg=t["bg_main"])
        self._redraw_gradient()
        self.header_sep.configure(bg=t["border"])

        self.title_lbl.config(font=t["font_title"], fg=t["accent"], bg=t["bg_main"])
        self.subtitle_lbl.config(fg=t["text_muted"], bg=t["bg_main"], font=("Consolas", 9))

        self.editor_tab_bar.configure(bg=t["panel_bg"])
        self.editor_label.config(fg=t["accent_alt"], bg=t["panel_bg"], font=("Consolas", 8, "bold"))
        self._editor_status_dot.configure(bg=t["accent"])
        self.editor_border.config(bg=t["border"])
        self._editor_inner.config(bg=t["panel_bg"])
        self.code_editor.config(
            bg=t["panel_bg"],
            fg=t["text_main"],
            insertbackground=t["insert_color"],
            selectbackground=t["accent"],
            selectforeground=t["bg_main"],
        )
        self._ed_vscroll.config(
            bg=t["border"],
            troughcolor=t["bg_main"],
            activebackground=t["accent"],
            relief=tk.FLAT,
            bd=0,
            elementborderwidth=0,
        )

        lbl_colors = t.get("lbl_colors", [t["accent"]] * 4)
        for lbl, color in zip([self.v_lbl, self.t_lbl, self.ai_lbl, self.h_lbl], lbl_colors):
            lbl.config(fg=color, bg=t["bg_main"])
        for row in self._panel_lbl_rows:
            row.configure(bg=t["bg_main"])
        pip_colors = t.get("pip_colors", [t["accent"]] * 4)
        for pip, color in zip(self._panel_pips, pip_colors):
            pip.configure(bg=color)

        for wrap in [self.trace_banner.master, self.ai_panel.master, self.history_feed.master, self.var_table.master]:
            wrap["background"] = t["border"]

        self.trace_banner.config(bg=t["panel_bg"], fg=t["trace_fg"])
        self.ai_panel.config(bg=t["panel_bg"], fg=t["text_main"])
        self.history_feed.config(
            bg=t["panel_bg"],
            fg=t["text_muted"],
            selectbackground=t["accent"],
            selectforeground=t["bg_main"],
        )

        run_bg = t.get("btn_primary_bg", t["accent"])
        run_fg = t.get("btn_primary_fg", t["bg_main"])
        clear_bg = t.get("btn_secondary_bg", t["panel_bg"])
        clear_fg = t.get("btn_secondary_fg", t["text_muted"])

        self.run_btn.config(bg=run_bg, fg=run_fg, activebackground=t["accent_alt"], activeforeground=t["bg_main"])
        self.clear_btn.config(bg=clear_bg, fg=clear_fg, activebackground=t["border"], activeforeground=t["text_main"])

        self.run_btn.bind("<Enter>", lambda _event: self.run_btn.config(bg=t["accent_alt"], fg=t["bg_main"]))
        self.run_btn.bind("<Leave>", lambda _event: self.run_btn.config(bg=run_bg, fg=run_fg))
        self.clear_btn.bind("<Enter>", lambda _event: self.clear_btn.config(bg=t["border"], fg=t["text_main"]))
        self.clear_btn.bind("<Leave>", lambda _event: self.clear_btn.config(bg=clear_bg, fg=clear_fg))

        style = ttk.Style()
        style.configure(
            "Treeview",
            background=t["panel_bg"],
            fieldbackground=t["panel_bg"],
            foreground=t["text_main"],
            rowheight=24,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=t["bg_main"],
            foreground=t.get("gold", t["accent_alt"]),
            font=("Consolas", 8, "bold"),
            relief="flat",
        )
        style.map("Treeview", background=[("selected", t["accent"])], foreground=[("selected", t["bg_main"])])
        style.configure(
            "TCombobox",
            fieldbackground=t["panel_bg"],
            background=t["border"],
            foreground=t["text_main"],
            arrowcolor=t["accent"],
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", t["panel_bg"])],
            selectbackground=[("readonly", t["panel_bg"])],
            selectforeground=[("readonly", t["text_main"])],
        )

        self.status_bar.configure(bg=t["border"])
        self._sb_left.configure(bg=t["border"])
        self._sb_right.configure(bg=t["border"])
        self._sb_dot.configure(bg=t["accent"])
        self._sb_mid.configure(bg=t["border"], fg=t["text_muted"])
        self._sb_lang_lbl.configure(bg=t["border"], fg=t["accent"])
        self._sb_ready_lbl.configure(bg=t["border"], fg=t["accent_alt"])

    def switch_theme_trigger(self, _event):
        self.current_theme_name = self.theme_box.get()
        self.apply_theme_styles()

    def handle_language_change(self):
        selected = self.lang_box.get()
        self._sb_lang_lbl.configure(text=f"< {selected.upper()} />")
        self.code_editor.delete("1.0", tk.END)
        self.code_editor.insert("1.0", self.templates.get(selected, ""))

    def clear_output_panels(self):
        self.trace_banner.delete("1.0", tk.END)
        self.ai_panel.delete("1.0", tk.END)
        for item in self.var_table.get_children():
            self.var_table.delete(item)

    def ask_gemini_agent(self, code_content, trace_output, language):
        if not self.ai_client:
            self.ai_panel.delete("1.0", tk.END)
            self.ai_panel.insert(
                "1.0",
                "Gemini is offline. Install google-genai and set your API key to enable AI diagnostics.",
            )
            return

        self.ai_panel.delete("1.0", tk.END)
        self.ai_panel.insert("1.0", "Analyzing crash structures with Gemini Engine...")
        self.root.update_idletasks()

        prompt = (
            "You are the intelligent diagnostic agent core of 'debugr'.\n"
            f"Target Language Space: {language}\n\n"
            f"--- SOURCE CODE ---\n{code_content}\n\n"
            f"--- RUNTIME LOGS / STACK TRACE ---\n{trace_output}\n\n"
            "Task: Briefly explain why this code crashed in 2 clear sentences, "
            "and provide a clear tip to fix it."
        )
        try:
            response = self.ai_client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            self.ai_panel.delete("1.0", tk.END)
            self.ai_panel.insert("1.0", response.text.strip())
        except Exception as exc:
            self.ai_panel.delete("1.0", tk.END)
            self.ai_panel.insert("1.0", f"Cognitive sync offline: {exc}")

    def save_session_to_history(self, language, code, status):
        timestamp = datetime.now().strftime("%H:%M")
        log_entry = {"timestamp": timestamp, "language": language, "code": code, "status": status}
        history_data = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as file:
                    history_data = json.load(file)
            except Exception:
                history_data = []
        history_data.insert(0, log_entry)
        with open(self.history_file, "w", encoding="utf-8") as file:
            json.dump(history_data, file, indent=4)
        self.load_history_from_file()

    def load_history_from_file(self):
        self.history_feed.delete(0, tk.END)
        if not os.path.exists(self.history_file):
            return
        try:
            with open(self.history_file, "r", encoding="utf-8") as file:
                self.saved_sessions = json.load(file)
            for item in self.saved_sessions:
                self.history_feed.insert(
                    tk.END,
                    f" [{item['timestamp']}] Workspace Session ({item['language']}) -> {item['status']}",
                )
        except Exception:
            self.saved_sessions = []

    def load_selected_history_item(self, event):
        indices = event.widget.curselection()
        if not indices:
            return
        index = indices[0]
        if index < len(self.saved_sessions):
            selected_item = self.saved_sessions[index]
            self.lang_box.set(selected_item["language"])
            self.code_editor.delete("1.0", tk.END)
            self.code_editor.insert("1.0", selected_item["code"])

    def execute_user_code(self):
        self.clear_output_panels()
        lang = self.lang_box.get()
        code = self.code_editor.get("1.0", tk.END).strip()
        status = "Pass"

        if not code:
            self.trace_banner.insert("1.0", "No source code to execute.")
            return

        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                result = self.run_code_for_language(lang, code, tmpdir)
                if result.returncode == 0:
                    trace_str = f"RUNTIME SUCCESSFUL:\n\n{result.stdout}"
                    self.trace_banner.insert("1.0", trace_str)
                    self.ai_panel.insert("1.0", "Core operating parameters optimal.")
                    self.var_table.insert("", tk.END, values=("exit_status", "PASS"))
                else:
                    status = "Fault"
                    trace_str = f"EXCEPTION LOGGED:\n\n{result.stderr or result.stdout}"
                    self.trace_banner.insert("1.0", trace_str)
                    self.var_table.insert("", tk.END, values=("exit_status", "FAULT"))
                    self.ask_gemini_agent(code, trace_str, lang)
            except subprocess.TimeoutExpired:
                status = "Timeout"
                self.trace_banner.insert("1.0", "PROCESS KILLED: 5s threshold exceeded.")
            except FileNotFoundError as exc:
                status = "Missing Tool"
                self.trace_banner.insert("1.0", f"Missing runtime/compiler: {exc.filename}")
            except Exception as exc:
                status = "Error"
                self.trace_banner.insert("1.0", f"APPLICATION ERROR: {exc}")

            self.save_session_to_history(lang, code, status)

    def run_code_for_language(self, lang, code, tmpdir):
        if lang == "Python":
            filepath = os.path.join(tmpdir, "script.py")
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(code)
            return subprocess.run(["python", filepath], capture_output=True, text=True, errors="ignore", timeout=5)

        if lang == "JavaScript":
            filepath = os.path.join(tmpdir, "script.js")
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(code)
            return subprocess.run(["node", filepath], capture_output=True, text=True, errors="ignore", timeout=5)

        if lang == "Java":
            filepath = os.path.join(tmpdir, "Main.java")
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(code)
            compile_res = subprocess.run(["javac", filepath], capture_output=True, text=True, errors="ignore", timeout=5)
            if compile_res.returncode != 0:
                return compile_res
            return subprocess.run(["java", "-cp", tmpdir, "Main"], capture_output=True, text=True, errors="ignore", timeout=5)

        if lang == "C++":
            filepath = os.path.join(tmpdir, "main.cpp")
            exe_path = os.path.join(tmpdir, "main.exe" if os.name == "nt" else "main")
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(code)
            compile_res = subprocess.run(["g++", filepath, "-o", exe_path], capture_output=True, text=True, errors="ignore", timeout=5)
            if compile_res.returncode != 0:
                return compile_res
            return subprocess.run([exe_path], capture_output=True, text=True, errors="ignore", timeout=5)

        raise ValueError(f"Unsupported language: {lang}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DebugrApp(root)
    root.mainloop()





