import time
import logging
from typing import Callable, Dict, Any
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
import json
from config import get_server_config, get_model_config_by_name
from log import logger

# 配置日志


class AuthMiddleware:
    """认证中间件"""
    
    def __init__(self, auth_url: str):
        self.auth_url = auth_url
        from auth_proxy import AuthProxy
        self.auth_proxy = AuthProxy(auth_url)
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """处理认证"""
        try:
            # 跳过健康检查等不需要认证的路径
            if request.url.path in ["/health", "/docs"]:
                return await call_next(request)
            
            # 执行认证
            self.auth_proxy.auth(request)
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"认证失败: {e}")
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication failed", "detail": str(e)}
            )


class LoggingMiddleware:
    """日志记录中间件"""
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 记录请求信息
        logger.info(f"收到请求: {request.method} {request.url.path}")
        
        # 处理请求
        response = await call_next(request)
        
        # 记录响应信息
        process_time = time.time() - start_time
        logger.info(f"请求完成: {request.method} {request.url.path} - 状态码: {response.status_code} - 耗时: {process_time:.3f}s")
        
        # 添加处理时间到响应头
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class ErrorHandlingMiddleware:
    """错误处理中间件"""
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except HTTPException:
            # 重新抛出HTTP异常
            raise
        except Exception as e:
            logger.error(f"未处理的异常: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error", "detail": str(e)}
            )


class RateLimitingMiddleware:
    """速率限制中间件"""
    
    def __init__(self):
        self.request_counts: Dict[str, int] = {}
        self.last_reset = time.time()
        self.max_requests = 100  # 每分钟最大请求数
        self.reset_interval = 60  # 重置间隔（秒）
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        # 获取客户端IP
        client_ip = request.client.host if request.client else "unknown"
        
        # 检查是否需要重置计数器
        current_time = time.time()
        if current_time - self.last_reset > self.reset_interval:
            self.request_counts.clear()
            self.last_reset = current_time
        
        # 检查速率限制
        if client_ip in self.request_counts:
            if self.request_counts[client_ip] >= self.max_requests:
                return JSONResponse(
                    status_code=429,
                    content={"error": "Rate limit exceeded", "detail": "Too many requests"}
                )
            self.request_counts[client_ip] += 1
        else:
            self.request_counts[client_ip] = 1
        
        return await call_next(request)


class CORSMiddleware:
    """CORS中间件"""
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # 添加CORS头
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        
        return response


def setup_middleware(app, auth_url: str):
    """设置所有中间件"""
    
    # 添加中间件（注意顺序很重要）
    #app.add_middleware(ErrorHandlingMiddleware)
    
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 记录请求信息
        logger.info(f"收到请求: {request.method} {request.url.path}")
        
        # 处理请求
        response = await call_next(request)
        
        # 记录响应信息
        process_time = time.time() - start_time
        logger.info(f"请求完成: {request.method} {request.url.path} - 状态码: {response.status_code} - 耗时: {process_time:.3f}s")
        
        # 添加处理时间到响应头
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    @app.middleware("http")
    async def model_validation_middleware(request: Request, call_next: Callable) -> Response:
        # 只对API请求进行模型验证
        if request.url.path.startswith("/v1/"):
            try:
                # 获取请求体
                body = await request.body()
                if body:
                    try:
                        # 尝试解码为字符串，然后解析JSON
                        body_str = body.decode('utf-8')
                        logger.info(f"Request body length: {len(body_str)}")
                        logger.info(f"Request body (first 500 chars): {body_str[:500]}")
                        
                        # 检查是否有明显的JSON格式问题
                        if body_str.strip() == "":
                            logger.error("Empty request body")
                            return JSONResponse(
                                status_code=400,
                                content={"error": "Empty request body"}
                            )
                        
                        # 检查是否以 { 开头
                        if not body_str.strip().startswith('{'):
                            logger.error(f"Request body does not start with '{{': {body_str[:100]}")
                            return JSONResponse(
                                status_code=400,
                                content={"error": "Request body must be valid JSON object"}
                            )
                        
                        request_data = json.loads(body_str)
                        print(f"request_data: {request_data}")
                        # 存储解析后的请求数据到request.state中
                        request.state.request_data = request_data.copy()
                        # 存储原始body字符串以便调试
                        request.state.request_body_str = body_str
                        
                        model_name = request_data.get("model")
                        
                        if not model_name:
                            return JSONResponse(
                                status_code=400,
                                content={"error": "Model name is required"}
                            )
                        
                        # 验证模型是否存在
                        try:
                            server_config = get_server_config()
                            print(f"model_name: {model_name}, server_config: {server_config}")
                            model_config = get_model_config_by_name(server_config, model_name)
                            # 将模型配置添加到请求状态中
                            request.state.model_config = model_config
                        except ValueError as e:
                            return JSONResponse(
                                status_code=400,
                                content={"error": f"Invalid model: {str(e)}"}
                            )
                    except UnicodeDecodeError as e:
                        logger.error(f"Failed to decode request body as UTF-8: {e}")
                        logger.error(f"Body bytes: {body[:100]}")
                        return JSONResponse(
                            status_code=400,
                            content={"error": "Invalid request encoding", "detail": "Request body must be valid UTF-8"}
                        )
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {e}")
                        logger.error(f"Error position: {e.pos}")
                        logger.error(f"Body around error: {body_str[max(0, e.pos-50):e.pos+50]}")
                        return JSONResponse(
                            status_code=400,
                            content={
                                "error": "Invalid JSON in request body",
                                "detail": f"JSON decode error: {str(e)}",
                                "position": e.pos if hasattr(e, 'pos') else None
                            }
                        )
                
            except Exception as e:
                logger.error(f"模型验证失败: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": "Internal server error during model validation", "detail": str(e)}
                )
        
        return await call_next(request)
    
    #app.add_middleware(RateLimitingMiddleware)
    # app.add_middleware(AuthMiddleware, auth_url=auth_url)
    #app.add_middleware(CORSMiddleware)