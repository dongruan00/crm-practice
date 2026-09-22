def payload(name="张三", phone="13800000000", company="示例科技"):
    return {"name": name, "phone": phone, "company": company}


def test_create_and_get_customer(client):
    response = client.post("/api/customers", json=payload())
    assert response.status_code == 201
    customer_id = response.get_json()["data"]["id"]

    detail = client.get(f"/api/customers/{customer_id}")
    assert detail.status_code == 200
    assert detail.get_json()["data"]["name"] == "张三"


def test_duplicate_phone_returns_400(client):
    client.post("/api/customers", json=payload())
    response = client.post("/api/customers", json=payload(name="李四"))
    assert response.status_code == 400
    assert response.get_json()["message"] == "手机号已存在"


def test_list_search_and_pagination(client):
    client.post("/api/customers", json=payload())
    client.post("/api/customers", json=payload(
        name="李四", phone="13900000000", company="另一家公司"
    ))

    response = client.get("/api/customers?keyword=张三&page=1&per_page=1")
    data = response.get_json()["data"]
    assert response.status_code == 200
    assert data["total"] == 1
    assert len(data["customers"]) == 1


def test_update_rejects_duplicate_phone(client):
    first = client.post("/api/customers", json=payload()).get_json()["data"]
    client.post("/api/customers", json=payload(
        name="李四", phone="13900000000"
    ))

    response = client.put(
        f"/api/customers/{first['id']}",
        json=payload(name="张三改", phone="13900000000"),
    )
    assert response.status_code == 400


def test_missing_customer_returns_404(client):
    response = client.get("/api/customers/999")
    assert response.status_code == 404


def test_delete_customer(client):
    created = client.post("/api/customers", json=payload()).get_json()["data"]
    response = client.delete(f"/api/customers/{created['id']}")
    assert response.status_code == 200
    assert client.get(f"/api/customers/{created['id']}").status_code == 404
