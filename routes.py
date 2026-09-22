from flask import Blueprint, jsonify, request

from customer_service import (
    create_customer,
    delete_customer,
    get_customer_by_id,
    list_customers,
    update_customer,
)

customer_bp = Blueprint("customer", __name__, url_prefix="/api/customers")


def success(data=None, message="success", status=200):
    return jsonify({"code": 0, "message": message, "data": data}), status


def error(message, status):
    return jsonify({"code": status, "message": message, "data": None}), status


def _customer_payload():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, error("请求体必须是 JSON 对象", 400)

    name = data.get("name")
    phone = data.get("phone")
    company = data.get("company")

    if not isinstance(name, str) or not name.strip():
        return None, error("姓名不能为空", 400)
    if not isinstance(phone, str) or not phone.strip():
        return None, error("手机号不能为空", 400)
    if company is not None and not isinstance(company, str):
        return None, error("公司必须是字符串或 null", 400)

    return {
        "name": name.strip(),
        "phone": phone.strip(),
        "company": company.strip() if company else None,
    }, None


@customer_bp.post("")
def add_customer():
    payload, validation_error = _customer_payload()
    if validation_error:
        return validation_error

    try:
        customer = create_customer(**payload)
        return success(customer.to_dict(), "创建成功", 201)
    except ValueError as exc:
        return error(str(exc), 400)


@customer_bp.get("")
def get_customers():
    keyword = request.args.get("keyword", "").strip()

    try:
        page = int(request.args.get("page", "1"))
        per_page = int(request.args.get("per_page", "10"))
    except ValueError:
        return error("page 和 per_page 必须是整数", 400)

    if page < 1 or per_page < 1:
        return error("page 和 per_page 必须大于 0", 400)
    if per_page > 100:
        return error("per_page 不能超过 100", 400)

    result = list_customers(keyword, page, per_page)
    data = {
        "customers": [customer.to_dict() for customer in result["customers"]],
        "total": result["total"],
        "page": result["page"],
        "per_page": result["per_page"],
        "pages": result["pages"],
    }
    return success(data, "查询成功")


@customer_bp.get("/<int:customer_id>")
def get_customer(customer_id):
    customer = get_customer_by_id(customer_id)
    if customer is None:
        return error("客户不存在", 404)
    return success(customer.to_dict(), "查询成功")


@customer_bp.put("/<int:customer_id>")
def edit_customer(customer_id):
    payload, validation_error = _customer_payload()
    if validation_error:
        return validation_error

    try:
        customer = update_customer(customer_id, **payload)
        return success(customer.to_dict(), "更新成功")
    except LookupError as exc:
        return error(str(exc), 404)
    except ValueError as exc:
        return error(str(exc), 400)


@customer_bp.delete("/<int:customer_id>")
def remove_customer(customer_id):
    try:
        delete_customer(customer_id)
        return success(None, "删除成功")
    except LookupError as exc:
        return error(str(exc), 404)
