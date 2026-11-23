
def validate_method(wi_row, issue_type, description):
    if not wi_row:
        return {"valid": False, "message": "Chưa chọn mã W.I."}
    if not description.strip():
        return {"valid": False, "message": "Vui lòng mô tả lỗi Method."}
    return {"valid": True, "message": "OK"}
