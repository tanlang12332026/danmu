FROM node:20-slim AS build-stage

# 安装必要工具：curl 和用于弹幕/网页运行的基础库

WORKDIR /app

COPY . .

RUN npm install

RUN npm run build


FROM python:3.11.14-slim
WORKDIR /app
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY main.py .

COPY --from=build-stage /app/dist ./dist


# 注意：Vite 必须监听 0.0.0.0 才能在容器外/网络中被访问
# 修改 package.json 的 scripts: "dev": "vite --host"
CMD python main.py