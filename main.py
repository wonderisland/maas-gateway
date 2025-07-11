from typing import Dict
import aiohttp
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, logger
import uvicorn
import ssl
import json

from args import parse_args
from config import ModelConfig, init_config
from middleware import setup_middleware
from log import logger

args = parse_args()
init_config(args.config_path)
app = FastAPI(title="Maas Gateway")
# 设置中间件
setup_middleware(app, args.auth_url)

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "maas-gateway"}


@app.post("/debug/json")
async def debug_json_endpoint(request: Request):
    """调试JSON解析问题的端点"""
    try:
        body = await request.body()
        if body:
            body_str = body.decode('utf-8')
            logger.info(f"Debug - Request body length: {len(body_str)}")
            logger.info(f"Debug - Request body: {body_str}")
            
            try:
                parsed = json.loads(body_str)
                return {
                    "status": "success",
                    "message": "JSON parsed successfully",
                    "parsed_data": parsed
                }
            except json.JSONDecodeError as e:
                return {
                    "status": "error",
                    "message": "JSON parse error",
                    "error": str(e),
                    "position": e.pos,
                    "line": e.lineno,
                    "column": e.colno,
                    "body_preview": body_str[:200]
                }
        else:
            return {"status": "error", "message": "Empty request body"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}


@app.post("/{path:path}")
async def dispatch(path: str, request: Request, background_tasks: BackgroundTasks):
    """
    处理API请求
    
    中间件已经处理了：
    - 认证 (AuthMiddleware)
    - 模型验证 (ModelValidationMiddleware)
    - 日志记录 (LoggingMiddleware)
    - 错误处理 (ErrorHandlingMiddleware)
    - 速率限制 (RateLimitingMiddleware)
    """
    try:
        # 获取请求数据
        return await handle_request(request)   
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"Unhandled exception in dispatch: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def handle_request(request: Request):
    """处理流式请求"""
    uri = request.url.path
    logger.info(f"handle request: {uri}")
    
    # 获取请求header并创建可变副本
    headers = dict(request.headers)
    logger.info(f"request headers: {headers}")
    
    # 检查是否有模型配置（对于/v1/路径的请求）
    model_config = getattr(request.state, 'model_config', None)
    if model_config is None:
        # 对于非/v1/路径的请求，使用默认配置或返回错误
        raise HTTPException(status_code=400, detail="Model configuration not found")
    
    api_key = model_config.api_key
    headers["authorization"] = f"Bearer {api_key}"
    
    # 使用中间件已经解析的请求数据
    request_data = getattr(request.state, 'request_data', {})
    if not request_data:
        # 如果没有中间件解析的数据，尝试直接解析（用于非/v1/路径的请求）
        try:
            # 注意：如果中间件已经消费了body，这里可能会失败
            # 我们应该依赖中间件解析的数据
            logger.warning("No request data from middleware, using empty dict")
            request_data = {}
        except Exception as e:
            logger.error(f"Failed to parse request JSON: {e}")
            request_data = {}
    
    is_stream = request_data.get("stream", False) # 流式请求
    
    if is_stream:
        return await handle_stream_request(uri, headers, request_data, model_config)
    else:
        return await handle_block_request(uri, headers, request_data, model_config)
    

async def handle_block_request(uri: str, headers: Dict[str, str], request_data: dict, model_config: ModelConfig):
    #svc_addr = model_config.model_svc(model_config.model_name)
    svc_addr = f"https://chat.cq.uban360.com:21008/{uri}"
    print(f"handle block request to {svc_addr}")
    
    # 创建SSL上下文，跳过证书验证
    '''
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    '''
    async with aiohttp.ClientSession() as session:
        print(f"request_data: {request_data}")
        print(f"headers: {headers}")
        async with session.post(svc_addr, json=request_data, headers=headers) as response:
            print(f"response: {response}")
            if response.status == 200:
                response_data = await response.text()
                print(f"response_data: {response_data}")
                # 尝试解析为JSON，如果失败则返回原始文本
                try:
                    return json.loads(response_data)
                except json.JSONDecodeError:
                    return {"response": response_data}
            else:
                error_text = await response.text()
                raise HTTPException(status_code=response.status, detail=error_text)
            

async def handle_stream_request(uri: str, headers: Dict[str, str], request_data: dict, model_config: ModelConfig):
    pass


if __name__ == "__main__":
    
    uvicorn.run(app, host=args.host, port=args.port)