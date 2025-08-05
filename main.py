
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

.youtube.com	TRUE	/	FALSE	1788494943	HSID	AHI19-pRZmB8yQ9ST
.youtube.com	TRUE	/	TRUE	1788494943	SSID	A-pLqiAuyz8V5LVFI
.youtube.com	TRUE	/	FALSE	1788494943	APISID	0pHa12CXa5GRKTco/ALXQ3KF1rCJsUgghj
.youtube.com	TRUE	/	TRUE	1788494943	SAPISID	K6vPt3W6T83NLmPK/AxTdOYAaJKl3AVgLM
.youtube.com	TRUE	/	TRUE	1788494943	__Secure-1PAPISID	K6vPt3W6T83NLmPK/AxTdOYAaJKl3AVgLM
.youtube.com	TRUE	/	TRUE	1788494943	__Secure-3PAPISID	K6vPt3W6T83NLmPK/AxTdOYAaJKl3AVgLM
.youtube.com	TRUE	/	TRUE	1783231114	LOGIN_INFO	AFmmF2swRgIhAIs0L0gYORkajT_Te1jC9bwNtbg2W7ZYyGwtYdBoyhuPAiEApBBsqCxoKdazwIhdccRvZ9sKB7RG7h7sgBAxZH-ikns:QUQ3MjNmeEktNDZjV3kzMjI0ZkdGdWMwbWNDQ3p1RDNYcER5T3VlS09oSzVpdVE2OHM5M3VFUlAzNlNfVXo2YXhfb3ZtOU96ci1Nbk4tRGtoYXNzNVhMNDVIMlgwQnM0SGN5Nkd5c09qNDdjRFR5T21sVXlaYkZJWlI4NThjSVg3MFlweUtVQ3UzNWRMSzIyRXd3RkI1NWZHMTJ5a0JkWEVn
.youtube.com	TRUE	/	FALSE	1756690679	_gcl_au	1.1.8000727.1748914679
.youtube.com	TRUE	/	TRUE	1788982905	PREF	f7=100&tz=America.Los_Angeles&repeat=NONE&autoplay=true
.youtube.com	TRUE	/	FALSE	1788494943	SID	g.a000zwi6mWkH3MXzgpov8uGIiC7GiF9bg6DcApZvuUP4dNISNhnDkxyLXt2StZuEJdCZ8bH-CQACgYKAfMSARUSFQHGX2Mi2LrihkU1IBnniIjZonUF-RoVAUF8yKoVkAc1r4D2LaFl8RRArSde0076
.youtube.com	TRUE	/	TRUE	1788494943	__Secure-1PSID	g.a000zwi6mWkH3MXzgpov8uGIiC7GiF9bg6DcApZvuUP4dNISNhnD0OTdkF9JJlbwgUi1LUHWNgACgYKAQMSARUSFQHGX2MiENbbmWB_Z7jUbF4XNOJtORoVAUF8yKqZJ7J8Gs4ipAQhHBPzNN6J0076
.youtube.com	TRUE	/	TRUE	1788494943	__Secure-3PSID	g.a000zwi6mWkH3MXzgpov8uGIiC7GiF9bg6DcApZvuUP4dNISNhnDHaExtjB7w0WW6V6Go2uQ3gACgYKAZgSARUSFQHGX2Mi01uAZXlovMmPR4bfkSpYZxoVAUF8yKqi6REUmpA2YCphwog_tEu40076
.youtube.com	TRUE	/	TRUE	1785944214	__Secure-1PSIDTS	sidts-CjEB5H03P6f1Tq5Lzf6bA8OeOYn5Iq9AWN_uZl8kdDllNYp33IUzSveCYk9YYwasT91eEAA
.youtube.com	TRUE	/	TRUE	1785944214	__Secure-3PSIDTS	sidts-CjEB5H03P6f1Tq5Lzf6bA8OeOYn5Iq9AWN_uZl8kdDllNYp33IUzSveCYk9YYwasT91eEAA
.youtube.com	TRUE	/	FALSE	1785958914	SIDCC	AKEyXzXbJZw1GLhlRYCI_nSC1pAsnjHigKWe_bWxqS08XvzCyPIA4iNf4emo1N70zplaP7a-Zg
.youtube.com	TRUE	/	TRUE	1785958914	__Secure-1PSIDCC	AKEyXzVGiztVElnOUZXJ_J-aJV236PJfK7XLlnbWkSwrZ0b4g-nGABWHtHFUVPiW66AJDiQ2zSc
.youtube.com	TRUE	/	TRUE	1785958914	__Secure-3PSIDCC	AKEyXzXG3g2EwbFnTnf_jZ_amdjTSMFKUvTap0UfJwoD2fPWlup6B-miebhLFDN4ERtf5gEot2Q
.youtube.com	TRUE	/	TRUE	1769974901	VISITOR_INFO1_LIVE	3rtGQjt3kP8
.youtube.com	TRUE	/	TRUE	1769974901	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgBw%3D%3D
.youtube.com	TRUE	/	TRUE	1769938821	__Secure-ROLLOUT_TOKEN	CNi_mfSS2MTIERCv8taL2qWNAxjR1vSZsPOOAw%3D%3D
.youtube.com	TRUE	/	TRUE	0	YSC	OaUB6OSOZBc



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
                "download_url": f"https://anshapi.onrender.com/p/?id={short_id}",
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
