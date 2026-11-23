
def validate_material(part_no, bom_row, quantity, lot, issue_type, description):
    if not part_no:
        return {"valid": False, "message": "Vui lòng nhập Part Number."}
    if not bom_row:
        return {"valid": False, "message": "Part Number không tồn tại trong BOM List."}
    if quantity <= 0:
        return {"valid": False, "message": "Số lượng lỗi phải lớn hơn 0."}
    if not lot.strip():
        return {"valid": False, "message": "Vui lòng nhập mã Lot."}
    if not description.strip():
        return {"valid": False, "message": "Vui lòng mô tả vấn đề Material."}
    return {"valid": True, "message": "OK"}
