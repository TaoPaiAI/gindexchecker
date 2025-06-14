import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk, Menu, filedialog
import csv
import requests
import json
import webbrowser
from datetime import datetime
import threading
import re
from utils import resource_path, TRANSLATIONS, load_config, save_config, set_app_icon
from spinner import Spinner

class ToolTip:
    def __init__(self, widget, text='widget info', delay=1000):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tipwindow = None
        self.id = None
        widget.bind("<Enter>", self.enter)
        widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.delay, self.showtip)

    def unschedule(self):
        _id = self.id
        self.id = None
        if _id:
            self.widget.after_cancel(_id)

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def showtip(self):
        if self.tipwindow or not self.text:
            return
        tip_text = self.text() if callable(self.text) else self.text
        x, y = self.widget.winfo_pointerxy()
        x += 10 
        y += 10  
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=tip_text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def filtrar_dominios(entrada):
    patron = re.compile(r'\b([a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\/[^\s]*)?)\b')
    dominios = patron.findall(entrada)
    unique_domains = list(dict.fromkeys(dominios))
    return "\n".join(unique_domains)

class GIndexCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GIndexChecker")
        set_app_icon(self.root)
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        self.api_keys_win = None
        self.cx_win = None
        self.help_doc_win = None
        self.help_about_win = None
        self.help_donations_win = None
        self.child_windows = []
        self.load_configuration()
        self.key_usage = {key: 0 for key in self.api_keys}
        self.current_api_key_index = 0
        self.full_results = {}
        self.invalid_cx_flag = False
        self.create_widgets()
        self.create_menu()

    def translate(self, key, **kwargs):
        return TRANSLATIONS[self.language].get(key, key).format(**kwargs)

    def load_configuration(self):
        config = load_config()
        self.api_keys = [key.strip() for key in config.get('API_KEYS', [])]
        self.cx = config.get('CX', '').strip()
        self.language = config.get('language', "es")

    def save_configuration(self):
        config = {'API_KEYS': self.api_keys, 'CX': self.cx, 'language': self.language}
        save_config(config)

    def validate_length(self, new_text):
        return len(new_text) <= 100

    def on_child_close(self, win, ref_attr):
        if win in self.child_windows:
            self.child_windows.remove(win)
        setattr(self, ref_attr, None)
        win.destroy()

    def add_context_menu(self, widget):
        context_menu = Menu(self.root, tearoff=0, bg='#3c3f41', fg='white')
        context_menu.add_command(label=self.translate("paste"), command=lambda: widget.event_generate("<<Paste>>"))
        widget.context_menu = context_menu
        def popup(event):
            widget.context_menu.tk_popup(event.x_root, event.y_root)
        widget.bind("<Button-3>", popup)
        widget.popup_context_menu = popup

    def create_widgets(self):
        bg_color = '#2d2d2d'
        fg_color = 'white'
        button_bg = 'white'
        button_fg = 'black'
        self.root.configure(bg=bg_color)

        self.domain_frame = tk.Frame(self.root, bg=bg_color)
        self.domain_frame.place(x=10, y=40)
        self.query_text = tk.Text(self.domain_frame, width=50, height=10,
                                  bg='#3c3f41', fg=fg_color, insertbackground=fg_color)
        self.query_text.pack(side="left", fill="both", expand=True)
        self.domain_scroll = tk.Scrollbar(self.domain_frame, orient="vertical")
        self.domain_scroll.pack(side="right", fill="y")
        self.query_text.config(yscrollcommand=self.domain_scroll.set)
        self.domain_scroll.config(command=self.query_text.yview)
        self.add_context_menu(self.query_text)

        self.filtrar_button = tk.Button(
            self.root, 
            text=self.translate("filter_domains"),
            command=self.filtrar_dominios_en_casilla,
            bg=button_bg, fg=button_fg, width=15, cursor="hand2"
        )
        self.filtrar_button.place(x=500, y=150)
        ToolTip(self.filtrar_button, lambda: self.translate("tooltip_filter"), delay=1000)

        self.query_label = ttk.Label(
            self.root, text=self.translate("domain_input"),
            background=bg_color, foreground=fg_color
        )
        self.query_label.place(x=10, y=10)

        self.search_button = tk.Button(
            self.root, text=self.translate("analyze_domains"),
            command=self.search, bg=button_bg, fg=button_fg,
            width=15, height=1, cursor="hand2"
        )
        self.search_button.place(x=500, y=90)
        ToolTip(self.search_button, lambda: self.translate("tooltip_search"), delay=1000)

        self.spinner = Spinner(self.root, text=self.translate("analyzing_text"))

        self.results_frame = tk.Frame(self.root, bg=bg_color)
        self.results_frame.place(x=10, y=220, width=500, height=350)
        self.results_text = tk.Text(
            self.results_frame, 
            bg='#3c3f41', 
            fg=fg_color,
            insertbackground=fg_color, 
            cursor="arrow",
            wrap="word"
        )
        self.results_text.grid(row=0, column=0, sticky="nsew")
        self.results_scroll = tk.Scrollbar(
            self.results_frame,
            orient="vertical",
            command=self.results_text.yview,
            width=16, bg="gray", activebackground="gray"
        )
        self.results_scroll.grid(row=0, column=1, sticky="ns")
        self.results_text.config(yscrollcommand=self.results_scroll.set)
        self.results_frame.grid_rowconfigure(0, weight=1)
        self.results_frame.grid_columnconfigure(0, weight=1)

        self.buttons_frame = tk.Frame(self.root, bg=bg_color)
        self.buttons_frame.place(x=520, y=220, width=160, height=350)
        self.copy_all_button = tk.Button(
            self.buttons_frame, text=self.translate("copy_all"),
            command=self.copy_all_domains, bg=button_bg, fg=button_fg,
            width=15, cursor="hand2"
        )
        self.copy_all_button.pack(pady=5)
        ToolTip(self.copy_all_button, lambda: self.translate("tooltip_copy_all"), delay=1000)
        self.copy_green_button = tk.Button(
            self.buttons_frame, text=self.translate("green").capitalize(),
            command=lambda: self.copy_domains("green"), bg="#00FF00",
            fg="black", width=15, cursor="hand2"
        )
        self.copy_green_button.pack(pady=5)
        ToolTip(self.copy_green_button, lambda: self.translate("tooltip_copy_green"), delay=1000)
        self.copy_yellow_button = tk.Button(
            self.buttons_frame, text=self.translate("yellow").capitalize(),
            command=lambda: self.copy_domains("yellow"), bg="yellow",
            fg="black", width=15, cursor="hand2"
        )
        self.copy_yellow_button.pack(pady=5)
        ToolTip(self.copy_yellow_button, lambda: self.translate("tooltip_copy_yellow"), delay=1000)
        self.copy_orange_button = tk.Button(
            self.buttons_frame, text=self.translate("orange").capitalize(),
            command=lambda: self.copy_domains("orange"), bg="#FF8C00",
            fg="black", width=15, cursor="hand2"
        )
        self.copy_orange_button.pack(pady=5)
        ToolTip(self.copy_orange_button, lambda: self.translate("tooltip_copy_orange"), delay=1000)
        self.export_csv_button = tk.Button(
            self.buttons_frame, text=self.translate("export_csv"),
            command=self.export_csv, bg=button_bg, fg=button_fg,
            width=15, cursor="hand2"
        )
        self.export_csv_button.pack(pady=5)
        ToolTip(self.export_csv_button, lambda: self.translate("tooltip_export_csv"), delay=1000)
        separator = ttk.Separator(self.buttons_frame, orient="horizontal")
        separator.pack(fill="x", pady=(15, 5))
        self.clear_results_button = tk.Button(
            self.buttons_frame, text=self.translate("clear_results"),
            command=self.clear_results, bg=button_bg, fg=button_fg,
            width=15, cursor="hand2"
        )
        self.clear_results_button.pack(pady=5)
        ToolTip(self.clear_results_button, lambda: self.translate("tooltip_clear_results"), delay=1000)

    def create_menu(self):
        menubar = Menu(self.root, bg='#2d2d2d', fg='white')
        self.root.config(menu=menubar)
        self.settings_menu = Menu(menubar, tearoff=0, bg='#3c3f41', fg='white')
        menubar.add_cascade(label=self.translate("config_menu_label"), menu=self.settings_menu)
        self.settings_menu.add_command(label=self.translate("change_language"), command=self.change_language)
        self.settings_menu.add_command(label=self.translate("api_keys"), command=self.api_keys_window)
        self.settings_menu.add_command(label=self.translate("cx"), command=self.cx_window)
        self.help_menu = Menu(menubar, tearoff=0, bg='#3c3f41', fg='white')
        menubar.add_cascade(label=self.translate("help_menu_label"), menu=self.help_menu)
        self.help_menu.add_command(label=self.translate("help_documentation"), command=self.show_help_documentation)
        self.help_menu.add_command(label=self.translate("help_about"), command=self.show_help_about)
        self.help_menu.add_command(label=self.translate("help_donations"), command=self.show_help_donations)

    def change_language(self):
        self.language = "en" if self.language == "es" else "es"
        self.update_ui_texts()
        self.create_menu()
        self.save_configuration()
        for win in self.child_windows:
            if hasattr(win, "update_ui_texts"):
                win.update_ui_texts()
        self.spinner.update_text(self.translate("analyzing_text"))

    def update_ui_texts(self):
        self.query_label.config(text=self.translate("domain_input"))
        self.search_button.config(text=self.translate("analyze_domains"))
        self.filtrar_button.config(text=self.translate("filter_domains"))
        self.copy_all_button.config(text=self.translate("copy_all"))
        self.copy_green_button.config(text=self.translate("green").capitalize())
        self.copy_yellow_button.config(text=self.translate("yellow").capitalize())
        self.copy_orange_button.config(text=self.translate("orange").capitalize())
        self.export_csv_button.config(text=self.translate("export_csv"))
        self.clear_results_button.config(text=self.translate("clear_results"))
        if hasattr(self.query_text, 'context_menu'):
            self.add_context_menu(self.query_text)

    def filtrar_dominios_en_casilla(self):
        entrada = self.query_text.get("1.0", tk.END).strip()
        dominios_filtrados = filtrar_dominios(entrada)
        self.query_text.delete("1.0", tk.END)
        self.query_text.insert(tk.END, dominios_filtrados)

    def api_keys_window(self):
        if self.api_keys_win is not None and self.api_keys_win.winfo_exists():
            self.api_keys_win.lift()
            return
        self.api_keys_win = tk.Toplevel(self.root)
        self.child_windows.append(self.api_keys_win)
        self.api_keys_win.title(self.translate("api_keys"))
        set_app_icon(self.api_keys_win)
        self.api_keys_win.geometry("600x665")
        self.api_keys_win.resizable(False, False)
        self.api_keys_win.configure(bg='#2d2d2d')

        tree_frame = tk.Frame(self.api_keys_win, bg='#2d2d2d')
        tree_frame.pack(padx=10, pady=10, fill="x")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#3c3f41", fieldbackground="#3c3f41", foreground="white")
        self.api_tree = ttk.Treeview(tree_frame, columns=("API Key", "Status"), show="headings", height=5)
        self.api_tree.heading("API Key", text="API Key")
        self.api_tree.heading("Status", text=self.translate("status"))
        self.api_tree.column("API Key", width=350)
        self.api_tree.column("Status", width=100)
        self.api_tree.pack(side=tk.LEFT, fill="x", expand=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.api_tree.yview)
        self.api_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        for key in self.api_keys:
            self.api_tree.insert("", tk.END, values=(key, ""))
        self.api_paste_label = ttk.Label(self.api_keys_win, text=self.translate("paste_api_key_here"),
                                          background='#2d2d2d', foreground='white')
        self.api_paste_label.pack(padx=10, pady=(10,0))
        vcmd = (self.api_keys_win.register(self.validate_length), '%P')
        self.api_keys_entry = tk.Entry(self.api_keys_win, width=50, bg='#3c3f41', fg='white',
                                       insertbackground='white', validate="key", validatecommand=vcmd)
        self.api_keys_entry.pack(padx=10, pady=5)
        self.add_context_menu(self.api_keys_entry)
        btn_frame = tk.Frame(self.api_keys_win, bg='#2d2d2d')
        btn_frame.pack(padx=10, pady=5)
        self.add_button = ttk.Button(btn_frame, text=self.translate("add_api_key_button"),
                                     command=self.add_api_key, cursor="hand2")
        self.add_button.grid(row=0, column=0, padx=5)
        self.delete_button = ttk.Button(btn_frame, text=self.translate("delete_api_key_button"),
                                        command=self.remove_selected_api_key, cursor="hand2")
        self.delete_button.grid(row=0, column=1, padx=5)
        self.verify_button = ttk.Button(btn_frame, text=self.translate("verify_api_keys_button"),
                                        command=self.verify_api_keys, cursor="hand2")
        self.verify_button.grid(row=0, column=2, padx=5)
        guide_frame = tk.Frame(self.api_keys_win, bg='#2d2d2d')
        guide_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.guide_text_widget = tk.Text(guide_frame, width=68, height=10, bg='#2d2d2d',
                                          fg='white', wrap='word', bd=0)
        self.guide_text_widget.pack(side=tk.LEFT, fill="both", expand=True)
        self.guide_text_widget.delete("1.0", tk.END)
        self.guide_text_widget.insert(tk.END, self.translate("api_guide"))
        if self.language == "es":
            anchor_text = "Consola de Google Cloud"
        else:
            anchor_text = "Google Cloud Console"
        self.guide_text_widget.config(state='normal')
        start_index = self.guide_text_widget.search(anchor_text, "1.0", tk.END)
        if start_index:
            end_index = f"{start_index}+{len(anchor_text)}c"
            self.guide_text_widget.tag_add("cloud", start_index, end_index)
            self.guide_text_widget.tag_config("cloud", foreground="#00FF00", underline=True)
            self.guide_text_widget.tag_bind("cloud", "<Enter>", lambda e: self.guide_text_widget.config(cursor="hand2"))
            self.guide_text_widget.tag_bind("cloud", "<Leave>", lambda e: self.guide_text_widget.config(cursor="arrow"))
            self.guide_text_widget.tag_bind("cloud", "<Button-1>", lambda e: webbrowser.open("https://console.cloud.google.com"))
        self.guide_text_widget.config(state='disabled')

        def update_ui():
            self.api_keys_win.title(self.translate("api_keys"))
            self.api_paste_label.config(text=self.translate("paste_api_key_here"))
            self.api_tree.heading("Status", text=self.translate("status"))
            self.add_button.config(text=self.translate("add_api_key_button"))
            self.delete_button.config(text=self.translate("delete_api_key_button"))
            self.verify_button.config(text=self.translate("verify_api_keys_button"))
            self.guide_text_widget.config(state='normal')
            self.guide_text_widget.delete("1.0", tk.END)
            self.guide_text_widget.insert(tk.END, self.translate("api_guide"))
            self.guide_text_widget.config(state='disabled')
            self.add_context_menu(self.api_keys_entry)
        self.api_keys_win.update_ui_texts = update_ui
        self.api_keys_win.protocol("WM_DELETE_WINDOW", lambda w=self.api_keys_win: self.on_child_close(w, "api_keys_win"))

    def add_api_key(self):
        key = self.api_keys_entry.get().strip()
        if key:
            self.api_keys.append(key)
            if key not in self.key_usage:
                self.key_usage[key] = 0
            self.api_tree.insert("", tk.END, values=(key, ""))
            self.api_keys_entry.delete(0, tk.END)
            self.save_configuration()

    def remove_selected_api_key(self):
        selected = self.api_tree.selection()
        if selected:
            for item in selected:
                key = self.api_tree.item(item, "values")[0]
                self.api_keys = [k for k in self.api_keys if k != key]
                self.api_tree.delete(item)
                if key in self.key_usage:
                    del self.key_usage[key]
            self.save_configuration()

    def verify_api_keys(self):
        dummy_cx = "invalid_cx_placeholder"
        test_query = "test"
        for item in self.api_tree.get_children():
            key = self.api_tree.item(item, "values")[0]
            params = {"key": key, "cx": dummy_cx, "q": test_query}
            try:
                response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
                if response.status_code == 400:
                    error_info = response.json()["error"]["errors"][0]
                    message = error_info.get("message", "").strip().lower()
                    if "request contains an invalid argument" in message:
                        self.api_tree.set(item, "Status", "OK")
                        self.api_tree.tag_configure("ok", foreground="green")
                        self.api_tree.item(item, tags=("ok",))
                    elif "api key not valid" in message or "api key not found" in message:
                        self.api_tree.set(item, "Status", "no valid")
                        self.api_tree.tag_configure("fail", foreground="red")
                        self.api_tree.item(item, tags=("fail",))
                    elif "quota exceeded" in message:
                        self.api_tree.set(item, "Status", message)
                        self.api_tree.tag_configure("quota", foreground="orange")
                        self.api_tree.item(item, tags=("quota",))
                    else:
                        self.api_tree.set(item, "Status", message)
                        self.api_tree.tag_configure("fail", foreground="red")
                        self.api_tree.item(item, tags=("fail",))
                else:
                    try:
                        error_info = response.json()["error"]["errors"][0]
                        message = error_info.get("message", "").strip().lower()
                        if "quota exceeded" in message:
                            self.api_tree.set(item, "Status", message)
                            self.api_tree.tag_configure("quota", foreground="orange")
                            self.api_tree.item(item, tags=("quota",))
                        else:
                            self.api_tree.set(item, "Status", message)
                            self.api_tree.tag_configure("fail", foreground="red")
                            self.api_tree.item(item, tags=("fail",))
                    except Exception:
                        self.api_tree.set(item, "Status", "Falla")
                        self.api_tree.tag_configure("fail", foreground="red")
                        self.api_tree.item(item, tags=("fail",))
            except Exception as e:
                self.api_tree.set(item, "Status", "Falla")
                self.api_tree.tag_configure("fail", foreground="red")
                self.api_tree.item(item, tags=("fail",))

    def cx_window(self):
        if self.cx_win is not None and self.cx_win.winfo_exists():
            self.cx_win.lift()
            return
        self.cx_win = tk.Toplevel(self.root)
        self.child_windows.append(self.cx_win)
        self.cx_win.title(self.translate("cx"))
        set_app_icon(self.cx_win)
        self.cx_win.geometry("500x400")
        self.cx_win.resizable(False, False)
        self.cx_win.configure(bg='#2d2d2d')
        self.cx_label = ttk.Label(self.cx_win, text=self.translate("cx") + ":",
                                    background='#2d2d2d', foreground='white')
        self.cx_label.pack(padx=10, pady=10)
        vcmd_cx = (self.cx_win.register(self.validate_length), '%P')
        self.cx_entry = tk.Entry(self.cx_win, width=50, bg='#3c3f41', fg='white',
                                 insertbackground='white', validate="key", validatecommand=vcmd_cx)
        self.cx_entry.pack(padx=10, pady=10)
        self.add_context_menu(self.cx_entry)
        if self.cx:
            self.cx_entry.insert(0, self.cx)
        self.cx_save_button = ttk.Button(self.cx_win, text=self.translate("add_cx_button"),
                                         command=lambda: self.save_cx(self.cx_entry.get()), cursor="hand2")
        self.cx_save_button.pack(padx=10, pady=10)
        self.cx_guide_label = tk.Text(self.cx_win, width=60, height=8, bg='#2d2d2d', fg='white',
                                      wrap='word', bd=0)
        self.cx_guide_label.pack(padx=10, pady=10)
        self.cx_guide_label.delete("1.0", tk.END)
        self.cx_guide_label.insert(tk.END, self.translate("cx_guide"))
        
        self.cx_guide_label.config(state='normal')
        anchor_text = "Google Custom Search Engine"
        start_index = self.cx_guide_label.search(anchor_text, "1.0", tk.END)
        if start_index:
            end_index = f"{start_index}+{len(anchor_text)}c"
            self.cx_guide_label.tag_add("cse_link", start_index, end_index)
            self.cx_guide_label.tag_config("cse_link", foreground="#00FF00", underline=True)
            self.cx_guide_label.tag_bind("cse_link", "<Enter>", lambda e: self.cx_guide_label.config(cursor="hand2"))
            self.cx_guide_label.tag_bind("cse_link", "<Leave>", lambda e: self.cx_guide_label.config(cursor="arrow"))
            self.cx_guide_label.tag_bind("cse_link", "<Button-1>", lambda e: webbrowser.open("https://cse.google.com/cse"))
        self.cx_guide_label.config(state='disabled')

        def update_ui():
            self.cx_win.title(self.translate("cx"))
            self.cx_label.config(text=self.translate("cx") + ":")
            self.cx_save_button.config(text=self.translate("add_cx_button"))
            self.cx_guide_label.config(state='normal')
            self.cx_guide_label.delete("1.0", tk.END)
            self.cx_guide_label.insert(tk.END, self.translate("cx_guide"))
            # Reasignamos el enlace después de actualizar el texto
            start_index = self.cx_guide_label.search(anchor_text, "1.0", tk.END)
            if start_index:
                end_index = f"{start_index}+{len(anchor_text)}c"
                self.cx_guide_label.tag_add("cse_link", start_index, end_index)
                self.cx_guide_label.tag_config("cse_link", foreground="#00FF00", underline=True)
                self.cx_guide_label.tag_bind("cse_link", "<Enter>", lambda e: self.cx_guide_label.config(cursor="hand2"))
                self.cx_guide_label.tag_bind("cse_link", "<Leave>", lambda e: self.cx_guide_label.config(cursor="arrow"))
                self.cx_guide_label.tag_bind("cse_link", "<Button-1>", lambda e: webbrowser.open("https://cse.google.com/cse"))
            self.cx_guide_label.config(state='disabled')
            self.add_context_menu(self.cx_entry)
        self.cx_win.update_ui_texts = update_ui
        self.cx_win.protocol("WM_DELETE_WINDOW", lambda w=self.cx_win: self.on_child_close(w, "cx_win"))

    def save_cx(self, cx):
        self.cx = cx.strip()
        self.save_configuration()
        if self.cx_win is not None and self.cx_win.winfo_exists():
            self.on_child_close(self.cx_win, "cx_win")

    def get_available_api_key(self):
        if self.current_api_key_index < len(self.api_keys):
            return self.api_keys[self.current_api_key_index]
        return None

    def get_indexed_urls(self, domain):
        query = f"site:{domain}"
        self.invalid_cx_flag = False
        while True:
            api_key = self.get_available_api_key()
            if not api_key:
                return None
            params = {"key": api_key, "cx": self.cx, "q": query}
            response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
            if response.status_code == 200:
                search_results = response.json()
                total_results = search_results.get("searchInformation", {}).get("totalResults", "0")
                self.key_usage[api_key] += 1
                return int(total_results)
            elif response.status_code == 429:
                self.current_api_key_index += 1
            elif response.status_code == 400:
                try:
                    error_info = response.json()["error"]["errors"][0]
                    message = error_info.get("message", "").strip().lower()
                    if "request contains an invalid argument" in message:
                        self.invalid_cx_flag = True
                        return None
                    if "api key not valid" in message or "api key not found" in message or "quota exceeded" in message:
                        self.current_api_key_index += 1
                        continue
                    else:
                        self.root.after(0, lambda: messagebox.showerror("Error", f"Error al obtener resultados para {domain}: {response.status_code}\n{response.text}"))
                        return 0
                except Exception:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Error al obtener resultados para {domain}: {response.status_code}\n{response.text}"))
                    return 0
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error al obtener resultados para {domain}: {response.status_code}\n{response.text}"))
                return 0

    def validate_config(self):
        if not self.api_keys and not self.cx:
            messagebox.showwarning("Configuración Requerida", self.translate("configure_both_keys"))
            return False
        if not self.api_keys:
            messagebox.showwarning("Configuración Requerida", self.translate("configure_api_keys"))
            return False
        if not self.cx:
            messagebox.showwarning("Configuración Requerida", self.translate("configure_cx_key"))
            return False
        return True

    def search(self):
        if not self.validate_config():
            return
        self.filtrar_dominios_en_casilla()
        self.current_api_key_index = 0
        self.invalid_cx_flag = False
        self.spinner.start()
        threading.Thread(target=self._search_process).start()

    def _search_process(self):
        domains = self.query_text.get("1.0", tk.END).strip().split("\n")
        if not domains or domains == [""]:
            self.root.after(0, lambda: messagebox.showwarning("Error de Entrada", self.translate("enter_domains")))
            self.root.after(0, self.spinner.stop)
            return
        new_results = {}
        keys_used = set()
        not_processed = []
        for domain in domains:
            domain = domain.strip()
            if domain:
                if domain in self.full_results:
                    continue
                result = self.get_indexed_urls(domain)
                if self.invalid_cx_flag:
                    self.root.after(0, lambda: messagebox.showerror("Error", self.translate("invalid_cx_error")))
                    self.root.after(0, self.spinner.stop)
                    return
                if result is None:
                    not_processed.append(domain)
                    continue
                new_results[domain] = result
                keys_used.add(self.api_keys[self.current_api_key_index])
        self.full_results.update(new_results)
        if not_processed:
            count = len(not_processed)
            if self.language == "es":
                message = (
                    f"{count} dominios no se han podido analizar porque las claves API proporcionadas "
                    "no son válidas o han alcanzado su límite diario de consultas. Por favor, verifica y añade claves API válidas; "
                    "los dominios no analizados se mantendrán en la casilla de entrada."
                )
            else:
                message = (
                    f"{count} domains could not be analyzed because the provided API keys are either invalid or have reached "
                    "their daily quota. Please verify and add valid API keys; the unprocessed domains will remain in the input field."
                )
            self.root.after(0, lambda: messagebox.showinfo("Información", message))
        self.root.after(0, lambda: self.query_text.delete(1.0, tk.END))
        if not_processed:
            self.root.after(0, lambda: self.query_text.insert(tk.END, "\n".join(not_processed)))
        self.root.after(0, lambda: self.results_text.delete(1.0, tk.END))
        self.root.after(0, lambda: self.process_results(self.full_results, keys_used))
        self.root.after(0, self.spinner.stop)

    def process_results(self, results, keys_used):
        sorted_results = sorted(results.items(), key=lambda item: (0 if isinstance(item[1], int) else 1, item[1]), reverse=True)
        self.results_text.insert(tk.END, self.translate("api_keys_used", count=len(keys_used)) + "\n\n")
        self.results_text.insert(tk.END, self.translate("domain_results") + "\n")
        self.results_text.insert(tk.END, self.translate("divider") + "\n")
        self.domain_colors = {"green": [], "yellow": [], "orange": []}
        for domain, total in sorted_results:
            if total == "quota_exceeded":
                display_text = self.translate("cuota_api_superada")
                color = "#FF8C00"
                self.domain_colors["orange"].append(domain)
            else:
                if total > 10:
                    color = "#00FF00"
                    self.domain_colors["green"].append(domain)
                elif total > 5:
                    color = "yellow"
                    self.domain_colors["yellow"].append(domain)
                elif total > 0:
                    color = "orange"
                    self.domain_colors["orange"].append(domain)
                else:
                    color = "#FF5252"
            tag_name = f"link_{domain.replace('.', '_')}"
            self.results_text.insert(tk.END, domain, tag_name)
            if isinstance(total, int):
                self.results_text.insert(tk.END, f": {total} " + self.translate("urls_indexed") + "\n", "default")
            else:
                self.results_text.insert(tk.END, f": {display_text}\n", "default")
            self.results_text.tag_configure(tag_name, foreground=color, underline=True)
            self.results_text.tag_configure("default", foreground="white")
            self.results_text.tag_bind(tag_name, "<Button-1>", lambda e, d=domain: self.open_in_browser(d))
            self.results_text.tag_bind(tag_name, "<Enter>", lambda e: self.results_text.config(cursor="hand2"))
            self.results_text.tag_bind(tag_name, "<Leave>", lambda e: self.results_text.config(cursor="arrow"))
        self.results_text.update_idletasks()

    def open_in_browser(self, domain):
        url = f"https://www.google.com/search?q=site:{domain}"
        webbrowser.open(url)

    def copy_domains(self, color):
        if not hasattr(self, "domain_colors"):
            messagebox.showinfo("Copiar Dominios", self.translate("no_domains_to_copy"))
            return
        translated_color = self.translate(color)
        if color in self.domain_colors:
            domains = self.domain_colors[color]
            if domains:
                self.root.clipboard_clear()
                self.root.clipboard_append("\n".join(domains))
                self.root.update()
                messagebox.showinfo("Copiar Dominios", self.translate("copy_color", color=translated_color))
            else:
                messagebox.showinfo("Copiar Dominios", self.translate("no_domains_to_copy"))
        else:
            messagebox.showinfo("Copiar Dominios", self.translate("no_domains_to_copy"))

    def copy_all_domains(self):
        if not hasattr(self, "domain_colors"):
            messagebox.showinfo("Copiar Todos", self.translate("no_domains_to_copy"))
            return
        all_domains = self.domain_colors.get("green", []) + self.domain_colors.get("yellow", []) + self.domain_colors.get("orange", [])
        if all_domains:
            self.root.clipboard_clear()
            self.root.clipboard_append("\n".join(all_domains))
            self.root.update()
            messagebox.showinfo("Copiar Todos", self.translate("copy_all_confirm"))
        else:
            messagebox.showinfo("Copiar Todos", self.translate("no_domains_to_copy"))

    def export_csv(self):
        if not self.full_results:
            messagebox.showwarning("Export CSV", self.translate("enter_domains"))
            return
        now = datetime.now()
        default_filename = f"GIndexChecker_{now.strftime('%Y-%m-%d_%H-%M')}.csv"
        file_path = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                sorted_results = sorted(
                    self.full_results.items(),
                    key=lambda item: item[1] if isinstance(item[1], int) else 0,
                    reverse=True
                )
                with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(["Domain", "Total Results"])
                    for domain, total in sorted_results:
                        if total == "quota_exceeded":
                            writer.writerow([domain, self.translate("cuota_api_superada")])
                        else:
                            writer.writerow([domain, total])
                messagebox.showinfo("Export CSV", self.translate("csv_export_success"))
            except Exception as e:
                messagebox.showerror("Export CSV", f"Error exporting CSV: {e}")

    def clear_results(self):
        self.results_text.delete(1.0, tk.END)
        self.full_results = {}

    def show_help_documentation(self):
        if self.help_doc_win is not None and self.help_doc_win.winfo_exists():
            self.help_doc_win.lift()
            return
        self.help_doc_win = tk.Toplevel(self.root)
        self.child_windows.append(self.help_doc_win)
        self.help_doc_win.title(self.translate("help_documentation"))
        set_app_icon(self.help_doc_win)
        self.help_doc_win.geometry("730x350")
        self.help_doc_win.resizable(False, False)
        self.help_doc_win.configure(bg='#2d2d2d')
        text = tk.Text(self.help_doc_win, wrap="word", bg='#2d2d2d', fg='white', bd=0)
        text.pack(fill="both", expand=True, padx=10, pady=10)
        md = self.translate("help_documentation_text")
        self.process_markdown_links(md, text)
        def update_ui():
            self.help_doc_win.title(self.translate("help_documentation"))
            text.delete("1.0", tk.END)
            self.process_markdown_links(self.translate("help_documentation_text"), text)
        self.help_doc_win.update_ui_texts = update_ui
        self.help_doc_win.protocol("WM_DELETE_WINDOW", lambda w=self.help_doc_win: self.on_child_close(w, "help_doc_win"))

    def show_help_about(self):
        if self.help_about_win is not None and self.help_about_win.winfo_exists():
            self.help_about_win.lift()
            return
        self.help_about_win = tk.Toplevel(self.root)
        self.child_windows.append(self.help_about_win)
        self.help_about_win.title(self.translate("help_about"))
        set_app_icon(self.help_about_win)
        self.help_about_win.geometry("600x450")
        self.help_about_win.resizable(False, False)
        self.help_about_win.configure(bg='#2d2d2d')
        icon_path = resource_path("gindexchecker2.png")
        if os.path.exists(icon_path):
            img = tk.PhotoImage(file=icon_path)
            img_label = tk.Label(self.help_about_win, image=img, bg='#2d2d2d')
            img_label.image = img
            img_label.pack(pady=10)
        text = tk.Text(self.help_about_win, wrap="word", bg='#2d2d2d', fg='white', bd=0, height=8)
        text.pack(fill="both", expand=True, padx=10, pady=(0,10))
        md = self.translate("help_about_text")
        self.process_markdown_links(md, text)
        def update_ui():
            self.help_about_win.title(self.translate("help_about"))
            text.delete("1.0", tk.END)
            self.process_markdown_links(self.translate("help_about_text"), text)
        self.help_about_win.update_ui_texts = update_ui
        self.help_about_win.protocol("WM_DELETE_WINDOW", lambda w=self.help_about_win: self.on_child_close(w, "help_about_win"))

    def show_help_donations(self):
        if self.help_donations_win is not None and self.help_donations_win.winfo_exists():
            self.help_donations_win.lift()
            return
        self.help_donations_win = tk.Toplevel(self.root)
        self.child_windows.append(self.help_donations_win)
        self.help_donations_win.title(self.translate("help_donations"))
        set_app_icon(self.help_donations_win)
        self.help_donations_win.geometry("600x200")
        self.help_donations_win.resizable(False, False)
        self.help_donations_win.configure(bg='#2d2d2d')
        text = tk.Text(self.help_donations_win, wrap="word", bg='#2d2d2d', fg='white', bd=0)
        text.pack(fill="both", expand=True, padx=10, pady=10)
        text.delete("1.0", tk.END)
        # Build the full donation content by concatenating the donation text and a markdown link.
        donation_content = self.translate("help_donations_text")
        # The link text is taken from translations ('donations_view_qr') (for example "Ver codigo QR" or "View QR Code")
        qr_link = f"[{self.translate('donations_view_qr')}](https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=bc1qs4n97g4k65rmqymzw3q6syg75m3z3yun9kfk39)"
        full_content = donation_content + "\n\n" + qr_link
        # Process markdown so that the link becomes clickable, with green color and hand cursor.
        self.process_markdown_links(full_content, text)
        text.config(state="disabled")
        def show_copy_menu(event):
            try:
                selected = text.get(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                return
            copy_menu = Menu(self.help_donations_win, tearoff=0, bg='#3c3f41', fg='white')
            copy_menu.add_command(label=self.translate("copy"), command=lambda: self.help_donations_win.clipboard_append(selected))
            copy_menu.post(event.x_root, event.y_root)
        text.bind("<Button-3>", show_copy_menu)
        def update_ui():
            self.help_donations_win.title(self.translate("help_donations"))
            text.config(state="normal")
            text.delete("1.0", tk.END)
            donation_content = self.translate("help_donations_text")
            qr_link = f"[{self.translate('donations_view_qr')}](https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=bc1qs4n97g4k65rmqymzw3q6syg75m3z3yun9kfk39)"
            full_content = donation_content + "\n\n" + qr_link
            self.process_markdown_links(full_content, text)
            text.config(state="disabled")
        self.help_donations_win.update_ui_texts = update_ui
        self.help_donations_win.protocol("WM_DELETE_WINDOW", lambda w=self.help_donations_win: self.on_child_close(w, "help_donations_win"))

    def process_markdown_links(self, md_text, text_widget):
        links = list(re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', md_text))
        cleaned = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'[\1]', md_text)
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, cleaned)
        for link in links:
            anchor_text = link.group(1)
            url = link.group(2)
            start = text_widget.search(f'[{anchor_text}]', "1.0", tk.END)
            if start:
                end = f"{start}+{len(anchor_text)+2}c"
                tag = f"link_{start}"
                text_widget.tag_add(tag, start, end)
                text_widget.tag_config(tag, foreground="#00FF00", underline=True)
                text_widget.tag_bind(tag, "<Enter>", lambda e: text_widget.config(cursor="hand2"))
                text_widget.tag_bind(tag, "<Leave>", lambda e: text_widget.config(cursor="arrow"))
                text_widget.tag_bind(tag, "<Button-1>", lambda e, url=url: webbrowser.open(url))

if __name__ == "__main__":
    root = tk.Tk()
    app = GIndexCheckerApp(root)
    root.mainloop()
