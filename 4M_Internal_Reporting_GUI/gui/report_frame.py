
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import date

from database import load_csv, create_report
from engines.man_engine import validate_man
from engines.method_engine import validate_method
from engines.material_engine import validate_material
from engines.machine_engine import validate_machine


class ReportFrame(ttk.Frame):
    def __init__(self, parent, user, app):
        super().__init__(parent)
        self.user, self.app = user, app
        self.employees = load_csv("employees.csv")
        self.machines = load_csv("machines.csv")
        self.bom = load_csv("bom_list.csv")
        self.wis = load_csv("wi_list.csv")
        self.category = tk.StringVar(value="Man")
        self.severity = tk.StringVar(value="Trung bình")
        self.attachment = ""

        ttk.Label(self, text="📝 Báo cáo sự cố 4M", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self, text="Nhập thông tin theo từng nhóm nguyên nhân",
                  style="Sub.TLabel").pack(anchor="w", pady=(0,10))

        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Label(top, text="Mã NV:").grid(row=0,column=0,sticky="w")
        ttk.Entry(top, width=12, state="readonly",
                  textvariable=tk.StringVar(value=user["user_id"])).grid(row=0,column=1,padx=5)
        ttk.Label(top, text="Người báo:").grid(row=0,column=2,padx=(15,3))
        ttk.Label(top, text=user["name"]).grid(row=0,column=3,sticky="w")
        ttk.Label(top, text="Ngày báo cáo:").grid(row=0,column=4,padx=(20,3))
        self.date_var = tk.StringVar(value=str(date.today()))
        ttk.Entry(top, textvariable=self.date_var, width=12).grid(row=0,column=5)

        ttk.Label(top, text="Mức độ:").grid(row=0,column=6,padx=(20,3))
        ttk.Combobox(top, textvariable=self.severity, state="readonly",
                     values=["Thấp","Trung bình","Cao"], width=12).grid(row=0,column=7)

        selector = ttk.Frame(self)
        selector.pack(fill="x", pady=15)
        for cat, icon in [("Man","👤"),("Method","📘"),("Material","🧱"),("Machine","⚙")]:
            ttk.Button(selector, text=f"{icon} {cat}", command=lambda c=cat:self.select_category(c)).pack(
                side="left", expand=True, fill="x", padx=3)

        self.form = ttk.Frame(self)
        self.form.pack(fill="both", expand=True)
        self.build_man()

    def select_category(self, category):
        self.category.set(category)
        for w in self.form.winfo_children():
            w.destroy()
        getattr(self, f"build_{category.lower()}")()

    def add_common_bottom(self):
        ttk.Label(self.form, text="Đính kèm ảnh / file (không bắt buộc)").pack(anchor="w", pady=(10,2))
        af = ttk.Frame(self.form)
        af.pack(fill="x")
        self.file_label = ttk.Label(af, text="Chưa chọn file", foreground="#666")
        self.file_label.pack(side="left")
        ttk.Button(af, text="Chọn file...", command=self.choose_file).pack(side="right")
        ttk.Button(self.form, text="📤 SUBMIT BÁO CÁO", command=self.submit).pack(
            pady=15, ipadx=30, ipady=8)

    def choose_file(self):
        path = filedialog.askopenfilename(
            title="Chọn file đính kèm",
            filetypes=[("Ảnh / tài liệu","*.png *.jpg *.jpeg *.pdf *.xlsx *.docx"),("Tất cả","*.*")]
        )
        if path:
            self.attachment = path
            self.file_label.config(text=path)

    def build_man(self):
        ttk.Label(self.form, text="👤 MAN — Con người", font=("Segoe UI",14,"bold")).pack(anchor="w")
        teams = sorted(set(x["team"] for x in self.employees if x.get("team")))
        self.team_var=tk.StringVar(value="Tất cả")
        row=ttk.Frame(self.form); row.pack(fill="x",pady=8)
        ttk.Label(row,text="Tổ:").pack(side="left")
        cb=ttk.Combobox(row,textvariable=self.team_var,state="readonly",values=["Tất cả"]+teams,width=18)
        cb.pack(side="left",padx=5); cb.bind("<<ComboboxSelected>>",lambda e:self.update_people())
        self.person_var=tk.StringVar()
        self.person_cb=ttk.Combobox(row,textvariable=self.person_var,state="readonly",width=35)
        self.person_cb.pack(side="left",padx=10)
        self.update_people()
        ttk.Label(self.form,text="Loại vấn đề:").pack(anchor="w")
        self.issue_var=tk.StringVar(value="Vắng mặt")
        ttk.Combobox(self.form,textvariable=self.issue_var,state="readonly",
                     values=["Vắng mặt","Kỹ năng yếu","Vi phạm quy trình","An toàn","Khác"]).pack(anchor="w")
        ttk.Label(self.form,text="Mô tả vấn đề:").pack(anchor="w",pady=(10,2))
        self.desc=tk.Text(self.form,height=9); self.desc.pack(fill="both",expand=True)
        self.add_common_bottom()

    def update_people(self):
        team=self.team_var.get()
        rows=[x for x in self.employees if team=="Tất cả" or x["team"]==team]
        self.people_rows=rows
        self.person_cb["values"]=[x["name"] for x in rows]
        if rows:self.person_var.set(rows[0]["name"])

    def build_method(self):
        ttk.Label(self.form,text="📘 METHOD — Phương pháp / W.I",font=("Segoe UI",14,"bold")).pack(anchor="w")
        self.wi_var=tk.StringVar()
        ttk.Combobox(self.form,textvariable=self.wi_var,state="readonly",
                     values=[x["wi_code"] for x in self.wis],width=25).pack(anchor="w",pady=8)
        self.wi_info=ttk.Label(self.form,text="")
        self.wi_info.pack(anchor="w")
        self.wi_var.trace_add("write",lambda *a:self.show_wi())
        ttk.Label(self.form,text="Loại vấn đề:").pack(anchor="w",pady=(10,2))
        self.issue_var=tk.StringVar(value="Làm sai quy trình")
        ttk.Combobox(self.form,textvariable=self.issue_var,state="readonly",
                     values=["Làm sai quy trình","W.I chưa cập nhật","Thiếu W.I","Không phù hợp thực tế","Khác"]).pack(anchor="w")
        ttk.Label(self.form,text="Mô tả lỗi Method:").pack(anchor="w",pady=(10,2))
        self.desc=tk.Text(self.form,height=9);self.desc.pack(fill="both",expand=True)
        self.add_common_bottom()

    def show_wi(self):
        r=next((x for x in self.wis if x["wi_code"]==self.wi_var.get()),None)
        if r:self.wi_info.config(text=f'{r["wi_name"]} | Folder: {r["folder_path"]}')

    def build_material(self):
        ttk.Label(self.form,text="🧱 MATERIAL — Vật liệu",font=("Segoe UI",14,"bold")).pack(anchor="w")
        row=ttk.Frame(self.form);row.pack(fill="x",pady=8)
        ttk.Label(row,text="Part Number:").pack(side="left")
        self.part_var=tk.StringVar()
        e=ttk.Entry(row,textvariable=self.part_var,width=25);e.pack(side="left",padx=5)
        e.bind("<FocusOut>",lambda e:self.lookup_part())
        ttk.Button(row,text="Tra BOM",command=self.lookup_part).pack(side="left")
        self.part_info=ttk.Label(self.form,text="Chưa tra cứu BOM");self.part_info.pack(anchor="w")
        row2=ttk.Frame(self.form);row2.pack(fill="x",pady=8)
        ttk.Label(row2,text="Số lượng lỗi:").pack(side="left")
        self.qty_var=tk.StringVar(value="1");ttk.Entry(row2,textvariable=self.qty_var,width=12).pack(side="left",padx=5)
        ttk.Label(row2,text="Lot:").pack(side="left",padx=(20,3))
        self.lot_var=tk.StringVar();ttk.Entry(row2,textvariable=self.lot_var,width=25).pack(side="left")
        ttk.Label(self.form,text="Loại vấn đề:").pack(anchor="w")
        self.issue_var=tk.StringVar(value="Sai vật liệu")
        ttk.Combobox(self.form,textvariable=self.issue_var,state="readonly",
                     values=["Sai vật liệu","Sai màu","Lot bất thường","Thiếu vật liệu","Tạp chất","Khác"]).pack(anchor="w")
        ttk.Label(self.form,text="Mô tả:").pack(anchor="w",pady=(10,2))
        self.desc=tk.Text(self.form,height=8);self.desc.pack(fill="both",expand=True)
        self.add_common_bottom()

    def lookup_part(self):
        p=self.part_var.get().strip().upper()
        self.material_row=next((x for x in self.bom if x["part_no"].upper()==p),None)
        if self.material_row:
            r=self.material_row
            self.part_info.config(text=f'Tên: {r["part_name"]} | BOM: {r["bom_name"]} | Version: {r["bom_version"]}')
        else:self.part_info.config(text="Không tìm thấy Part Number trong BOM.")

    def build_machine(self):
        ttk.Label(self.form,text="⚙ MACHINE — Thiết bị",font=("Segoe UI",14,"bold")).pack(anchor="w")
        lines=sorted(set(x["line"] for x in self.machines))
        self.line_var=tk.StringVar(value="Tất cả")
        row=ttk.Frame(self.form);row.pack(fill="x",pady=8)
        ttk.Label(row,text="Dây chuyền:").pack(side="left")
        cb=ttk.Combobox(row,textvariable=self.line_var,state="readonly",values=["Tất cả"]+lines,width=18)
        cb.pack(side="left",padx=5);cb.bind("<<ComboboxSelected>>",lambda e:self.update_machines())
        self.machine_var=tk.StringVar()
        self.machine_cb=ttk.Combobox(row,textvariable=self.machine_var,state="readonly",width=25)
        self.machine_cb.pack(side="left",padx=10);self.machine_cb.bind("<<ComboboxSelected>>",lambda e:self.show_machine())
        self.update_machines()
        self.machine_info=ttk.Label(self.form,text="");self.machine_info.pack(anchor="w")
        ttk.Label(self.form,text="Loại lỗi:").pack(anchor="w",pady=(10,2))
        self.issue_var=tk.StringVar(value="Cơ")
        ttk.Combobox(self.form,textvariable=self.issue_var,state="readonly",
                     values=["Cơ","Điện","Phần mềm","Khác"]).pack(anchor="w")
        ttk.Label(self.form,text="Mô tả hiện tượng:").pack(anchor="w",pady=(10,2))
        self.desc=tk.Text(self.form,height=8);self.desc.pack(fill="both",expand=True)
        self.add_common_bottom()

    def update_machines(self):
        line=self.line_var.get()
        self.machine_rows=[x for x in self.machines if line=="Tất cả" or x["line"]==line]
        self.machine_cb["values"]=[x["machine_code"] for x in self.machine_rows]
        if self.machine_rows:self.machine_var.set(self.machine_rows[0]["machine_code"]);self.show_machine()

    def show_machine(self):
        r=next((x for x in self.machine_rows if x["machine_code"]==self.machine_var.get()),None)
        if r:self.machine_info.config(text=f'{r["machine_name"]} | {r["process"]}')

    def submit(self):
        report_date=self.date_var.get().strip()
        if not report_date:
            messagebox.showerror("Lỗi","Chưa nhập ngày báo cáo.");return
        if report_date > str(date.today()):
            messagebox.showerror("Lỗi","Không được chọn ngày tương lai.");return

        cat=self.category.get(); sev=self.severity.get()
        desc=self.desc.get("1.0","end").strip()
        details={}

        if cat=="Man":
            person=next((x for x in self.people_rows if x["name"]==self.person_var.get()),{})
            result=validate_man(person,self.issue_var.get(),desc)
            details={"employee_id":person.get("user_id",""),"employee_name":person.get("name",""),
                     "team":person.get("team",""),"issue_type":self.issue_var.get(),"description":desc}
            summary=f'{person.get("name","")} - {self.issue_var.get()}'
        elif cat=="Method":
            wi=next((x for x in self.wis if x["wi_code"]==self.wi_var.get()),{})
            result=validate_method(wi,self.issue_var.get(),desc)
            details={"wi_code":self.wi_var.get(),"wi_name":wi.get("wi_name",""),
                     "folder_path":wi.get("folder_path",""),"issue_type":self.issue_var.get(),"description":desc}
            summary=f'{self.wi_var.get()} - {self.issue_var.get()}'
        elif cat=="Material":
            p=self.part_var.get().strip().upper()
            try: qty=float(self.qty_var.get())
            except ValueError: qty=0
            result=validate_material(p,getattr(self,"material_row",None),qty,self.lot_var.get(),self.issue_var.get(),desc)
            r=getattr(self,"material_row",{}) or {}
            details={"part_no":p,"part_name":r.get("part_name",""),"bom_name":r.get("bom_name",""),
                     "bom_version":r.get("bom_version",""),"quantity":qty,"lot":self.lot_var.get(),
                     "issue_type":self.issue_var.get(),"description":desc}
            summary=f'{p} - {self.issue_var.get()}'
        else:
            m=next((x for x in self.machine_rows if x["machine_code"]==self.machine_var.get()),{})
            result=validate_machine(m,self.issue_var.get(),desc)
            details={"machine_code":m.get("machine_code",""),"machine_name":m.get("machine_name",""),
                     "line":m.get("line",""),"process":m.get("process",""),
                     "issue_type":self.issue_var.get(),"description":desc}
            summary=f'{m.get("machine_code","")} - {self.issue_var.get()}'

        if not result["valid"]:
            messagebox.showerror("Không thể gửi báo cáo",result["message"]);return

        code=create_report(self.user,report_date,cat,sev,summary,details,self.attachment)
        messagebox.showinfo("Thành công",f"Đã gửi báo cáo thành công.\n\nMã báo cáo: {code}")
        self.app.show_page("dashboard")
