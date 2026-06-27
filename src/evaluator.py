"""RAG 评估模块 — 评分制（0-10），阈值≥7 为通过"""
from llama_index.core.prompts import PromptTemplate

PASS_THRESHOLD = 7  # 通过阈值

_FAITHFULNESS_PROMPT = PromptTemplate(
    """请评估以下「回答」对「参考资料」的忠实程度，仅返回一个 0 到 10 的整数。

- 10：回答完全基于参考资料，无任何编造
- 7-9：回答基本忠于参考资料，个别用词略有拓展
- 4-6：回答引入了少量参考资料外信息
- 0-3：回答大量编造，与参考资料无关

【参考资料】
{context}

【回答】
{answer}

分数："""
)

_ANSWER_RELEVANCE_PROMPT = PromptTemplate(
    """请评估以下「回答」对「问题」的切题程度，仅返回一个 0 到 10 的整数。

- 10：回答完全切题，直接回应了问题
- 7-9：回答基本切题，能回答问题的核心
- 4-6：回答部分切题，但存在偏离
- 0-3：回答严重偏离，答非所问

【问题】
{query}

【回答】
{answer}

分数："""
)


def _parse_score(text: str) -> int:
    """从 LLM 返回的文本中提取整数分数"""
    import re
    match = re.search(r'\b(\d+)\b', str(text))
    if match:
        score = int(match.group(1))
        return max(0, min(10, score))
    return 5  # 解析失败默认中性分


def evaluate(llm, query: str, answer: str, sources: list) -> dict:
    """对一次 RAG 回答进行评估

    返回格式:
        {
            "faithfulness": {"score": 8, "pass": True},
            "relevance":    {"score": 7, "pass": True},
        }
    """
    result = {"faithfulness": None, "relevance": None}
    context = "\n---\n".join([s.get("text", "") for s in sources]) if sources else "（无检索来源）"

    try:
        raw = llm.predict(_FAITHFULNESS_PROMPT, context=context, answer=answer)
        score = _parse_score(raw)
        result["faithfulness"] = {"score": score, "pass": score >= PASS_THRESHOLD}
    except Exception:
        pass

    try:
        raw = llm.predict(_ANSWER_RELEVANCE_PROMPT, query=query, answer=answer)
        score = _parse_score(raw)
        result["relevance"] = {"score": score, "pass": score >= PASS_THRESHOLD}
    except Exception:
        pass

    return result
