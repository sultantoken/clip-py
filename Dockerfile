FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg curl && \
    pip install flask yt-dlp && \
    apt-get clean
WORKDIR /app
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
