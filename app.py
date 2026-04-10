from flask import Flask, request, send_file, jsonify
import subprocess, os, uuid, base64

app = Flask(__name__)
DOWNLOAD_DIR = '/tmp/clips'
COOKIES_FILE = '/tmp/yt_cookies.txt'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Write cookies from env variable on startup
cookies_b64 = os.environ.get('COOKIES_BASE64', '')
if cookies_b64:
    with open(COOKIES_FILE, 'wb') as f:
        f.write(base64.b64decode(cookies_b64))

@app.route('/clip', methods=['POST'])
def clip():
    data     = request.json
    url      = str(data.get('url', '')).strip().lstrip('=')
    start    = int(str(data.get('start_seconds', 0)).strip().lstrip('='))
    end      = int(str(data.get('end_seconds', 30)).strip().lstrip('='))
    clip_id  = str(uuid.uuid4())[:8]
    output   = f'{DOWNLOAD_DIR}/{clip_id}.mp4'

    cmd = [
        'yt-dlp',
        '--no-check-certificates',
        '--extractor-args', 'youtube:player_client=android',
        '-f', 'best[height<=720][ext=mp4]/best[height<=720]/best',
        '--download-sections', f'*{start}-{end}',
        '--force-keyframes-at-cuts',
        '--concurrent-fragments', '5',
        '--no-playlist',
        '-o', output,
        url
    ]

    # Add cookies if available
    if os.path.exists(COOKIES_FILE):
        cmd += ['--cookies', COOKIES_FILE]

    try:
        subprocess.run(cmd, check=True, timeout=300,
                       capture_output=True, text=True)
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
