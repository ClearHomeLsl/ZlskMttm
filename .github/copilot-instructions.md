# ZlskMttm 的 Copilot 指令

## 项目概述
ZlskMttm 是一个基于 Django 的金融交易平台 Web 应用程序，具备用户管理、AliPay 集成和实时 XAUUSD（黄金）价格数据功能。它使用 MySQL 存储持久数据，使用 Redis 进行缓存/会话存储。

## 架构
- **模块化应用**：`apps/users`（自定义 UserProfile 模型）、`apps/aliyun_pay`（支付订单）、`apps/kline`（K线数据）
- **工具**：`utils/` 包含支付逻辑、阿里云短信、数据库配置和价格获取脚本
- **前端**：`templates/` 中的基本 HTML 模板、`static/` 中的静态文件，通过 JS 更新图表

## 关键模式
- **用户模型**：使用 `UserProfile` 而非 Django 的 `AbstractUser`（见 `apps/users/models.py`）
- **支付**：通过 `utils/pay.py` 和 `apps/aliyun_pay/` 集成 AliPay
- **实时数据**：`utils/get_price_script.py` 中的 APScheduler 每 2-4 秒获取价格，存储在 Redis 中
- **环境**：使用 `django-environ` 处理密钥；默认值在 `settings.py` 和 `utils/DBMysql.py` 中
- **安全**：通过 `utils/middleware.py` 全局禁用 CSRF（生产环境需审查）

## 工作流程
- **开发**：`python manage.py runserver`（DEBUG=True）
- **数据库**：`python manage.py makemigrations && python manage.py migrate`
- **价格更新**：运行 `utils/get_price_script.py` 启动调度器
- **部署**：`uwsgi.ini` 中的 uWSGI 配置用于生产

## 约定
- **语言**：中文（zh-hans），上海时区
- **依赖**：在 `requirements.txt` 中列出；包括 `alibabacloud-dysmsapi20170525` 用于短信、`alipay` 用于支付
- **URLs**：API 端点在 `/api/` 下（例如 `/api/user_login/`、`/api/kline/`）
- **数据流**：价格缓存在 Redis 键如 `m1_XAUUSD_price` 中；订单通过模型存储在 MySQL 中

## 示例
- **用户注册**：POST 到 `/api/user_register/`，包含 username、mobile、password
- **支付创建**：在 `utils/pay.py` 中使用 `AlipayPayment.create_payment()`
- **价格检索**：GET `/api/kline/` 获取来自 Redis 的 K线数据</content>
<parameter name="filePath">c:\Users\77\Desktop\AllProject\ZlskMttm\.github\copilot-instructions.md