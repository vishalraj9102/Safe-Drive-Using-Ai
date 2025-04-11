FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN apk add --no-cache gcc musl-dev libffi-dev && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=run.py

CMD ["flask", "run", "--host=0.0.0.0"]
