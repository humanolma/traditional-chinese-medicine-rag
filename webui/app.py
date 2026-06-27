"""Streamlit Web UI - 中医临床智能诊疗助手
用法：streamlit run webui/app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from src.config_loader import configure_settings, _get_llm_for_eval
from src.document_processor import load_documents, build_index
from src.vector_store import persist_index, load_index
from src.rag_engine import build_query_engine, query as rag_query
from src.evaluator import evaluate, PASS_THRESHOLD

BASE_DIR = Path(__file__).resolve().parent.parent
PERSIST_DIR = BASE_DIR / "docs_emb"

# ── 页面配置 ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="中医临床智能诊疗助手", page_icon="🏥", layout="centered")


# ── 侧边栏 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🏥 中医临床智能诊疗助手")
    st.caption("基于 RAG 的中医知识问答")

    st.divider()
    st.subheader("索引管理")

    if st.button("🔄 构建向量索引", use_container_width=True, type="secondary"):
        with st.spinner("正在加载文档并构建索引..."):
            try:
                configure_settings()
                documents = load_documents(str(BASE_DIR / "data"))
                index = build_index(documents, chunk_size=256)
                persist_index(index, str(PERSIST_DIR))
                st.success("✅ 索引构建完成！")
                st.session_state.query_engine = None
                if "eval_llm" in st.session_state:
                    del st.session_state.eval_llm
            except Exception as e:
                st.error(f"构建失败：{e}")

    st.divider()
    st.subheader("功能设置")
    enable_eval = st.toggle(
        "启用回答质量评估",
        value=st.session_state.get("enable_eval", False),
        help=f"开启后自动评估忠实度和答案相关性（阈值≥{PASS_THRESHOLD}，额外消耗 LLM 调用）",
    )
    st.session_state.enable_eval = enable_eval

    if enable_eval:
        st.caption(f"✅ 评估已开启（阈值≥{PASS_THRESHOLD}）")
    else:
        st.caption("评估已关闭")

    st.divider()
    st.caption("LlamaIndex + RAG")


# ── 初始化 session_state ─────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "query_engine" not in st.session_state:
    st.session_state.query_engine = None
if "pending_question" not in st.session_state:
    st.session_state.pending_question = ""
if "enable_eval" not in st.session_state:
    st.session_state.enable_eval = False


# ── 加载索引 ────────────────────────────────────────────────────────────────
if st.session_state.query_engine is None:
    if PERSIST_DIR.exists():
        try:
            with st.spinner("正在加载向量索引..."):
                configure_settings()
                index = load_index(str(PERSIST_DIR))
                st.session_state.query_engine = build_query_engine(
                    index, similarity_top_k=5, similarity_cutoff=0.6
                )
                st.success("✅ 索引加载成功，可以开始提问！")
        except Exception as e:
            st.warning(f"索引加载失败：{e}")
    else:
        st.info("👈 请先点击左侧「构建向量索引」")


# ── 示例问题按钮 ────────────────────────────────────────────────────────────
st.caption("💡 示例问题（点击试用）")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("表虚证的临床表现", use_container_width=True):
        st.session_state.pending_question = "表虚证的临床表现是什么？"
with col2:
    if st.button("肾虚证的主要症状", use_container_width=True):
        st.session_state.pending_question = "肾虚证的主要症状有哪些？"
with col3:
    if st.button("湿热证常用治法", use_container_width=True):
        st.session_state.pending_question = "湿热证常用的治法有哪些？"


# ── 显示历史对话 ────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("📄 检索来源"):
                for i, src in enumerate(msg["sources"], 1):
                    score_str = f"相似度: {src['score']:.3f}" if src.get("score") else ""
                    st.caption(f"片段 {i}  {score_str}")
                    st.write(src["text"])
        if msg.get("eval_result"):
            er = msg["eval_result"]
            parts = []
            if er.get("faithfulness"):
                f = er["faithfulness"]
                icon = "✅" if f["pass"] else "❌"
                parts.append(f"忠实度 {f['score']}/10 {icon}")
            if er.get("relevance"):
                r = er["relevance"]
                icon = "✅" if r["pass"] else "❌"
                parts.append(f"答案相关性 {r['score']}/10 {icon}")
            if parts:
                st.caption(f"📊  {'  ·  '.join(parts)}  （阈值≥{PASS_THRESHOLD}）")


# ── 处理示例问题 ──────────────────────────────────────────────────────────
injected_input = None
if st.session_state.pending_question:
    injected_input = st.session_state.pending_question
    st.session_state.pending_question = ""


# ── 用户输入 ────────────────────────────────────────────────────────────────
user_input = st.chat_input("请输入中医临床相关问题...")
if injected_input:
    user_input = injected_input


# ── 处理查询 ────────────────────────────────────────────────────────────────
if user_input and st.session_state.query_engine is not None:

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                result = rag_query(st.session_state.query_engine, user_input)
                sources = result.get("source_nodes", [])

                # 非中医问题拦截
                is_relevant = True
                if not sources:
                    is_relevant = False
                else:
                    top_score = max(s["score"] for s in sources if s.get("score"))
                    if top_score < 0.4:
                        is_relevant = False

                if not is_relevant:
                    answer = (
                        "抱歉，我在中医临床知识库中没有找到与您问题相关的内容。\n\n"
                        "请输入与中医临床诊疗相关的问题，例如：\n"
                        "• 某种证候的临床表现\n"
                        "• 某种疾病的治疗方法\n"
                        "• 某种治法的适用症状"
                    )
                    st.write(answer)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": [],
                        "eval_result": None,
                    })
                else:
                    answer = result["answer"]
                    st.write(answer)

                    # 评估
                    eval_result = None
                    if st.session_state.get("enable_eval", False):
                        try:
                            if "eval_llm" not in st.session_state:
                                st.session_state.eval_llm = _get_llm_for_eval()
                            eval_result = evaluate(
                                st.session_state.eval_llm,
                                query=user_input,
                                answer=answer,
                                sources=sources,
                            )
                            # 简洁展示
                            parts = []
                            if eval_result.get("faithfulness"):
                                f = eval_result["faithfulness"]
                                icon = "✅" if f["pass"] else "❌"
                                parts.append(f"忠实度 {f['score']}/10 {icon}")
                            if eval_result.get("relevance"):
                                r = eval_result["relevance"]
                                icon = "✅" if r["pass"] else "❌"
                                parts.append(f"答案相关性 {r['score']}/10 {icon}")
                            if parts:
                                st.caption(f"📊  {'  ·  '.join(parts)}  （阈值≥{PASS_THRESHOLD}）")
                        except Exception:
                            pass

                    # 检索来源
                    with st.expander("📄 检索来源"):
                        for i, src in enumerate(sources, 1):
                            score_str = f"相似度: {src['score']:.3f}" if src.get("score") else ""
                            st.caption(f"片段 {i}  {score_str}")
                            st.write(src["text"])

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                        "eval_result": eval_result,
                    })

            except Exception as e:
                st.error(f"查询失败：{e}")
