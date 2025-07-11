from dataclasses import dataclass
from typing import Dict
import json
from pathlib import Path


@dataclass
class ModelConfig:
    model_name: str
    svc_name: str
    svc_port: int
    api_key: str
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ModelConfig':
        """从字典创建ModelConfig实例"""
        return cls(
            model_name=data['model_name'],  
            svc_name=data['svc_name'],
            svc_port=data['svc_port'],
            api_key=data['api_key']
        )
    @classmethod
    def from_model_name(cls, model_name: str) -> 'ModelConfig':
        """根据模型名称获取ModelConfig"""
        return cls(
            model_name=model_name,
            svc_name=model_name,
            svc_port=9002,
            api_key=model_name)
        
    def model_svc(self, model_name: str) -> str:
        """根据模型名称获取服务名称"""
        svc_addr = f"{self.svc_name}-svc.maas.svc.cluster.local:{self.svc_port}"
        
        return svc_addr
        
        
        
    
@dataclass
class ServerConfig:
    model_config: Dict[str, ModelConfig]
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ServerConfig':
        """从字典创建ServerConfig实例"""
        model_configs = {}
        for config in data['model_config']:
            model_config = ModelConfig.from_dict(config)
            model_configs[model_config.model_name] = model_config
        return cls(model_config=model_configs)
    
    
def load_config(config_path: str) -> ServerConfig:
    """
    从JSON文件加载配置并解析为ServerConfig对象
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        ServerConfig: 解析后的配置对象
        
    Raises:
        FileNotFoundError: 配置文件不存在
        json.JSONDecodeError: JSON格式错误
        KeyError: 缺少必需的配置字段
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"JSON格式错误: {e}", e.doc, e.pos)
    
    try:
        return ServerConfig.from_dict(config_data)
    except KeyError as e:
        raise KeyError(f"配置文件缺少必需字段: {e}")
    except Exception as e:
        raise Exception(f"解析配置文件时出错: {e}")


def get_model_config_by_name(server_config: ServerConfig, model_name: str) -> ModelConfig:
    """
    根据模型名称获取对应的ModelConfig
    
    Args:
        server_config: 服务器配置对象
        model_name: 模型名称
        
    Returns:
        ModelConfig: 匹配的模型配置
        
    Raises:
        ValueError: 未找到指定的模型配置
    """
    if model_name in server_config.model_config:
        return server_config.model_config[model_name]
    
    available_models = list(server_config.model_config.keys())
    raise ValueError(f"未找到模型 '{model_name}'，可用模型: {available_models}")

server_config = None

def init_config(config_path: str):
    global server_config
    server_config = load_config(config_path)
    print(f"server_config: {server_config}")
    
    
def get_server_config() -> ServerConfig:
    global server_config
    return server_config
    


if __name__ == "__main__":
    init_config("config.json")
    print(server_config)
