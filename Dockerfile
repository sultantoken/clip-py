FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg curl && apt-get clean

RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp \
    -o /usr/local/bin/yt-dlp && chmod a+rx /usr/local/bin/yt-dlp

RUN pip install flask requests

WORKDIR /app
COPY app.py .

EXPOSE 5000
CMD ["python", "app.py"]
