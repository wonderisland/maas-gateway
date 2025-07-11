#!/usr/bin/env python3
"""
测试middleware功能
"""

import asyncio
import json
from unittest.mock import Mock, AsyncMock
from fastapi import Request
from fastapi.responses import JSONResponse

from middleware import (
    AuthMiddleware, 
    LoggingMiddleware, 
    ModelValidationMiddleware,
    ErrorHandlingMiddleware,
    RateLimitingMiddleware,
    CORSMiddleware
)
from config import init_config


async def test_auth_middleware():
    """测试认证中间件"""
    print("🔐 测试认证中间件...")
    
    # 创建模拟的认证中间件
    auth_middleware = AuthMiddleware("http://auth-service:8080")
    
    # 模拟请求
    mock_request = Mock()
    mock_request.url.path = "/v1/chat/completions"
    
    # 模拟call_next函数
    async def mock_call_next(request):
        return JSONResponse(content={"status": "success"})
    
    try:
        response = await auth_middleware(mock_request, mock_call_next)
        print("✅ 认证中间件测试通过")
    except Exception as e:
        print(f"❌ 认证中间件测试失败: {e}")


async def test_logging_middleware():
    """测试日志中间件"""
    print("\n📝 测试日志中间件...")
    
    logging_middleware = LoggingMiddleware()
    
    # 模拟请求
    mock_request = Mock()
    mock_request.method = "POST"
    mock_request.url.path = "/v1/chat/completions"
    
    # 模拟call_next函数
    async def mock_call_next(request):
        return JSONResponse(content={"status": "success"})
    
    try:
        response = await logging_middleware(mock_request, mock_call_next)
        print("✅ 日志中间件测试通过")
        print(f"   响应头包含处理时间: {response.headers.get('X-Process-Time')}")
    except Exception as e:
        print(f"❌ 日志中间件测试失败: {e}")


async def test_model_validation_middleware():
    """测试模型验证中间件"""
    print("\n🔍 测试模型验证中间件...")
    
    # 初始化配置
    init_config("config.json")
    
    model_validation_middleware = ModelValidationMiddleware()
    
    # 测试有效请求
    mock_request = Mock()
    mock_request.url.path = "/v1/chat/completions"
    mock_request.body = AsyncMock(return_value=json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "Hello"}]
    }).encode())
    
    async def mock_call_next(request):
        return JSONResponse(content={"status": "success"})
    
    try:
        response = await model_validation_middleware(mock_request, mock_call_next)
        print("✅ 模型验证中间件测试通过")
    except Exception as e:
        print(f"❌ 模型验证中间件测试失败: {e}")
    
    # 测试无效模型
    mock_request.body = AsyncMock(return_value=json.dumps({
        "model": "invalid-model",
        "messages": [{"role": "user", "content": "Hello"}]
    }).encode())
    
    try:
        response = await model_validation_middleware(mock_request, mock_call_next)
        if response.status_code == 400:
            print("✅ 无效模型验证测试通过")
        else:
            print("❌ 无效模型验证测试失败")
    except Exception as e:
        print(f"❌ 无效模型验证测试失败: {e}")


async def test_rate_limiting_middleware():
    """测试速率限制中间件"""
    print("\n⏱️  测试速率限制中间件...")
    
    rate_limiting_middleware = RateLimitingMiddleware()
    
    # 模拟请求
    mock_request = Mock()
    mock_request.client.host = "127.0.0.1"
    
    async def mock_call_next(request):
        return JSONResponse(content={"status": "success"})
    
    try:
        # 测试正常请求
        response = await rate_limiting_middleware(mock_request, mock_call_next)
        print("✅ 速率限制中间件测试通过")
    except Exception as e:
        print(f"❌ 速率限制中间件测试失败: {e}")


async def test_cors_middleware():
    """测试CORS中间件"""
    print("\n🌐 测试CORS中间件...")
    
    cors_middleware = CORSMiddleware()
    
    # 模拟请求
    mock_request = Mock()
    
    async def mock_call_next(request):
        return JSONResponse(content={"status": "success"})
    
    try:
        response = await cors_middleware(mock_request, mock_call_next)
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods", 
            "Access-Control-Allow-Headers"
        ]
        
        if all(header in response.headers for header in cors_headers):
            print("✅ CORS中间件测试通过")
        else:
            print("❌ CORS中间件测试失败")
    except Exception as e:
        print(f"❌ CORS中间件测试失败: {e}")


async def test_error_handling_middleware():
    """测试错误处理中间件"""
    print("\n🚨 测试错误处理中间件...")
    
    error_handling_middleware = ErrorHandlingMiddleware()
    
    # 模拟请求
    mock_request = Mock()
    
    # 测试正常情况
    async def mock_call_next_success(request):
        return JSONResponse(content={"status": "success"})
    
    try:
        response = await error_handling_middleware(mock_request, mock_call_next_success)
        print("✅ 错误处理中间件正常情况测试通过")
    except Exception as e:
        print(f"❌ 错误处理中间件正常情况测试失败: {e}")
    
    # 测试异常情况
    async def mock_call_next_error(request):
        raise Exception("测试异常")
    
    try:
        response = await error_handling_middleware(mock_request, mock_call_next_error)
        if response.status_code == 500:
            print("✅ 错误处理中间件异常情况测试通过")
        else:
            print("❌ 错误处理中间件异常情况测试失败")
    except Exception as e:
        print(f"❌ 错误处理中间件异常情况测试失败: {e}")


async def main():
    """运行所有测试"""
    print("🚀 开始测试middleware功能...\n")
    
    await test_auth_middleware()
    await test_logging_middleware()
    await test_model_validation_middleware()
    await test_rate_limiting_middleware()
    await test_cors_middleware()
    await test_error_handling_middleware()
    
    print("\n🎉 所有middleware测试完成!")


if __name__ == "__main__":
    asyncio.run(main()) 