FROM python:3.10

# 设置工作目录
WORKDIR /usr/src/app

# 设置时区为上海
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# 先复制requirements.txt到容器中的工作目录
COPY requirements.txt .

# 升级pip并安装依赖
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# 安装supervisor
RUN pip install supervisor

# 将当前目录内容复制到容器中的工作目录
COPY . .

# 将supervisord配置文件复制到容器中
COPY supervisord.conf /etc/supervisord.conf

# 暴露端口8000供外部访问
EXPOSE 8000

# 使用supervisord启动服务
# CMD ["/usr/local/bin/supervisord", "-c", "/etc/supervisord.conf"]

# HEALTHCHECK 指令
# --interval=30s: 健康检查的间隔时间是30秒。
#--timeout=30s: 如果健康检查命令在30秒内没有完成，则认为超时。
#--start-period=5s: 在容器启动后的前5秒内，健康检查的失败将不会被计入失败次数。
#--retries=3: 在认定容器不健康之前，允许检查失败的次数是3次。
#HEALTHCHECK --interval=5s --timeout=180s --retries=36 --start-period=10s \
#    CMD curl -fs https://api.gggggun.cn || exit 1
