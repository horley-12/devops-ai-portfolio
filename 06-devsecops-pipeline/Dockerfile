FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY lambda_function.py .
CMD ["python", "lambda_function.py"]
