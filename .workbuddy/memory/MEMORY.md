# 基于RAG的中医临床诊疗术语问答系统 - 项目长期记忆

## 项目概述
- 基于 LlamaIndex + RAG 的中医临床诊疗术语问答系统
- 技术栈：LlamaIndex + DashScope（Qwen-Max + text-embedding-v1）+ Streamlit
- 数据：data/ 目录下的 .txt 文件（中医临床诊疗知识）
- 索引持久化：doc_emb/ 目录（5个JSON文件）

## 项目结构
```
config/settings.yml          # 配置
src/config_loader.py         # 全局Settings配置 + system_prompt + eval专用LLM
src/document_processor.py    # 文档加载 + 索引构建
src/vector_store.py          # 索引持久化/加载
src/prompt_templates.py      # 中文QA/Refine模板
src/rag_engine.py            # 检索器+后处理器+查询引擎组装
src/evaluator.py             # LLM-as-Judge 评估（faithfulness + relevance，0-10分）
webui/app.py                 # Streamlit界面
run.py                       # 启动脚本
```

## 关键技术决策
- system_prompt 注入中医助手身份约束（system角色，每轮生效）
- QA_TEMPLATE / REFINE_TEMPLATE 替换 LlamaIndex 默认英文模板
- ResponseMode.REFINE：多chunk顺序合并，质量优先
- SimilarityPostprocessor cutoff=0.6 过滤低相关检索结果
- 评估用 temperature=0.0 的独立LLM实例，确保打分确定性
- 非中医问题拦截：source_nodes为空或top_score < 0.4

## 文档产出
- 简历：C:\Users\18746\Desktop\简历_AI应用开发师.md（STAR格式，3个项目）
- 项目彻底理解指南.md：面试准备核心文档，参照ReActAgent项目指南结构
