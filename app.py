from flask import Flask, request, send_file, jsonify
import subprocess, os, uuid, requests, re

app = Flask(__name__)
DOWNLOAD_DIR = '/tmp/clips'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

INVIDIOUS_URL = os.environ.get('INVIDIOUS_URL', 'http://invidious:3000')

def get_video_id(url):
    match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
    return match.group(1) if match else None

def get_direct_url(video_id):
    resp = requests.get(
        f'{INVIDIOUS_URL}/api/v1/videos/{video_id}',
        timeout=30
    )
    data = resp.json()
    formats = [f for f in data.get('formatStreams', [])
               if f.get('container') == 'mp4']
    if not formats:
        raise Exception('No mp4 formats found. Invidious response: ' + str(data)[:300])
    return formats[-1]['url']

@app.route('/clip', methods=['POST'])
def clip():
    data     = request.json
    url      = str(data.get('url', '')).strip().lstrip('=')
    start    = int(str(data.get('start_seconds', 0)).strip().lstrip('='))
    end      = int(str(data.get('end_seconds', 30)).strip().lstrip('='))
    clip_id  = str(uuid.uuid4())[:8]
    output   = f'{DOWNLOAD_DIR}/{clip_id}.mp4'

    try:
        video_id   = get_video_id(url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400

        direct_url = get_direct_url(video_id)

        subprocess.run([
            'yt-dlp',
            '--no-check-certificates',
            '-f', 'best[height<=720][ext=mp4]/best',
            '--download-sections', f'*{start}-{end}',
            '--concurrent-fragments', '5',
            '--no-playlist',
            '--remux-video', 'mp4',
            '-o', output,
            direct_url
        ], check=True, timeout=300, capture_output=True, text=True)

        return send_file(output, mimetype='video/mp4',
                         as_attachment=True,
                         download_name=f'clip_{clip_id}.mp4')

    except subprocess.CalledProcessError as e:
        return jsonify({'error': e.stderr[-1000:] if e.stderr else 'yt-dlp failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
