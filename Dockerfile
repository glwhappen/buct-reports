# 选择一个合适的 Python 镜像作为基础
FROM selenium/standalone-chrome

# 安装 Python 和必要的依赖
USER root

RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y python3-pip &&\
    # 清理APT缓存
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 先复制 requirements.txt 并安装 Python 依赖
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目的其他文件
COPY . /app

# 设置默认启动命令为运行 main.py
CMD ["python3", "main.py"]
#CMD ["tail", "-f", "/dev/null"]