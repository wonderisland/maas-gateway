# Maas Gateway

一个基于FastAPI的模型服务网关，支持多种AI模型的统一接入和管理。

## 功能特性

### 🔐 认证中间件 (AuthMiddleware)
- 统一的用户认证和授权
- 支持跳过特定路径的认证（如健康检查）
- 自动处理认证失败的情况

### 📝 日志中间件 (LoggingMiddleware)
- 自动记录所有请求和响应
- 计算请求处理时间
- 在响应头中添加处理时间信息

### 🔍 模型验证中间件 (ModelValidationMiddleware)
- 验证请求中的模型名称
- 自动从配置中获取模型配置
- 将验证后的模型配置传递给路由处理器

### 🚨 错误处理中间件 (ErrorHandlingMiddleware)
- 统一处理未捕获的异常
- 提供友好的错误响应
- 记录详细的错误日志

### ⏱️ 速率限制中间件 (RateLimitingMiddleware)
- 基于客户端IP的请求限制
- 可配置的速率限制参数
- 自动重置计数器

### 🌐 CORS中间件 (CORSMiddleware)
- 支持跨域请求
- 自动添加CORS响应头
- 可配置的CORS策略

## 安装和运行

### 1. 安装依赖
```bash
pip install fastapi uvicorn aiohttp
```

### 2. 配置
创建 `config.json` 文件：
```json
{
    "model_config": [
        {
            "model_name": "deepseek-chat",
            "app_name": "deepseek-v3-0324",
            "api_key": "your-api-key"
        },
        {
            "model_name": "deepseek-reasoner",
            "app_name": "deepseek-r1",
            "api_key": "your-api-key"
        }
    ]
}
```

### 3. 运行服务
```bash
python main.py \
    --auth-url http://auth-service:8080 \
    --base-url https://api.deepseek.com \
    --config-path config.json \
    --host 0.0.0.0 \
    --port 8000
```

## API 使用

### 健康检查
```bash
curl http://localhost:8000/health
```

### 聊天完成
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "model": "deepseek-chat",
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ]
  }'
```

## 中间件配置

### 速率限制配置
在 `middleware.py` 中修改 `RateLimitingMiddleware` 的参数：
```python
self.max_requests = 100  # 每分钟最大请求数
self.reset_interval = 60  # 重置间隔（秒）
```

### 认证跳过路径
在 `AuthMiddleware` 中修改跳过认证的路径：
```python
if request.url.path in ["/health", "/docs", "/openapi.json"]:
    return await call_next(request)
```

## 测试

### 运行配置测试
```bash
python test_config.py
```

### 运行中间件测试
```bash
python test_middleware.py
```

## 项目结构

```
maas-gateway/
├── main.py              # 主应用入口
├── config.py            # 配置管理
├── middleware.py        # 中间件实现
├── auth_proxy.py        # 认证代理
├── args.py              # 命令行参数
├── config.json          # 配置文件
├── test_config.py       # 配置测试
├── test_middleware.py   # 中间件测试
└── README.md           # 项目文档
```

## 开发

### 添加新的中间件
1. 在 `middleware.py` 中创建新的中间件类
2. 实现 `__call__` 方法
3. 在 `setup_middleware` 函数中注册中间件

### 自定义错误处理
在 `ErrorHandlingMiddleware` 中添加特定的异常处理逻辑。

### 扩展模型支持
在 `config.json` 中添加新的模型配置，中间件会自动处理验证。

## 监控和日志

服务会自动记录以下信息：
- 请求和响应日志
- 处理时间
- 错误详情
- 认证状态

所有日志都包含时间戳和请求ID，便于问题排查。
