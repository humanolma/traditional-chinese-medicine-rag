#!/bin/bash
# Railway 启动脚本：自动检测索引是否存在，不存在则构建，然后启动 Streamlit
set -e

echo "=== 基于RAG的中医临床诊疗术语问答系统 - 启动中 ==="

# 检查索引是否已存在
if [ -f "docs_emb/default__vector_store.json" ]; then
    echo "✅ 索引文件已存在，跳过构建"
else
    echo "📦 索引不存在，开始构建..."
    python -c "
from src.config_loader import configure_settings
from src.document_processor import load_documents, build_index
from src.vector_store import persist_index
import os

configure_settings()
documents = load_documents('data')
index = build_index(documents, chunk_size=256)
persist_index(index, 'docs_emb')
print('✅ 索引构建完成')
"
fi

# 获取 Railway 分配的端口（默认 8501）
PORT=${PORT:-8501}
echo "🚀 启动 Streamlit，端口: $PORT"

streamlit run webui/app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true
