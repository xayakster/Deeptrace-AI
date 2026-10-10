import urllib.request
import json
import os

test_images_map = {
    'authentic_photo.jpg': os.path.join(os.getcwd(), 'test_images', 'real_images', 'authentic_photo.jpg'),
    'ai_synthetic.jpg': os.path.join(os.getcwd(), 'test_images', 'ai_generated_images', 'ai_synthetic.jpg'),
    'spliced_tampered.jpg': os.path.join(os.getcwd(), 'test_images', 'edited_images', 'spliced_tampered.jpg')
}

for fname, p in test_images_map.items():
    if not os.path.exists(p):
        p = os.path.join(os.getcwd(), 'scratch_test_assets', fname)
    with open(p, 'rb') as f:
        img_bytes = f.read()

    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    header_part = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="{fname}"\r\n'
        f'Content-Type: image/jpeg\r\n\r\n'
    ).encode('utf-8')
    footer_part = f'\r\n--{boundary}--\r\n'.encode('utf-8')
    body = header_part + img_bytes + footer_part

    req = urllib.request.Request(
        'http://localhost:8501/analyze',
        data=body,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
    )
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read())
        print(f"=== {fname} ===")
        print(f"Verdict: {data['verdict']}")
        print(f"Detection Type: {data['detection_type']}")
        print(f"Composite Score: {data['score']}% | AI Score: {data['ai_score']}% | Tamper Score: {data['tamper_score']}%")
        print(f"Badges: {[b['label'] for b in data['badges']]}\n")
