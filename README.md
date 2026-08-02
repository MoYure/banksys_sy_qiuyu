# banksys_sy_qiuyu

Bank marketing analytics and subscription prediction app built with Python 3.11 and Streamlit.

## Features

- Interactive data analysis for the CSV files in `data/`.
- Reserved online prediction workflow for a later offline-trained model.
- CI checks with ruff, pytest coverage, and Docker build.
- CD workflow that deploys the Streamlit container to port `8888` with fallback through `8898`.

## Local Setup

```bash
conda create -y -n banksys_sy_qiuyu python=3.11
conda activate banksys_sy_qiuyu
pip install -r requirements-dev.txt
```

## Run the App

```bash
streamlit run app.py --server.port 8888
```

Open `http://localhost:8888`.

## Test and Lint

```bash
ruff format --check .
ruff check .
pytest --cov=src --cov-fail-under=80
```

## Docker

```bash
docker build -t banksys_sy_qiuyu:latest .
docker run --rm -p 8888:8888 banksys_sy_qiuyu:latest
```

## Data Note

`data/train.csv` contains the `subscribe` target column. `data/test.csv` does not contain `subscribe`, so the training module must use `data/train.csv` as the labeled training source before model work begins.

## Deployment Secrets

GitHub Actions CD expects these repository secrets:

- `SSH_PRIVATE_KEY`
- `SSH_HOST`
- `SSH_USER`
