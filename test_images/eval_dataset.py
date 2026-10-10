import os
import urllib.request
import json
import io

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
categories = ['real_images', 'edited_images', 'ai_generated_images']

print(f"{'Category':<22} {'Image':<26} {'Verdict':<15} {'Score':<8} {'Conformal 95% Set'}")
print("-" * 95)

for category in categories:
    folder = os.path.join(BASE_DIR, category)
    if not os.path.exists(folder):
        continue
    for img_name in sorted(os.listdir(folder)):
        if not img_name.endswith('.jpg'):
            continue
        path = os.path.join(folder, img_name)
        boundary = '----WebKitBoundary123'
        body = io.BytesIO()
        body.write(b'--' + boundary.encode() + b'\r\n')
        body.write(f'Content-Disposition: form-data; name="file"; filename="{img_name}"\r\n'.encode())
        body.write(b'Content-Type: image/jpeg\r\n\r\n')
        with open(path, 'rb') as f:
            body.write(f.read())
        body.write(b'\r\n--' + boundary.encode() + b'--\r\n')
        
        req = urllib.request.Request(
            'http://localhost:8501/analyze',
            data=body.getvalue(),
            headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
        )
        data = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
        v_badge = data.get('verdict_badge', 'UNKNOWN')
        score = f"{data.get('score', 0)}%"
        conf_set = str(data.get('conformal_prediction', {}).get('prediction_set', []))
        print(f"{category:<22} {img_name:<26} {v_badge:<15} {score:<8} {conf_set}")
