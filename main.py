
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
.youtube.com	TRUE	/	TRUE	1788084434	PREF	f7=100&tz=America.Los_Angeles&repeat=NONE&autoplay=true
.youtube.com	TRUE	/	FALSE	1785825225	SID	g.a000ygi6mcbnkqsjX5eSPi-7MaOeNdvBMD6CENxWfF9MXw09TdfjVFPlLWTZLjG0tEzEMpfkvAACgYKAZcSARUSFQHGX2Mi_tCG-RFXZ9ySIRvY3h8OhxoVAUF8yKoORDmbupczVJQIfKo60ZvG0076
.youtube.com	TRUE	/	TRUE	1785825225	__Secure-1PSID	g.a000ygi6mcbnkqsjX5eSPi-7MaOeNdvBMD6CENxWfF9MXw09TdfjZD6eE5wGd8uBsX2zIY2KhAACgYKAckSARUSFQHGX2MiMrZpqRocBwTM0gOd04I8hhoVAUF8yKqcyEwUeEMnSWp5wArIRwjz0076
.youtube.com	TRUE	/	TRUE	1785825225	__Secure-3PSID	g.a000ygi6mcbnkqsjX5eSPi-7MaOeNdvBMD6CENxWfF9MXw09Tdfjzr53es2XvQH4q7PUpr9KsQACgYKAWQSARUSFQHGX2MiZ8jvufma3a6YnKnzgPFo7hoVAUF8yKpa4BGC17ngeVXfwu49iaDm0076
.youtube.com	TRUE	/	TRUE	1785060421	__Secure-1PSIDTS	sidts-CjEB5H03P4c2E3g8o6GCk-8jinC3k4pTr20Nf5O9RXCuMouxfmHq36yDOAZ4JfCJzAnJEAA
.youtube.com	TRUE	/	TRUE	1785060421	__Secure-3PSIDTS	sidts-CjEB5H03P4c2E3g8o6GCk-8jinC3k4pTr20Nf5O9RXCuMouxfmHq36yDOAZ4JfCJzAnJEAA
.youtube.com	TRUE	/	FALSE	1785060466	SIDCC	AKEyXzUTaoGv3cPQwlVBpD7s3LaJDU2c2OJ_COrnpPVMXZJZBdnY9loxP3mw99y6ThHuzJPE5A
.youtube.com	TRUE	/	TRUE	1785060466	__Secure-1PSIDCC	AKEyXzX5G9Y-s3aqHez8IS4ZHVYyB-NukY6NgY6hKYiRZZDOy_HEi_GaHeMJ-9GD7_YHvmoVgKk
.youtube.com	TRUE	/	TRUE	1785060466	__Secure-3PSIDCC	AKEyXzXuV67FFXre8eBPWwDW5PKy_Li17rNHYMiwrfkgnNWE2_89EYpXyOJekeLvqftk7WUTkiA
.youtube.com	TRUE	/	TRUE	1769076429	VISITOR_INFO1_LIVE	3rtGQjt3kP8
.youtube.com	TRUE	/	TRUE	1769076429	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgBw%3D%3D
.youtube.com	TRUE	/	TRUE	1768996837	__Secure-ROLLOUT_TOKEN	CNi_mfSS2MTIERCv8taL2qWNAxjl4cGG-9eOAw%3D%3D
.youtube.com	TRUE	/	TRUE	0	YSC	LgoIOOtKTm4

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
                "download_url": f"then-jocelin-anshapiyt-459a1299.koyeb.app/p/?id={short_id}",
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
