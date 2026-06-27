"""配置加载模块 - 读取 API Key 并配置全局 Settings"""
import os
from pathlib import Path

from llama_index.core import Settings
from llama_index.llms.dashscope import DashScope, DashScopeGenerationModels
from llama_index.embeddings.dashscope import DashScopeEmbedding, DashScopeTextEmbeddingModels

BASE_DIR = Path(__file__).resolve().parent.parent


def load_api_key():
    """从 .env 文件加载环境变量（不依赖 python-dotenv）"""
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()


def configure_settings():
    """配置全局 LLM 和 Embedding 模型（与 index_api.ipynb Cell 25-26 一致）"""
    load_api_key()

    # 设置 system prompt（真正作为 system role 消息发送）
    Settings.system_prompt = (
        "你是一个专业的中医临床诊疗助手。"
        "你只能根据提供的参考资料回答用户问题，严禁使用先验知识或编造内容。"
        "你的回答应严谨、专业，使用规范的中医术语。"
        "如果用户询问与中医临床无关的问题，请礼貌地告知你无法回答。"
    )

    Settings.llm = DashScope(
        model_name=DashScopeGenerationModels.QWEN_MAX,
        api_key=os.getenv("DASHSCOPE_API_KEY"),
    )
    Settings.embed_model = DashScopeEmbedding(
        model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V1,
    )


def _get_llm_for_eval():
    """获取用于评估的 LLM 实例（轻量，不修改全局 Settings）"""
    load_api_key()
    return DashScope(
        model_name=DashScopeGenerationModels.QWEN_MAX,
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        temperature=0.0,   # 评估需要确定性输出
    )
