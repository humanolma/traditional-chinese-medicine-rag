"""文档处理模块 - 加载文档并构建向量索引"""
from pathlib import Path

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter


def load_documents(data_dir: str = "./data"):
    """加载 ./data 目录下的 .txt 文档"""
    documents = SimpleDirectoryReader(
        data_dir,
        required_exts=[".txt"],
    ).load_data()
    return documents


def build_index(documents, chunk_size: int = 256):
    """构建向量索引"""
    index = VectorStoreIndex.from_documents(
        documents,
        transformations=[SentenceSplitter(chunk_size=chunk_size)],
    )
    return index
