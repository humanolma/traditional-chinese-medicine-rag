"""RAG 查询引擎模块（与 index_api.ipynb Cell 34, 58, 61 一致）"""
from llama_index.core import get_response_synthesizer
from llama_index.core.indices.vector_store import VectorIndexRetriever
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import ResponseMode

from .prompt_templates import get_qa_template, get_refine_template


def build_query_engine(index, similarity_top_k: int = 5, similarity_cutoff: float = None):
    """构建查询引擎（与 index_api.ipynb Cell 58 一致，支持 SimilarityPostprocessor + Refine）

    Args:
        index: 向量索引
        similarity_top_k: 检索返回 Top-K=5
        similarity_cutoff: 相似度过滤阈值（默认None，不过滤）
    """
    # 构建 retriever
    retriever = VectorIndexRetriever(index=index, similarity_top_k=similarity_top_k)

    # 构建 response synthesizer（Refine 模式，与 notebook Cell 58 一致）
    response_synthesizer = get_response_synthesizer(response_mode=ResponseMode.REFINE)

    # 构建 node_postprocessors
    node_postprocessors = []
    if similarity_cutoff is not None:
        node_postprocessors.append(SimilarityPostprocessor(similarity_cutoff=similarity_cutoff))

    # 构建查询引擎
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=response_synthesizer,
        node_postprocessors=node_postprocessors,
    )

    # 更新为中文 Prompt 模板（与 index_api.ipynb Cell 61 一致）
    query_engine.update_prompts({
        "response_synthesizer:text_qa_template": get_qa_template(),
        "response_synthesizer:refine_template": get_refine_template(),
    })

    return query_engine


def query(query_engine, query_text: str):
    """执行查询（与 index_api.ipynb Cell 36 一致）

    Returns:
        dict: {"answer": str, "source_nodes": list}
    """
    response = query_engine.query(query_text)

    result = {
        "answer": str(response),
        "source_nodes": [],
    }

    if hasattr(response, "source_nodes"):
        for node in response.source_nodes:
            result["source_nodes"].append({
                "text": node.node.get_content()[:300],
                "score": float(node.score) if node.score else None,
            })

    return result
