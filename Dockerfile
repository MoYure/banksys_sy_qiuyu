FROM python:3.11-slim

ARG PIP_INDEX_URL=https://pypi.org/simple

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8888

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --timeout 120 -i "${PIP_INDEX_URL}" -r requirements.txt

COPY . .

EXPOSE 8888

CMD ["streamlit", "run", "app.py", "--server.port", "8888", "--server.address", "0.0.0.0"]
