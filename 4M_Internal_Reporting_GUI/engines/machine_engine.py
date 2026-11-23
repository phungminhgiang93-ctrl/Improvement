
def validate_machine(machine_row, issue_type, description):
    if not machine_row:
        return {"valid": False, "message": "Chưa chọn mã thiết bị."}
    if not description.strip():
        return {"valid": False, "message": "Vui lòng mô tả hiện tượng Machine."}
    return {"valid": True, "message": "OK"}
