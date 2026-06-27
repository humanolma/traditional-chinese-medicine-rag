"""文档处理模块 - 加载文档并构建向量索引（与 index_api.ipynb Cell 29-31 一致）"""
from pathlib import Path

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter


def load_documents(data_dir: str = "./data"):
    """加载 ./data 目录下的 .txt 文档（与 index_api.ipynb Cell 29 一致）"""
    documents = SimpleDirectoryReader(
        data_dir,
        required_exts=[".txt"],
    ).load_data()
    return documents


def build_index(documents, chunk_size: int = 256):
    """构建向量索引（与 index_api.ipynb Cell 31 一致）"""
    index = VectorStoreIndex.from_documents(
        documents,
        transformations=[SentenceSplitter(chunk_size=chunk_size)],
    )
    return index
