from flask import Flask, request, send_file, jsonify
import subprocess, os, uuid

app = Flask(__name__)
DOWNLOAD_DIR = '/tmp/clips'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/clip', methods=['POST'])
def clip():
    data = request.json
    url      = data.get('url')
    start    = int(data.get('start_seconds', 0))
    duration = int(data.get('end_seconds', 30)) - start
    clip_id  = str(uuid.uuid4())[:8]
    output   = f'{DOWNLOAD_DIR}/{clip_id}.mp4'

    try:
        subprocess.run([
            'yt-dlp',
            '-f', 'best[ext=mp4]/best',
            '--download-sections', f'*{start}-{start+duration}',
            '--force-keyframes-at-cuts',
            '-o', output,
            url
        ], check=True, timeout=300)

        return send_file(output, mimetype='video/mp4',
                         as_attachment=True,
                         download_name=f'clip_{clip_id}.mp4')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
