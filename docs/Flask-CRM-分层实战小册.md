# Flask CRM 分层实战小册

## 从零构建可测试的客户管理 REST API

**技术栈：** Python 3.10+ / Flask / Flask-SQLAlchemy / SQLite / pytest  
**资料类型：** 项目式实战教程  
**版本：** 1.0.0  
**适合读者：** 具备 Python 基础、希望理解 Flask 后端项目分层与接口开发流程的学习者

---

## 使用说明

本小册采用“理解一个概念—完成一个小任务—运行验证—复盘”的方式组织。请尽量亲自输入代码，而不是一次性复制全部文件。

> **学习边界**：本项目是用于教学的轻量 CRM API，不是可直接投入生产的完整 CRM。它未实现认证授权、租户隔离、软删除、审计日志、数据库迁移、限流和生产部署。项目描述与简历表述应以实际完成内容为准。

### 学完后，你将能够

- 创建并运行一个 Flask 应用，理解应用工厂的作用。
- 说明 `app.py`、`routes.py`、`customer_service.py`、`models.py` 的职责边界。
- 使用 SQLAlchemy 定义客户模型并完成 CRUD。
- 实现关键词搜索、分页和手机号唯一性校验。
- 设计统一 JSON 响应，区分业务错误与 HTTP 状态码。
- 使用 curl 和 pytest 验证接口行为。
- 解释一次请求从 HTTP 入口到数据库提交的完整调用链。

## 目录

