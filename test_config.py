#!/usr/bin/env python3
"""
测试配置文件解析功能
"""

from config import load_config, get_model_config_by_name, ServerConfig, ModelConfig


def test_config_parsing():
    """测试配置文件解析"""
    try:
        # 加载配置文件
        server_config = load_config("config.json")
        
        print("✅ 配置文件解析成功!")
        print(f"📋 服务器配置: {server_config}")
        print(f"🔢 模型配置数量: {len(server_config.model_config)}")
        
        # 打印所有模型配置
        for i, (model_name, model_config) in enumerate(server_config.model_config.items(), 1):
            print(f"\n📝 模型配置 {i}:")
            print(f"   模型名称: {model_name}")
            print(f"   应用名称: {model_config.app_name}")
            print(f"   API密钥: {model_config.api_key[:8]}...")
        
        # 测试根据模型名称查找配置
        print("\n🔍 测试模型查找功能:")
        
        # 查找存在的模型
        deepseek_chat = get_model_config_by_name(server_config, "deepseek-chat")
        print(f"✅ 找到模型 'deepseek-chat': {deepseek_chat.app_name}")
        
        deepseek_reasoner = get_model_config_by_name(server_config, "deepseek-reasoner")
        print(f"✅ 找到模型 'deepseek-reasoner': {deepseek_reasoner.app_name}")
        
        # 测试查找不存在的模型
        try:
            get_model_config_by_name(server_config, "non-existent-model")
        except ValueError as e:
            print(f"✅ 正确捕获错误: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置文件解析失败: {e}")
        return False


def test_config_structure():
    """测试配置结构"""
    print("\n🏗️  测试配置结构:")
    
    # 创建测试配置
    test_model_configs = {
        "test-model-1": ModelConfig(
            model_name="test-model-1",
            app_name="test-app-1", 
            api_key="test-key-1"
        ),
        "test-model-2": ModelConfig(
            model_name="test-model-2",
            app_name="test-app-2",
            api_key="test-key-2"
        )
    }
    
    test_server_config = ServerConfig(model_config=test_model_configs)
    
    print(f"✅ 测试配置创建成功")
    print(f"📊 测试配置包含 {len(test_server_config.model_config)} 个模型")
    
    # 测试从字典创建
    test_dict = {
        "model_config": [
            {
                "model_name": "dict-model-1",
                "app_name": "dict-app-1",
                "api_key": "dict-key-1"
            }
        ]
    }
    
    dict_server_config = ServerConfig.from_dict(test_dict)
    print(f"✅ 从字典创建配置成功: {list(dict_server_config.model_config.keys())[0]}")


if __name__ == "__main__":
    print("🚀 开始测试配置文件解析功能...\n")
    
    # 测试配置解析
    success = test_config_parsing()
    
    # 测试配置结构
    test_config_structure()
    
    if success:
        print("\n🎉 所有测试通过!")
    else:
        print("\n💥 测试失败!") 