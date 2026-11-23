
import tkinter as tk
from tkinter import ttk, messagebox

from database import authenticate_user
from gui.dashboard_frame import DashboardFrame
from gui.report_frame import ReportFrame
from gui.management_frame import ManagementFrame
from gui.notice_frame import NoticeFrame


class AppWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("4M Internal Reporting System")
        self.root.geometry("1280x760")
        self.root.minsize(1100, 680)

        self.user = None
        self.frames = {}
        self.style = ttk.Style()
        try:
            self.style.theme_use("vista")
        except tk.TclError:
            pass
        self.style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
        self.style.configure("Sub.TLabel", font=("Segoe UI", 10))
        self.style.configure("Nav.TButton", font=("Segoe UI", 10, "bold"), padding=10)
        self.show_login()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def show_login(self):
        self.clear()
        frame = ttk.Frame(self.root, padding=30)
        frame.place(relx=.5, rely=.5, anchor="center")

        ttk.Label(frame, text="⚠ HỆ THỐNG QUẢN LÝ & BÁO CÁO SỰ CỐ 4M",
                  style="Title.TLabel").pack(pady=(0, 8))
        ttk.Label(frame, text="Ứng dụng Desktop nội bộ • Mạng Local",
                  style="Sub.TLabel").pack(pady=(0, 25))

        box = ttk.LabelFrame(frame, text="Đăng nhập bằng Mã Nhân Viên", padding=20)
        box.pack(fill="x")
        ttk.Label(box, text="Mã nhân viên:").grid(row=0, column=0, sticky="w", pady=5)
        self.login_var = tk.StringVar()
        ent = ttk.Entry(box, textvariable=self.login_var, width=28)
        ent.grid(row=0, column=1, padx=10, pady=5)
        ent.focus()
        ent.bind("<Return>", lambda e: self.login())

        self.login_info = ttk.Label(box, text="", foreground="#555")
        self.login_info.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)

        ttk.Button(box, text="Đăng nhập", command=self.login).grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(15, 0)
        )
        ttk.Label(frame, text="Demo: E001 / E002 / E003 / E004 / E005").pack(pady=12)

    def login(self):
        user = authenticate_user(self.login_var.get())
        if not user:
            self.login_info.config(text="Không tìm thấy Mã Nhân Viên.", foreground="red")
            return
        self.user = user
        self.show_main()

    def show_main(self, start="dashboard"):
        self.clear()
        self.frames = {}

        outer = ttk.Frame(self.root)
        outer.pack(fill="both", expand=True)

        sidebar = ttk.Frame(outer, padding=12)
        sidebar.pack(side="left", fill="y")

        ttk.Label(sidebar, text="4M REPORT", font=("Segoe UI", 18, "bold")).pack(pady=(5, 2))
        ttk.Label(sidebar, text="Internal System", foreground="#666").pack(pady=(0, 20))

        ttk.Label(sidebar, text=self.user["name"], font=("Segoe UI", 10, "bold")).pack()
        ttk.Label(sidebar, text=f'{self.user["user_id"]} • {self.user["role"]}',
                  foreground="#666").pack(pady=(0, 20))

        buttons = [
            ("📡  Tiếp nhận thông tin", "dashboard"),
            ("📝  Báo cáo sự cố 4M", "report"),
            ("📋  Quản lý báo cáo", "manage"),
            ("📌  Chỉ thị & Thông báo", "notice"),
        ]
        for text, key in buttons:
            ttk.Button(sidebar, text=text, style="Nav.TButton",
                       command=lambda k=key: self.show_page(k)).pack(fill="x", pady=4)

        ttk.Separator(sidebar).pack(fill="x", pady=20)
        ttk.Button(sidebar, text="Đăng xuất", command=self.show_login).pack(fill="x")

        self.content = ttk.Frame(outer, padding=(5, 10, 15, 10))
        self.content.pack(side="left", fill="both", expand=True)

        self.show_page(start)

    def show_page(self, key):
        for w in self.content.winfo_children():
            w.destroy()

        if key == "dashboard":
            frame = DashboardFrame(self.content, self.user, self)
        elif key == "report":
            frame = ReportFrame(self.content, self.user, self)
        elif key == "manage":
            frame = ManagementFrame(self.content, self.user, self)
        else:
            frame = NoticeFrame(self.content, self.user, self)
        frame.pack(fill="both", expand=True)
        self.frames[key] = frame
