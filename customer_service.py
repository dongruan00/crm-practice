from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Customer


def create_customer(name, phone, company=None):
    existing = db.session.scalar(select(Customer).where(Customer.phone == phone))
    if existing:
        raise ValueError("手机号已存在")

    customer = Customer(name=name, phone=phone, company=company)
    try:
        db.session.add(customer)
        db.session.commit()
        return customer
    except IntegrityError as exc:
        db.session.rollback()
        raise ValueError("手机号已存在") from exc


def list_customers(keyword="", page=1, per_page=10):
    stmt = select(Customer)
    count_stmt = select(func.count()).select_from(Customer)

    if keyword:
        condition = or_(
            Customer.name.contains(keyword),
            Customer.company.contains(keyword),
        )
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)

    total = db.session.scalar(count_stmt) or 0
    customers = db.session.scalars(
        stmt.order_by(Customer.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    ).all()

    return {
        "customers": customers,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }


def get_customer_by_id(customer_id):
    return db.session.get(Customer, customer_id)


def update_customer(customer_id, name, phone, company=None):
    customer = db.session.get(Customer, customer_id)
    if customer is None:
        raise LookupError("客户不存在")

    other = db.session.scalar(
        select(Customer).where(
            Customer.phone == phone,
            Customer.id != customer_id,
        )
    )
    if other:
        raise ValueError("手机号已被其他客户使用")

    customer.name = name
    customer.phone = phone
    customer.company = company

    try:
        db.session.commit()
        return customer
    except IntegrityError as exc:
        db.session.rollback()
        raise ValueError("手机号已被其他客户使用") from exc


def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    if customer is None:
        raise LookupError("客户不存在")

    db.session.delete(customer)
    db.session.commit()