1. [先理解需求：我们要构建什么](#第-1-章先理解需求我们要构建什么)
2. [搭好开发环境：让 Flask 先跑起来](#第-2-章搭好开发环境让-flask-先跑起来)
3. [拆分职责：建立清晰的项目结构](#第-3-章拆分职责建立清晰的项目结构)
4. [设计数据：用 SQLAlchemy 描述客户](#第-4-章设计数据用-sqlalchemy-描述客户)
5. [编写业务：让 Service 承担用例逻辑](#第-5-章编写业务让-service-承担用例逻辑)
6. [暴露接口：用 Blueprint 处理 HTTP](#第-6-章暴露接口用-blueprint-处理-http)
7. [规范交互：校验、状态码与异常](#第-7-章规范交互校验状态码与异常)
8. [动手验收：用 curl 与 pytest 验证](#第-8-章动手验收用-curl-与-pytest-验证)
9. [排查问题：从现象定位到责任层](#第-9-章排查问题从现象定位到责任层)
10. [复盘与进阶：把项目讲清楚、做扎实](#第-10-章复盘与进阶把项目讲清楚做扎实)
11. [附录：文件清单与发布前检查](#附录文件清单与发布前检查)

---

## 第 1 章：先理解需求——我们要构建什么

### 1.1 项目场景

假设一个小团队需要维护客户资料。我们先不做复杂的登录、权限和前端页面，而是通过 REST API 完成客户信息管理，以此练习后端开发中的核心环节。

### 1.2 功能范围

| 功能 | 规则 |
|---|---|
| 新增客户 | 姓名、手机号必填；手机号不可重复 |
| 客户列表 | 支持姓名/公司关键词搜索与分页 |
| 客户详情 | 根据客户 ID 查询；不存在返回 404 |
| 修改客户 | 本教程按完整更新处理；姓名、手机号必填 |
| 删除客户 | 教学版物理删除 |

### 1.3 API 契约

| 方法 | 路径 | 用途 | 成功状态 |
|---|---|---|---|
| `POST` | `/api/customers` | 新增客户 | 201 |
| `GET` | `/api/customers` | 列表、搜索、分页 | 200 |
| `GET` | `/api/customers/<id>` | 客户详情 | 200 |
| `PUT` | `/api/customers/<id>` | 完整更新 | 200 |
| `DELETE` | `/api/customers/<id>` | 删除客户 | 200 |

统一响应外形：

```json
{
  "code": 0,
  "message": "查询成功",
  "data": {}
}
```

这里的 JSON `code` 是响应体中的业务字段；HTTP 状态码是 HTTP 响应状态行的一部分，两者不要混为一谈。

### 本章练习

1. 不看上表，自己写出五个接口的方法和路径。
2. 思考：为什么“客户不存在”不应该返回 200？
3. 列出本项目明确不实现的三项生产能力。

**本章验收：**你能用自己的话说明项目目标、功能边界和接口清单。

---

## 第 2 章：搭好开发环境——让 Flask 先跑起来

### 2.1 创建目录与虚拟环境

```bash
mkdir crm-practice
cd crm-practice
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell 激活方式：

```powershell
.venv\Scripts\Activate.ps1
```

### 2.2 安装依赖

项目根目录的 `requirements.txt` 包含 Flask、Flask-SQLAlchemy 和 pytest。执行：

```bash
pip install -r requirements.txt
```

### 2.3 写一个最小应用

先建立 `app.py`，确认开发环境、Python 解释器和 Flask 安装无误：

```python
from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/hello")
def hello():
    return jsonify({"message": "Hello CRM"})


if __name__ == "__main__":
    app.run(debug=True)
```

启动并请求：

```bash
python app.py
curl http://127.0.0.1:5000/hello
```

预期收到包含 `Hello CRM` 的 JSON 响应。该最小示例仅用于本地开发；生产环境不要使用 Flask 自带开发服务器或开启调试模式。

### 本章练习

- 停止服务后重新启动，确认你知道如何退出进程。
- 故意在错误的虚拟环境中运行一次，观察依赖缺失时的报错。

**本章验收：**`/hello` 可以正常响应，且你能确认当前终端已激活项目虚拟环境。

---

## 第 3 章：拆分职责——建立清晰的项目结构

当所有代码都塞进一个文件，路由、业务规则和数据库操作会逐渐纠缠。我们采用轻量分层，而不是为了“架构感”而过度拆分。

### 3.1 目标结构

```text
crm-practice/
├── app.py                  # 应用工厂、扩展初始化、蓝图注册
├── config.py               # 环境配置
├── extensions.py           # SQLAlchemy 扩展实例
├── models.py               # Customer 数据模型
├── customer_service.py     # 业务用例与数据库操作
├── routes.py               # HTTP 参数、状态码和响应
├── requirements.txt        # 依赖清单
├── tests/
│   ├── conftest.py         # 测试应用与 fixtures
│   └── test_customers.py   # 接口测试
└── docs/
    └── Flask-CRM-分层实战小册.md
```

### 3.2 一次请求的调用链

```text
HTTP Client
    ↓
routes.py              解析请求、基础校验、映射 HTTP 状态码
    ↓
customer_service.py    执行业务用例、读写数据库
    ↓
models.py              描述 Customer 数据结构
    ↓
SQLite                 持久化数据
```

`app.py` 负责组装应用；`extensions.py` 创建可复用的扩展对象；`models.py` 描述数据；`customer_service.py` 承担业务用例；`routes.py` 负责 HTTP 边界。

### 3.3 为什么要有 `extensions.py`

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

扩展对象先独立创建，再由应用工厂调用 `db.init_app(app)` 绑定到 Flask 应用。这种模式便于测试时创建不同配置的应用，也能减少模块之间的循环导入。

### 本章练习

给每个文件写一句“它负责什么、不负责什么”。如果某个业务判断同时散落在 Route 和 Service，思考应该把它放在哪里。

**本章验收：**你能解释每一层的职责，并画出请求调用链。

---

## 第 4 章：设计数据——用 SQLAlchemy 描述客户

### 4.1 定义 Customer 模型

在 `models.py` 中定义客户表。完整实现以仓库根目录的 `models.py` 为准。

```python
from extensions import db


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    company = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "company": self.company,
        }
```

### 4.2 理解关键字段

- `primary_key=True`：主键，唯一标识一条客户记录。
- `nullable=False`：数据库字段不允许为空。
- `unique=True`：数据库层面约束手机号唯一。
- `to_dict()`：显式选择对外返回的字段，避免直接把 ORM 对象交给 JSON 序列化器。

应用层预先查询手机号，可以给出更友好的错误信息；但它不能替代数据库唯一约束，因为并发请求可能同时通过预检查。

### 4.3 创建表与迁移的区别

应用工厂中会在应用上下文里执行 `db.create_all()`。它只创建不存在的表，**不会修改已有表结构**。模型字段变化后，应使用 Flask-Migrate/Alembic 等迁移工具管理结构演进；不要误以为再次调用 `create_all()` 就完成了迁移。

### 本章练习

1. 暂时去掉 `unique=True`，思考重复手机号风险发生在哪一层。
2. 为 `to_dict()` 增加字段前，先判断该字段是否应该对 API 客户端公开。

**本章验收：**你能说明模型字段约束、序列化方法和数据库迁移的区别。

---

## 第 5 章：编写业务——让 Service 承担用例逻辑

Service 层负责业务动作和持久化，不负责生成 Flask Response。这样同一业务逻辑未来可以被 API、后台任务或批处理复用。

### 5.1 新增客户

新增用例通常包含以下步骤：

1. 查询手机号是否已存在；
2. 构建 `Customer` 对象；
3. 将对象加入 SQLAlchemy session；
4. 提交事务；
5. 若数据库唯一约束触发 `IntegrityError`，执行 `rollback()` 并转换为业务错误。

### 5.2 列表、搜索与分页

列表查询先构建基础查询，再按关键词添加筛选条件。数据查询和总数查询必须使用相同的筛选条件，因此 `total` 表示符合条件的总记录数，而不是当前页条数。

分页偏移量：

```text
offset = (page - 1) * per_page
```

例如 `page=2`、`per_page=10`，跳过前 10 条，再取下一页数据。

### 5.3 详情、修改与删除

- 详情：按主键查找，未找到时返回 `None`，由 Route 映射为 404。
- 修改：检查新手机号是否被其他客户占用；排除当前客户自身。
- 删除：本教程采用物理删除。真实业务可能需要软删除、权限控制和关联数据保护。

完整业务实现请查看仓库中的 `customer_service.py`。阅读时重点追踪每个函数的输入、输出、数据库操作和异常行为。

### 本章练习

- 为 `create_customer()` 画出正常流程与唯一约束冲突流程。
- 解释为什么事务提交失败后要 `rollback()`。
- 用一组数据手动计算分页的 `offset`。

**本章验收：**你能在不看代码的情况下描述新增、列表、修改三个 Service 用例的主要步骤。

---

## 第 6 章：暴露接口——用 Blueprint 处理 HTTP

### 6.1 Blueprint 的职责

Blueprint 是一组可注册到 Flask 应用的路由组织单元，不是独立的 Flask 应用。客户模块使用统一前缀 `/api/customers`，并在应用工厂中注册。

```python
customer_bp = Blueprint(
    "customer",
    __name__,
    url_prefix="/api/customers",
)
```

如果忘记在 `app.py` 中调用 `app.register_blueprint(customer_bp)`，路由就不会挂载到应用上。

### 6.2 Route 层做什么

Route 负责：

- 从 JSON 或 Query 参数读取输入；
- 执行基础格式和范围校验；
- 调用对应 Service；
- 将结果转换为 JSON 和 HTTP 状态码。

Route 不应承担复杂的数据库查询和业务规则，否则容易造成逻辑重复、难以测试。

### 本章练习

在 `routes.py` 中找到每个装饰器，写出它对应的 HTTP 方法和完整路径。再追踪它调用了哪个 Service 函数。

**本章验收：**你能从任意一个 API 路由一路追踪到数据库操作。

---

## 第 7 章：规范交互——校验、状态码与异常

### 7.1 状态码约定

| 状态码 | 本项目含义 |
|---|---|
| 200 | 请求成功 |
| 201 | 客户创建成功 |
| 400 | 参数错误或业务规则冲突 |
| 404 | 客户不存在 |
| 500 | 未预期的服务器/数据库错误 |

### 7.2 校验放在哪一层

- Route：请求体是否为 JSON 对象、必填字段是否为非空字符串、分页参数是否为合法整数和正数。
- Service：手机号是否与其他客户冲突等业务规则。
- Database：通过唯一约束等机制保证最终数据完整性。

### 7.3 错误处理原则

数据库事务失败后要回滚。对客户端返回可理解且不过度暴露内部细节的信息；详细异常写入服务端日志。不要把数据库连接、SQL 或堆栈信息直接返回给客户端。

本教程中的 `PUT` 要求提供姓名和手机号，按完整更新处理。若要支持部分更新，应设计 `PATCH`，并明确字段缺省、空字符串和 `null` 的语义。

### 本章练习

为以下情况写出预期 HTTP 状态码：缺少手机号、手机号重复、客户 ID 不存在、创建成功。

**本章验收：**你能区分参数校验、业务规则、数据库约束和 HTTP 状态码。

---

## 第 8 章：动手验收——用 curl 与 pytest 验证

### 8.1 启动服务

```bash
python app.py
```

### 8.2 新增客户

```bash
curl -X POST http://127.0.0.1:5000/api/customers \
  -H "Content-Type: application/json" \
  -d '{"name":"张三","phone":"13800000000","company":"示例科技"}'
```

成功应返回 HTTP 201。请记录响应中的客户 `id`，后续请求使用该 ID。

### 8.3 列表、搜索与分页

```bash
curl "http://127.0.0.1:5000/api/customers"
curl "http://127.0.0.1:5000/api/customers?keyword=张三"
curl "http://127.0.0.1:5000/api/customers?page=1&per_page=5"
```

`page` 从 1 开始，`per_page` 最大为 100。关键词匹配姓名或公司。

### 8.4 详情、更新与删除

```bash
curl http://127.0.0.1:5000/api/customers/1

curl -X PUT http://127.0.0.1:5000/api/customers/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"李四","phone":"13800000000","company":"新公司"}'

curl -X DELETE http://127.0.0.1:5000/api/customers/1
```

示例中的 `1` 只是占位 ID，请替换为实际创建返回的 ID。

### 8.5 自动化测试

在项目根目录执行：

```bash
pytest -q
```

测试应用使用独立的 SQLite 内存数据库，避免把测试数据写入开发数据库。测试结果以实际执行输出为准；不要仅凭测试文件存在就宣称测试通过。

### 本章验收清单

- [ ] 新增客户返回 201
- [ ] 重复手机号返回 400
- [ ] 缺少姓名或手机号返回 400
- [ ] 列表搜索与分页结果符合预期
- [ ] 不存在的客户返回 404
- [ ] 修改时允许保留自己的手机号，但拒绝占用其他客户手机号
- [ ] 删除后再次查询返回 404
- [ ] `pytest -q` 全部通过

---

## 第 9 章：排查问题——从现象定位到责任层

| 现象 | 优先检查 | 常见原因 |
|---|---|---|
| `ModuleNotFoundError` | 环境与启动目录 | 未激活虚拟环境、依赖未安装、导入路径错误 |
| 数据库表不存在 | 模型导入与应用上下文 | 模型未注册，或未执行 `db.create_all()` |
| 修改模型后表结构没变化 | 数据库迁移 | `create_all()` 不会修改已有表 |
| 重复手机号导致服务器错误 | Service 与数据库约束 | 未处理 `IntegrityError` 或事务未回滚 |
| API 返回 404 | 路由注册与请求路径 | Blueprint 未注册、路径/方法/端口不匹配 |
| 分页数据为空 | Query 参数与筛选条件 | 页码越界、关键词不匹配、偏移量理解错误 |
| 测试污染开发数据 | 测试配置 | 测试没有使用独立数据库 |

### 推荐排错顺序

1. 先读完整错误信息，不要只看最后一行。
2. 判断问题发生在环境、HTTP、业务、ORM 还是数据库层。
3. 复现最小场景，减少无关变量。
4. 修复后重新运行相关接口和测试。
5. 把问题、原因、修复方式记录到自己的项目笔记中。

**本章验收：**选择一个常见故障，按“现象—定位—原因—修复—回归验证”写一份排错记录。

---

## 第 10 章：复盘与进阶——把项目讲清楚、做扎实

### 10.1 面试复盘问题

1. 为什么把业务规则放在 Service 层？
2. `db.init_app(app)` 与 `db.create_all()` 分别做什么？
3. 为什么应用层预检查不能替代数据库唯一约束？
4. 为什么列表接口需要单独统计 `total`？
5. 为什么查询不到客户应返回 404？
6. PUT 与 PATCH 的语义有什么区别？
7. 测试为什么使用独立的内存数据库？

建议先不看教程口头回答，再回到代码中验证。不能解释的部分，就是下一轮需要补齐的知识点。

### 10.2 项目经历如何准确表达

可以如实描述为：

> 我实现了一个基于 Flask 和 SQLAlchemy 的分层客户管理 API，包含客户 CRUD、关键词搜索、分页、手机号唯一性校验和基础接口测试。项目通过应用工厂与 Blueprint 组织代码，将 HTTP 处理与业务用例分离。当前版本是教学项目，尚未实现认证授权、数据库迁移和生产部署。

只保留你亲自运行、理解并验证过的内容。不要把计划中的功能写成已经完成的经验。

### 10.3 进阶路线

| 阶段 | 任务 | 练习重点 |
|---|---|---|
| 1 | 增加 PATCH | 部分更新与字段语义 |
| 2 | 增加客户跟进记录 | 一对多关系与关联查询 |
| 3 | 引入 Flask-Migrate | 数据库结构演进 |
| 4 | 扩展 pytest | 边界条件、异常路径、回归测试 |
| 5 | 增加认证与权限隔离 | 身份、授权与数据边界 |
| 6 | 切换 PostgreSQL | 配置、连接与部署差异 |
| 7 | 提供 OpenAPI 文档 | API 契约与协作 |

每次只做一个阶段。先写需求和验收条件，再改代码，最后通过测试证明功能完成。

---

## 附录：文件清单与发布前检查

### A.1 与源码的对应关系

本小册解释设计与学习路径；可运行的完整实现以仓库根目录的源码文件为准：

- `app.py`
- `config.py`
- `extensions.py`
- `models.py`
- `customer_service.py`
- `routes.py`
- `requirements.txt`
- `tests/conftest.py`
- `tests/test_customers.py`

请在学习时将教程中的概念与这些文件逐一对照。若代码版本发生变化，应同步更新教程并记录版本号。

### A.2 发布前质量检查

- [ ] 从干净环境按 README 步骤安装依赖
- [ ] 启动应用并逐个验证 API
- [ ] 执行 `pytest -q` 并保存实际结果
- [ ] 检查代码块缩进、命令换行和中文显示
- [ ] 确认教程描述与仓库当前代码一致
- [ ] 补充作者/版权主体、授权范围、版本记录与售后渠道
- [ ] 明确本资料不承诺就业、收入或生产系统适用性

### A.3 版本记录

| 版本 | 说明 |
|---|---|
| 1.0.0 | 首版：整理 Flask CRM 分层实战路径、接口验收、排错与复盘内容 |

---

**结束语**  
真正的学习成果不是“复制出一套代码”，而是你能解释每个文件为什么存在、每个异常如何处理，以及如何通过测试验证自己的判断。