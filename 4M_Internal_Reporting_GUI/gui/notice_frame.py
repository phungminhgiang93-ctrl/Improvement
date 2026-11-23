
import tkinter as tk
from tkinter import ttk, messagebox
from database import get_notices, create_notice, set_notice_pin


class NoticeFrame(ttk.Frame):
    def __init__(self,parent,user,app):
        super().__init__(parent)
        self.user,self.app=user,app
        ttk.Label(self,text="📌 Chỉ thị & Thông báo",style="Title.TLabel").pack(anchor="w")
        ttk.Label(self,text="Kênh truyền đạt thông tin từ Trưởng phòng",style="Sub.TLabel").pack(anchor="w",pady=(0,8))
        self.build()

    def build(self):
        if self.user["role"]=="Trưởng phòng":
            box=ttk.LabelFrame(self,text="➕ Tạo thông báo / chỉ thị",padding=10);box.pack(fill="x",pady=(0,10))
            ttk.Label(box,text="Tiêu đề:").grid(row=0,column=0,sticky="w")
            self.title=tk.StringVar();ttk.Entry(box,textvariable=self.title,width=60).grid(row=0,column=1,sticky="ew",padx=5)
            ttk.Label(box,text="Nội dung:").grid(row=1,column=0,sticky="nw",pady=5)
            self.content=tk.Text(box,height=4);self.content.grid(row=1,column=1,sticky="ew",padx=5,pady=5)
            self.pin=tk.BooleanVar();ttk.Checkbutton(box,text="Ghim lên đầu",variable=self.pin).grid(row=2,column=1,sticky="w")
            ttk.Button(box,text="Phát hành",command=self.publish).grid(row=3,column=1,sticky="e",pady=5)
            box.columnconfigure(1,weight=1)

        self.list_frame=ttk.Frame(self);self.list_frame.pack(fill="both",expand=True)
        self.refresh()

    def refresh(self):
        for w in self.list_frame.winfo_children():w.destroy()
        for n in get_notices():
            box=ttk.LabelFrame(self.list_frame,text=f'{"📌 " if n["is_pinned"] else ""}{n["title"]}',padding=8)
            box.pack(fill="x",pady=4)
            ttk.Label(box,text=n["content"],wraplength=800).pack(anchor="w")
            ttk.Label(box,text=f'{n["created_by_name"]} • {n["created_at"]}',foreground="#666").pack(anchor="w",pady=(5,0))
            if self.user["role"]=="Trưởng phòng":
                ttk.Button(box,text="Bỏ ghim" if n["is_pinned"] else "Ghim",
                           command=lambda i=n["id"],p=not bool(n["is_pinned"]):self.toggle_pin(i,p)).pack(anchor="e")

    def publish(self):
        title=self.title.get().strip();content=self.content.get("1.0","end").strip()
        if not title or not content:
            messagebox.showerror("Lỗi","Vui lòng nhập tiêu đề và nội dung.");return
        create_notice(self.user,title,content,self.pin.get())
        self.title.set("");self.content.delete("1.0","end");self.pin.set(False);self.refresh()

    def toggle_pin(self,i,p):
        set_notice_pin(i,p);self.refresh()
