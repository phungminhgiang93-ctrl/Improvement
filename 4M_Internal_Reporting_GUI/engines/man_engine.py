
def validate_man(person_row, issue_type, description):
    if not person_row:
        return {"valid": False, "message": "Chưa chọn nhân viên gặp vấn đề."}
    if not description.strip():
        return {"valid": False, "message": "Vui lòng mô tả vấn đề Man."}
    return {"valid": True, "message": "OK"}
