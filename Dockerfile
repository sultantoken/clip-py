FROM python:3.11-slim

# Install ffmpeg, curl, unzip
RUN apt-get update && apt-get install -y ffmpeg curl unzip && apt-get clean

# Install latest yt-dlp binary (not pip version — always up to date)
RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp && \
    chmod a+rx /usr/local/bin/yt-dlp

# Install deno (JS runtime required by yt-dlp for YouTube)
RUN curl -fsSL https://deno.land/install.sh | sh
ENV DENO_INSTALL="/root/.deno"
ENV PATH="${DENO_INSTALL}/bin:${PATH}"

# Install flask
RUN pip install flask requests

WORKDIR /app
COPY app.py .

EXPOSE 5000
CMD ["python", "app.py"]
