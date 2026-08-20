FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -e ".[dashboard]"
EXPOSE 8501
CMD ["streamlit","run","dashboard/app.py","--server.address=0.0.0.0"]
