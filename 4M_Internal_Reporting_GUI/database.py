
import csv
import json
import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "4m_system.db"
CONFIG_DIR = BASE_DIR / "config"
DB_PATH.parent.mkdir(exist_ok=True)


def get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_code TEXT UNIQUE NOT NULL,
        reporter_id TEXT NOT NULL,
        reporter_name TEXT NOT NULL,
        department TEXT NOT NULL,
        team TEXT,
        report_date TEXT NOT NULL,
        reported_at TEXT NOT NULL,
        category TEXT NOT NULL,
        severity TEXT NOT NULL,
        summary TEXT NOT NULL,
        details_json TEXT NOT NULL,
        attachment_path TEXT,
        status TEXT NOT NULL DEFAULT 'Mới tiếp nhận',
        approved_by TEXT,
        approved_at TEXT,
        updated_by TEXT,
        updated_at TEXT
    );
    CREATE TABLE IF NOT EXISTS report_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        user_id TEXT NOT NULL,
        user_name TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_by TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        is_pinned INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER,
        user_id TEXT NOT NULL,
        action TEXT NOT NULL,
        detail TEXT,
        created_at TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()


def load_csv(filename):
    path = CONFIG_DIR / filename
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def authenticate_user(user_id):
    user_id = (user_id or "").strip().upper()
    for u in load_csv("employees.csv"):
        if u["user_id"].upper() == user_id:
            return u
    return None


def create_report(reporter, report_date, category, severity, summary, details, attachment_path=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO reports(
            report_code, reporter_id, reporter_name, department, team,
            report_date, reported_at, category, severity, summary,
            details_json, attachment_path, status
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, ("TEMP", reporter["user_id"], reporter["name"], reporter["department"],
          reporter.get("team", ""), report_date, now, category, severity, summary,
          json.dumps(details, ensure_ascii=False), attachment_path, "Mới tiếp nhận"))
    rid = cur.lastrowid
    code = f"4M-{datetime.now():%Y%m%d}-{rid:04d}"
    cur.execute("UPDATE reports SET report_code=? WHERE id=?", (code, rid))
    cur.execute(
        "INSERT INTO audit_logs(report_id,user_id,action,detail,created_at) VALUES(?,?,?,?,?)",
        (rid, reporter["user_id"], "Tạo báo cáo", f"{category}: {summary}", now)
    )
    conn.commit()
    conn.close()
    return code


def row_to_report(row):
    if not row:
        return None
    d = dict(row)
    d["details"] = json.loads(d.pop("details_json"))
    return d


def get_reports(user=None, report_date=None, category=None, status=None, keyword=None):
    conn = get_conn()
    sql = "SELECT * FROM reports WHERE 1=1"
    params = []
    if user and user["role"] == "Leader":
        sql += " AND team=?"
        params.append(user.get("team", ""))
    elif user and user["role"] == "Trưởng nhóm/Kỹ sư":
        sql += " AND (team=? OR department=?)"
        params += [user.get("team", ""), user["department"]]
    if report_date:
        sql += " AND report_date=?"
        params.append(report_date)
    if category:
        sql += " AND category=?"
        params.append(category)
    if status:
        sql += " AND status=?"
        params.append(status)
    if keyword:
        sql += " AND (report_code LIKE ? OR summary LIKE ? OR reporter_name LIKE ?)"
        k = f"%{keyword}%"
        params += [k, k, k]
    sql += " ORDER BY reported_at DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [row_to_report(r) for r in rows]


def get_report(report_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM reports WHERE id=?", (report_id,)).fetchone()
    conn.close()
    return row_to_report(row)


def update_status(report_id, status, user):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_conn()
    old = conn.execute("SELECT status FROM reports WHERE id=?", (report_id,)).fetchone()
    old_status = old["status"] if old else ""
    conn.execute(
        "UPDATE reports SET status=?,updated_by=?,updated_at=? WHERE id=?",
        (status, user["user_id"], now, report_id)
    )
    conn.execute(
        "INSERT INTO audit_logs(report_id,user_id,action,detail,created_at) VALUES(?,?,?,?,?)",
        (report_id, user["user_id"], "Cập nhật trạng thái",
         f"{old_status} → {status}", now)
    )
    conn.commit()
    conn.close()


def approve_report(report_id, user):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_conn()
    conn.execute("""
        UPDATE reports SET status='Đã phê duyệt',
        approved_by=?,approved_at=?,updated_by=?,updated_at=? WHERE id=?
    """, (user["user_id"], now, user["user_id"], now, report_id))
    conn.execute(
        "INSERT INTO audit_logs(report_id,user_id,action,detail,created_at) VALUES(?,?,?,?,?)",
        (report_id, user["user_id"], "Phê duyệt", "Trưởng phòng phê duyệt kết quả", now)
    )
    conn.commit()
    conn.close()


def add_comment(report_id, user, content):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_conn()
    conn.execute(
        "INSERT INTO report_comments(report_id,user_id,user_name,content,created_at) VALUES(?,?,?,?,?)",
        (report_id, user["user_id"], user["name"], content, now)
    )
    conn.execute(
        "INSERT INTO audit_logs(report_id,user_id,action,detail,created_at) VALUES(?,?,?,?,?)",
        (report_id, user["user_id"], "Phản hồi", content, now)
    )
    conn.commit()
    conn.close()


def get_comments(report_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM report_comments WHERE report_id=? ORDER BY created_at ASC",
        (report_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_audit_logs(report_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM audit_logs WHERE report_id=? ORDER BY created_at ASC",
        (report_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_notice(user, title, content, pinned=False):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_conn()
    conn.execute(
        "INSERT INTO notices(created_by,title,content,is_pinned,created_at) VALUES(?,?,?,?,?)",
        (user["user_id"], title, content, int(pinned), now)
    )
    conn.commit()
    conn.close()


def get_notices():
    users = {x["user_id"]: x["name"] for x in load_csv("employees.csv")}
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM notices ORDER BY is_pinned DESC, created_at DESC"
    ).fetchall()
    conn.close()
    return [{**dict(r), "created_by_name": users.get(r["created_by"], r["created_by"])} for r in rows]


def set_notice_pin(notice_id, pinned):
    conn = get_conn()
    conn.execute("UPDATE notices SET is_pinned=? WHERE id=?", (int(pinned), notice_id))
    conn.commit()
    conn.close()
