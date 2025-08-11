FROM python:3.11
WORKDIR /app
RUN pip install flask
COPY . .
EXPOSE 5001
CMD ["python", "mock_drugbank.py"]