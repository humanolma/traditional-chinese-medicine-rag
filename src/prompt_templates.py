"""Prompt 模板模块 - 中文 QA / Refine 模板（与 index_api.ipynb Cell 61 一致）"""
from llama_index.core import PromptTemplate

# 中文 QA 模板（替换 LlamaIndex 默认英文模板）
QA_TEMPLATE = (
    "上下文信息如下。\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "请根据上下文信息而不是先验知识来回答以下的查询。"
    "作为一个中医临床诊疗助手，你的回答要尽可能严谨、专业，使用中医术语。\n"
    "Query: {query_str}\n"
    "Answer: "
)

# 中文 Refine 模板
REFINE_TEMPLATE = (
    "原始查询如下：{query_str}\n"
    "我们提供了现有答案：{existing_answer}\n"
    "我们有机会通过下面的更多上下文来完善现有答案（仅在需要时）。\n"
    "------------\n"
    "{context_msg}\n"
    "------------\n"
    "考虑到新的上下文，优化原始答案以更好地回答查询。如果上下文没有用，请返回原始答案。\n"
    "Refined Answer: "
)

def get_qa_template():
    return PromptTemplate(QA_TEMPLATE)

def get_refine_template():
    return PromptTemplate(REFINE_TEMPLATE)
