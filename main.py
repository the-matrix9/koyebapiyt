
from flask import Flask, request, jsonify, redirect
import yt_dlp
import random
import string
import tempfile
import os

app = Flask(__name__)
redirect_links = {}

def generate_id(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

YOUTUBE_COOKIE_TEXT = """# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.

.youtube.com	TRUE	/	FALSE	1785825225	HSID	AHI19-pRZmB8yQ9ST
.youtube.com	TRUE	/	TRUE	1785825225	SSID	A-pLqiAuyz8V5LVFI
.youtube.com	TRUE	/	FALSE	1785825225	APISID	0pHa12CXa5GRKTco/ALXQ3KF1rCJsUgghj
.youtube.com	TRUE	/	TRUE	1785825225	SAPISID	K6vPt3W6T83NLmPK/AxTdOYAaJKl3AVgLM
.youtube.com	TRUE	/	TRUE	1785825225	__Secure-1PAPISID	K6vPt3W6T83NLmPK/AxTdOYAaJKl3AVgLM
.youtube.com	TRUE	/	TRUE	1785825225	__Secure-3PAPISID	K6vPt3W6T83NLmPK/AxTdOYAaJKl3AVgLM
.youtube.com	TRUE	/	TRUE	1783231114	LOGIN_INFO	AFmmF2swRgIhAIs0L0gYORkajT_Te1jC9bwNtbg2W7ZYyGwtYdBoyhuPAiEApBBsqCxoKdazwIhdccRvZ9sKB7RG7h7sgBAxZH-ikns:QUQ3MjNmeEktNDZjV3kzMjI0ZkdGdWMwbWNDQ3p1RDNYcER5T3VlS09oSzVpdVE2OHM5M3VFUlAzNlNfVXo2YXhfb3ZtOU96ci1Nbk4tRGtoYXNzNVhMNDVIMlgwQnM0SGN5Nkd5c09qNDdjRFR5T21sVXlaYkZJWlI4NThjSVg3MFlweUtVQ3UzNWRMSzIyRXd3RkI1NWZHMTJ5a0JkWEVn
.youtube.com	TRUE	/	FALSE	1756690679	_gcl_au	1.1.8000727.1748914679
.youtube.com	TRUE	/	TRUE	1788249842	PREF	f7=100&tz=America.Los_Angeles&repeat=NONE&autoplay=true
.youtube.com	TRUE	/	FALSE	1785825225	SID	g.a000ygi6mcbnkqsjX5eSPi-7MaOeNdvBMD6CENxWfF9MXw09TdfjVFPlLWTZLjG0tEzEMpfkvAACgYKAZcSARUSFQHGX2Mi_tCG-RFXZ9ySIRvY3h8OhxoVAUF8yKoORDmbupczVJQIfKo60ZvG0076
.youtube.com	TRUE	/	TRUE	1785825225	__Secure-1PSID	g.a000ygi6mcbnkqsjX5eSPi-7MaOeNdvBMD6CENxWfF9MXw09TdfjZD6eE5wGd8uBsX2zIY2KhAACgYKAckSARUSFQHGX2MiMrZpqRocBwTM0gOd04I8hhoVAUF8yKqcyEwUeEMnSWp5wArIRwjz0076
.youtube.com	TRUE	/	TRUE	1785825225	__Secure-3PSID	g.a000ygi6mcbnkqsjX5eSPi-7MaOeNdvBMD6CENxWfF9MXw09Tdfjzr53es2XvQH4q7PUpr9KsQACgYKAWQSARUSFQHGX2MiZ8jvufma3a6YnKnzgPFo7hoVAUF8yKpa4BGC17ngeVXfwu49iaDm0076
.youtube.com	TRUE	/	TRUE	1753691028	CONSISTENCY	AKreu9tEFqvWSMlTq_lW3eEb_wQwT3hII-7oFLiZagM_auAdhZfDpQTvHXzbwArc-Mf8otLbyxjoAX3pPNWCAuUz
.youtube.com	TRUE	/	TRUE	1785226454	__Secure-1PSIDTS	sidts-CjEB5H03P0QO5gBuMxaNx9cKvkytXn50UU46ClFUAsLf5W3y-K8g6rQ9_GMICC4IMJQ2EAA
.youtube.com	TRUE	/	TRUE	1785226454	__Secure-3PSIDTS	sidts-CjEB5H03P0QO5gBuMxaNx9cKvkytXn50UU46ClFUAsLf5W3y-K8g6rQ9_GMICC4IMJQ2EAA
.youtube.com	TRUE	/	FALSE	1785226454	SIDCC	AKEyXzVnpkDSGQbVLbRkvgcnf50XGwWXSUOlFcqkAfUb9aUDH0DzN_ZH6UM3t2oqItZVlAkBdg
.youtube.com	TRUE	/	TRUE	1785226454	__Secure-1PSIDCC	AKEyXzUQSbDkDs3CVHZ7koqfV_7pnYHBUOZelS4-YXyz8nB-mp1_943bx9HZMzmjDbb2jeA6-vo
.youtube.com	TRUE	/	TRUE	1785226454	__Secure-3PSIDCC	AKEyXzWHGMT4SM1hrQy_dhjGDaUzcxZHSYhovrPbOrTpidfBIm9oueh6yYrqaHY-P30-nb0OTaw
.youtube.com	TRUE	/	TRUE	1769241840	VISITOR_INFO1_LIVE	3rtGQjt3kP8
.youtube.com	TRUE	/	TRUE	1769241840	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgBw%3D%3D
.youtube.com	TRUE	/	TRUE	0	YSC	qfKKyPwa6fc
.youtube.com	TRUE	/	TRUE	1769241831	__Secure-ROLLOUT_TOKEN	CNi_mfSS2MTIERCv8taL2qWNAxj8rLPci9-OAw%3D%3D


"""

@app.route('/')
def get_download_link():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "Missing 'url' query parameter"}), 400

    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp_cookie_file:
        tmp_cookie_file.write(YOUTUBE_COOKIE_TEXT)
        tmp_cookie_path = tmp_cookie_file.name

    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'format': 'best[ext=mp4]/best',
            'cookiefile': tmp_cookie_path,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            direct_url = info["url"]
            title = info.get("title", "Unknown")
            duration = info.get("duration_string", "Unknown")
            short_id = generate_id()
            redirect_links[short_id] = direct_url

            return jsonify({
                "status": "success",
                "title": title,
                "duration": duration,
                "download_url": f"anshapi.orender.com/p/?id={short_id}",
                "powered_by": "t.me/anshapi"
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if os.path.exists(tmp_cookie_path):
            os.remove(tmp_cookie_path)

@app.route('/p/')
def redirect_download():
    short_id = request.args.get('id')
    if short_id in redirect_links:
        return redirect(redirect_links[short_id])
    return jsonify({"error": "Invalid or expired ID"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
