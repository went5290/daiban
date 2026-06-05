# -*- coding: utf-8 -*-

import json
import os
import sys
import tkinter as tk
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from tkinter import messagebox, ttk
from typing import List, Optional


APP_TITLE = "本地提醒助手"
DATA_FILE = "reminders.json"
CHECK_INTERVAL_MS = 5_000
TIME_FORMAT = "%Y-%m-%d %H:%M"


def log_error(exc_type, exc_value, exc_traceback) -> None:
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "error.log")
    with open(log_path, "a", encoding="utf-8") as file:
        file.write("\n" + "=" * 70 + "\n")
        file.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=file)


@dataclass
class Reminder:
    id: int
    remind_at: str
    text: str
    done: bool = False


class ReminderApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("760x520")
        self.root.minsize(680, 440)
        self.root.attributes("-topmost", True)
        self.root.after(800, lambda: self.root.attributes("-topmost", False))
        self.root.after(100, self.root.focus_force)
        self.root.protocol("WM_DELETE_WINDOW", self._minimize_to_background)

        self.data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILE)
        self.reminders: List[Reminder] = []
        self.next_id = 1

        self._build_ui()
        self._load_reminders()
        self._refresh_table()
        self._schedule_check()

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        input_frame = ttk.LabelFrame(self.root, text="添加提醒", padding=12)
        input_frame.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 8))
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="时间").grid(row=0, column=0, sticky="w")
        self.time_var = tk.StringVar(value=(datetime.now() + timedelta(minutes=10)).strftime(TIME_FORMAT))
        time_entry = ttk.Entry(input_frame, textvariable=self.time_var, width=22)
        time_entry.grid(row=0, column=1, sticky="w", padx=(8, 16))

        quick_frame = ttk.Frame(input_frame)
        quick_frame.grid(row=0, column=2, sticky="e")
        for label, minutes in (("10分钟后", 10), ("1小时后", 60), ("明天此时", 24 * 60)):
            ttk.Button(
                quick_frame,
                text=label,
                command=lambda m=minutes: self._set_quick_time(m),
            ).pack(side="left", padx=(0, 6))

        ttk.Label(input_frame, text="事项").grid(row=1, column=0, sticky="nw", pady=(10, 0))
        self.text_input = tk.Text(input_frame, height=4, wrap="word")
        self.text_input.grid(row=1, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=(10, 0))

        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2, column=1, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(button_frame, text="添加提醒", command=self._add_reminder).pack(side="left", padx=(0, 8))
        ttk.Button(button_frame, text="清空输入", command=self._clear_inputs).pack(side="left")

        list_frame = ttk.LabelFrame(self.root, text="提醒列表", padding=12)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=14, pady=8)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        columns = ("time", "status", "text")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("time", text="提醒时间")
        self.tree.heading("status", text="状态")
        self.tree.heading("text", text="事项")
        self.tree.column("time", width=150, anchor="center", stretch=False)
        self.tree.column("status", width=80, anchor="center", stretch=False)
        self.tree.column("text", width=460, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        action_frame = ttk.Frame(self.root)
        action_frame.grid(row=2, column=0, sticky="ew", padx=14, pady=(8, 14))
        ttk.Button(action_frame, text="标记完成", command=self._mark_selected_done).pack(side="left")
        ttk.Button(action_frame, text="删除选中", command=self._delete_selected).pack(side="left", padx=(8, 0))
        ttk.Button(action_frame, text="删除已完成", command=self._delete_done).pack(side="left", padx=(8, 0))
        ttk.Button(action_frame, text="退出程序", command=self._exit_app).pack(side="left", padx=(8, 0))

        self.status_var = tk.StringVar(value="程序运行中，关闭窗口会最小化到后台。")
        ttk.Label(action_frame, textvariable=self.status_var).pack(side="right")

    def _minimize_to_background(self) -> None:
        self.root.iconify()
        self.status_var.set("已在后台运行，到时间会弹出提醒。")

    def _exit_app(self) -> None:
        if messagebox.askyesno(APP_TITLE, "退出后将不再检查提醒，确定退出吗？"):
            self.root.destroy()

    def _set_quick_time(self, minutes: int) -> None:
        self.time_var.set((datetime.now() + timedelta(minutes=minutes)).strftime(TIME_FORMAT))

    def _clear_inputs(self) -> None:
        self.time_var.set((datetime.now() + timedelta(minutes=10)).strftime(TIME_FORMAT))
        self.text_input.delete("1.0", "end")

    def _add_reminder(self) -> None:
        remind_at = self.time_var.get().strip()
        text = self.text_input.get("1.0", "end").strip()

        if not text:
            messagebox.showwarning(APP_TITLE, "请先填写要提醒的事情。")
            return

        try:
            parsed_time = datetime.strptime(remind_at, TIME_FORMAT)
        except ValueError:
            messagebox.showwarning(APP_TITLE, f"时间格式应为：{TIME_FORMAT.replace('%', '')}，例如 2026-06-06 09:30")
            return

        self.reminders.append(Reminder(id=self.next_id, remind_at=parsed_time.strftime(TIME_FORMAT), text=text))
        self.next_id += 1
        self._save_reminders()
        self._refresh_table()
        self._clear_inputs()

    def _mark_selected_done(self) -> None:
        reminder = self._get_selected_reminder()
        if reminder is None:
            return
        reminder.done = True
        self._save_reminders()
        self._refresh_table()

    def _delete_selected(self) -> None:
        reminder = self._get_selected_reminder()
        if reminder is None:
            return
        self.reminders = [item for item in self.reminders if item.id != reminder.id]
        self._save_reminders()
        self._refresh_table()

    def _delete_done(self) -> None:
        self.reminders = [item for item in self.reminders if not item.done]
        self._save_reminders()
        self._refresh_table()

    def _get_selected_reminder(self) -> Optional[Reminder]:
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo(APP_TITLE, "请先在列表中选中一个提醒。")
            return None
        reminder_id = int(selected[0])
        for reminder in self.reminders:
            if reminder.id == reminder_id:
                return reminder
        return None

    def _schedule_check(self) -> None:
        self._check_due_reminders()
        self.root.after(CHECK_INTERVAL_MS, self._schedule_check)

    def _check_due_reminders(self) -> None:
        now = datetime.now()
        changed = False
        due_items: List[Reminder] = []

        for reminder in self.reminders:
            if reminder.done:
                continue
            try:
                remind_time = datetime.strptime(reminder.remind_at, TIME_FORMAT)
            except ValueError:
                continue
            if remind_time <= now:
                reminder.done = True
                changed = True
                due_items.append(reminder)

        if changed:
            self._save_reminders()
            self._refresh_table()

        for reminder in due_items:
            self._show_popup(reminder)

    def _show_popup(self, reminder: Reminder) -> None:
        self.root.deiconify()
        self.root.lift()

        popup = tk.Toplevel(self.root)
        popup.title("提醒")
        popup.geometry("420x230")
        popup.resizable(False, False)
        popup.attributes("-topmost", True)
        popup.grab_set()

        frame = ttk.Frame(popup, padding=18)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="时间到了", font=("Microsoft YaHei UI", 16, "bold")).pack(anchor="w")
        ttk.Label(frame, text=reminder.remind_at).pack(anchor="w", pady=(6, 12))

        text_box = tk.Text(frame, height=5, wrap="word")
        text_box.insert("1.0", reminder.text)
        text_box.configure(state="disabled")
        text_box.pack(fill="both", expand=True)

        ttk.Button(frame, text="知道了", command=popup.destroy).pack(anchor="e", pady=(12, 0))
        popup.bell()
        popup.lift()
        popup.focus_force()

    def _load_reminders(self) -> None:
        if not os.path.exists(self.data_path):
            return

        try:
            with open(self.data_path, "r", encoding="utf-8") as file:
                raw_items = json.load(file)
        except (OSError, json.JSONDecodeError):
            messagebox.showwarning(APP_TITLE, "提醒数据文件读取失败，将从空列表开始。")
            return

        self.reminders = [
            Reminder(
                id=int(item.get("id", index + 1)),
                remind_at=str(item.get("remind_at", "")),
                text=str(item.get("text", "")),
                done=bool(item.get("done", False)),
            )
            for index, item in enumerate(raw_items)
            if item.get("text")
        ]
        if self.reminders:
            self.next_id = max(item.id for item in self.reminders) + 1

    def _save_reminders(self) -> None:
        with open(self.data_path, "w", encoding="utf-8") as file:
            json.dump([asdict(item) for item in self.reminders], file, ensure_ascii=False, indent=2)

    def _refresh_table(self) -> None:
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)

        sorted_items = sorted(self.reminders, key=lambda item: (item.done, item.remind_at))
        for reminder in sorted_items:
            status = "完成" if reminder.done else "等待"
            preview = reminder.text.replace("\n", " ")
            self.tree.insert("", "end", iid=str(reminder.id), values=(reminder.remind_at, status, preview))

        pending_count = sum(1 for item in self.reminders if not item.done)
        self.status_var.set(f"待提醒：{pending_count} 项")


def main() -> None:
    sys.excepthook = log_error
    root = tk.Tk()
    root.report_callback_exception = log_error
    ReminderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
