FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY . .
RUN pip install --no-cache-dir -e "./trading_bot[ui]" python-dotenv
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app/app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
