# Flask CRM：分层客户管理 API

一个用于学习 Flask + SQLAlchemy 的轻量客户管理 REST API，包含完整源码、自动化测试和中文实战教程。

## 功能

- 客户 CRUD（新增、列表、详情、完整更新、删除）
- 按姓名/公司关键词搜索
- 分页查询
- 手机号唯一性约束与冲突处理
- 统一 JSON 响应、基础参数校验
- pytest 自动化测试

## 技术栈

Python 3.10+、Flask、Flask-SQLAlchemy、SQLAlchemy 2.x、SQLite、pytest。

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python app.py
```

首次启动会在 Flask 实例目录下创建 SQLite 数据库。默认服务地址：`http://127.0.0.1:5000`。

运行测试：

```bash
pytest -q
```

## 项目结构

```text
crm-practice/
├── app.py
├── config.py
├── extensions.py
├── models.py
├── customer_service.py
├── routes.py
├── requirements.txt
├── tests/
│   ├── conftest.py
│   └── test_customers.py
└── docs/
    └── 实战教程.md
```

## API 一览

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/customers` | 新增客户 |
| GET | `/api/customers` | 客户列表；支持 `keyword`、`page`、`per_page` |
| GET | `/api/customers/<id>` | 客户详情 |
| PUT | `/api/customers/<id>` | 完整更新客户 |
| DELETE | `/api/customers/<id>` | 删除客户 |

成功响应结构：`{"code":0,"message":"...","data":...}`。创建成功返回 HTTP 201；参数或业务冲突返回 400；资源不存在返回 404。

## 教程

从 [`docs/实战教程.md`](docs/实战教程.md) 开始，包含架构说明、分层职责、接口测试、排错及面试复盘。

## 项目边界

这是教学项目，不是生产级 CRM。上线前应补充认证授权、数据库迁移、日志规范、自动化部署、速率限制和更全面的测试。`db.create_all()` 只创建缺失的表，不会迁移已有表结构。
