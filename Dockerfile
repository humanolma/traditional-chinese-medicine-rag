FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（Streamlit 需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 先装依赖（利用 Docker 缓存层）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 给启动脚本执行权限
RUN chmod +x start.sh

# Railway 会注入 PORT 环境变量
EXPOSE $PORT

# 启动
CMD ["bash", "start.sh"]
