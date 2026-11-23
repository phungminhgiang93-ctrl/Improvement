
import tkinter as tk
from tkinter import ttk
from datetime import date

from database import get_reports, get_notices


class DashboardFrame(ttk.Frame):
    def __init__(self, parent, user, app):
        super().__init__(parent)
        self.user, self.app = user, app

        ttk.Label(self, text="📡 Tiếp nhận thông tin chung",
                  style="Title.TLabel").pack(anchor="w")
        ttk.Label(self, text="Trung tâm theo dõi sự cố 4M và thông tin nội bộ",
                  style="Sub.TLabel").pack(anchor="w", pady=(0, 10))

        self.build_pinned()
        self.build_filters()
        self.build_table()
        self.refresh()

    def build_pinned(self):
        box = ttk.LabelFrame(self, text="📌 Thông báo / Chỉ thị đang ghim", padding=8)
        box.pack(fill="x", pady=(0, 8))
        self.pinned_text = tk.Text(box, height=4, wrap="word", state="disabled")
        self.pinned_text.pack(fill="x")

    def build_filters(self):
        f = ttk.Frame(self)
        f.pack(fill="x", pady=5)

        ttk.Label(f, text="Ngày:").pack(side="left")
        self.date_var = tk.StringVar(value=str(date.today()))
        ttk.Entry(f, textvariable=self.date_var, width=12).pack(side="left", padx=5)

        ttk.Label(f, text="4M:").pack(side="left", padx=(15, 3))
        self.cat_var = tk.StringVar(value="Tất cả")
        ttk.Combobox(f, textvariable=self.cat_var, state="readonly",
                     values=["Tất cả","Man","Method","Material","Machine"],
                     width=12).pack(side="left")

        ttk.Label(f, text="Trạng thái:").pack(side="left", padx=(15, 3))
        self.status_var = tk.StringVar(value="Tất cả")
        ttk.Combobox(f, textvariable=self.status_var, state="readonly",
                     values=["Tất cả","Mới tiếp nhận","Đang xử lý","Đã hoàn thành","Đã phê duyệt"],
                     width=18).pack(side="left")

        self.keyword_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.keyword_var, width=24).pack(side="left", padx=(15, 5))
        ttk.Button(f, text="🔎 Lọc", command=self.refresh).pack(side="left")
        ttk.Button(f, text="⟳ Làm mới", command=self.refresh).pack(side="left", padx=5)

    def build_table(self):
        columns = ("code","date","category","summary","severity","reporter","status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        headers = {
            "code":"Mã báo cáo","date":"Thời gian","category":"4M",
            "summary":"Nội dung","severity":"Mức độ","reporter":"Người báo","status":"Trạng thái"
        }
        widths = {"code":145,"date":145,"category":75,"summary":390,"severity":100,"reporter":160,"status":140}
        for c in columns:
            self.tree.heading(c, text=headers[c])
            self.tree.column(c, width=widths[c], anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.open_selected)

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        category = None if self.cat_var.get()=="Tất cả" else self.cat_var.get()
        status = None if self.status_var.get()=="Tất cả" else self.status_var.get()
        reports = get_reports(
            self.user,
            self.date_var.get().strip() or None,
            category,
            status,
            self.keyword_var.get().strip() or None
        )
        for r in reports:
            self.tree.insert("", "end", iid=str(r["id"]),
                values=(r["report_code"], r["reported_at"], r["category"],
                        r["summary"], r["severity"], r["reporter_name"], r["status"]))

        notices = get_notices()
        pinned = [n for n in notices if n["is_pinned"]]
        self.pinned_text.config(state="normal")
        self.pinned_text.delete("1.0","end")
        if pinned:
            for n in pinned:
                self.pinned_text.insert("end", f'📌 {n["title"]}\n{n["content"]}\n\n')
        else:
            self.pinned_text.insert("end", "Chưa có thông báo được ghim.")
        self.pinned_text.config(state="disabled")

    def open_selected(self, _event=None):
        selected = self.tree.selection()
        if selected:
            self.app.frames.pop("manage", None)
            self.app.show_page("manage")
            self.app.frames["manage"].select_report_id(int(selected[0]))
