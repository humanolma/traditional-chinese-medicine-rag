"""向量索引持久化模块（与 index_api.ipynb Cell 40-43 一致）"""
from pathlib import Path

from llama_index.core import StorageContext, load_index_from_storage


def persist_index(index, persist_dir: str = "./docs_emb"):
    """将向量索引持久化到磁盘（与 index_api.ipynb Cell 40 一致）"""
    Path(persist_dir).mkdir(exist_ok=True)
    index.storage_context.persist(persist_dir=persist_dir)


def load_index(persist_dir: str = "./docs_emb"):
    """从磁盘加载向量索引（与 index_api.ipynb Cell 43 一致）"""
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    index = load_index_from_storage(storage_context)
    return index
