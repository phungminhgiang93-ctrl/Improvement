
import tkinter as tk
from tkinter import ttk, messagebox
from database import get_reports, get_report, update_status, approve_report, add_comment, get_comments, get_audit_logs


class ManagementFrame(ttk.Frame):
    def __init__(self,parent,user,app):
        super().__init__(parent)
        self.user,self.app=user,app
        self.selected_id=None
        ttk.Label(self,text="📋 Quản lý báo cáo",style="Title.TLabel").pack(anchor="w")
        ttk.Label(self,text="Theo dõi, xử lý, phản hồi và phê duyệt",style="Sub.TLabel").pack(anchor="w",pady=(0,8))
        body=ttk.Panedwindow(self,orient="horizontal");body.pack(fill="both",expand=True)
        left=ttk.Frame(body,padding=5);right=ttk.Frame(body,padding=8)
        body.add(left,weight=1);body.add(right,weight=2)
        self.tree=ttk.Treeview(left,columns=("code","cat","status"),show="headings")
        for c,t,w in [("code","Mã",145),("cat","4M",70),("status","Trạng thái",130)]:
            self.tree.heading(c,text=t);self.tree.column(c,width=w)
        self.tree.pack(fill="both",expand=True);self.tree.bind("<<TreeviewSelect>>",lambda e:self.load_selected())
        self.detail=right
        self.refresh_list()

    def refresh_list(self):
        for i in self.tree.get_children():self.tree.delete(i)
        for r in get_reports(self.user):
            self.tree.insert("", "end",iid=str(r["id"]),values=(r["report_code"],r["category"],r["status"]))

    def select_report_id(self,rid):
        if self.tree.exists(str(rid)):
            self.tree.selection_set(str(rid));self.tree.focus(str(rid));self.load_selected()
        else:self.refresh_list()

    def load_selected(self):
        sel=self.tree.selection()
        if not sel:return
        self.selected_id=int(sel[0]);r=get_report(self.selected_id)
        for w in self.detail.winfo_children():w.destroy()

        ttk.Label(self.detail,text=f'{r["report_code"]} — {r["category"]}',font=("Segoe UI",15,"bold")).pack(anchor="w")
        ttk.Label(self.detail,text=f'Người báo: {r["reporter_name"]} | Ngày: {r["report_date"]} | Mức độ: {r["severity"]}').pack(anchor="w",pady=4)
        ttk.Label(self.detail,text=f'Nội dung: {r["summary"]}',font=("Segoe UI",10,"bold")).pack(anchor="w",pady=4)

        txt=tk.Text(self.detail,height=9,wrap="word");txt.pack(fill="x")
        txt.insert("1.0",str(r["details"]))
        txt.config(state="disabled")

        if r["attachment_path"]:
            ttk.Label(self.detail,text=f'📎 File: {r["attachment_path"]}',foreground="#555").pack(anchor="w")

        if self.user["role"] in ["Trưởng nhóm/Kỹ sư","Trưởng phòng"]:
            bar=ttk.Frame(self.detail);bar.pack(fill="x",pady=8)
            ttk.Label(bar,text="Trạng thái:").pack(side="left")
            self.status_var=tk.StringVar(value=r["status"])
            ttk.Combobox(bar,textvariable=self.status_var,state="readonly",
                         values=["Mới tiếp nhận","Đang xử lý","Đã hoàn thành","Đã phê duyệt"],width=18).pack(side="left",padx=5)
            ttk.Button(bar,text="Cập nhật",command=self.change_status).pack(side="left")
            if self.user["role"]=="Trưởng phòng" and r["status"]=="Đã hoàn thành":
                ttk.Button(bar,text="✔ Phê duyệt",command=self.approve).pack(side="left",padx=5)

        ttk.Label(self.detail,text="💬 Phản hồi / Chuyển giao",font=("Segoe UI",11,"bold")).pack(anchor="w",pady=(8,3))
        comments=get_comments(self.selected_id)
        ctext=tk.Text(self.detail,height=7,wrap="word");ctext.pack(fill="x")
        for c in comments:ctext.insert("end",f'{c["user_name"]} • {c["created_at"]}\n{c["content"]}\n\n')
        ctext.config(state="disabled")
        self.comment=tk.Text(self.detail,height=3);self.comment.pack(fill="x",pady=4)
        ttk.Button(self.detail,text="Gửi phản hồi",command=self.send_comment).pack(anchor="e")

        ttk.Label(self.detail,text="🕘 Lịch sử thao tác",font=("Segoe UI",11,"bold")).pack(anchor="w",pady=(8,3))
        audit=tk.Text(self.detail,height=6,wrap="word");audit.pack(fill="x")
        for x in get_audit_logs(self.selected_id):
            audit.insert("end",f'{x["created_at"]} | {x["user_id"]} | {x["action"]} | {x["detail"]}\n')
        audit.config(state="disabled")

    def change_status(self):
        update_status(self.selected_id,self.status_var.get(),self.user)
        self.refresh_list();self.select_report_id(self.selected_id)

    def approve(self):
        approve_report(self.selected_id,self.user)
        self.refresh_list();self.select_report_id(self.selected_id)

    def send_comment(self):
        content=self.comment.get("1.0","end").strip()
        if not content:return
        add_comment(self.selected_id,self.user,content)
        self.load_selected()
