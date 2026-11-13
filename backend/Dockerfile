ARG BASE_REGISTRY=docker.m.daocloud.io/library
FROM ${BASE_REGISTRY}/python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir --index-url https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
COPY . ./

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-"]
