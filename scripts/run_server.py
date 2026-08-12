# -*- coding: utf-8 -*-
"""부동산 홈페이지를 이 PC에서 웹서버로 띄운다.

시작 메뉴의 "홈페이지 서버 시작"으로 실행하면 이 스크립트가 돌아가면서
브라우저가 자동으로 열린다. 같은 와이파이(공유기)에 연결된 다른 기기
(핸드폰 등)에서도 아래 안내되는 주소로 접속해서 볼 수 있다.

이 창을 닫으면(또는 최소화 상태에서 완전히 종료하면) 서버가 꺼진다.
나중에 외부 호스팅으로 옮기기 전까지, 이 PC를 임시 서버로 쓰는 용도다.
"""
import http.server
import socket
import threading
import time
import webbrowser
from functools import partial
from pathlib import Path

PORT = 8090
SITE_DIR = Path(__file__).resolve().parent.parent / "docs"


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass


def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def open_browser_later():
    time.sleep(0.8)
    webbrowser.open(f"http://localhost:{PORT}")


def main():
    handler = partial(NoCacheHandler, directory=str(SITE_DIR))
    try:
        httpd = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), handler)
    except OSError as e:
        print(f"서버를 시작하지 못했습니다: {e}")
        print(f"이미 {PORT} 포트를 다른 프로그램이 쓰고 있을 수 있습니다.")
        print("(이 창의 scripts/run_server.py 맨 위 PORT 값을 다른 숫자로 바꿔보세요)")
        input("\n창을 닫으려면 Enter를 누르세요...")
        return

    lan_ip = get_lan_ip()
    print("=" * 54)
    print(" 푸르지오뱅크 천은택 부동산 홈페이지 - 로컬 서버 실행 중")
    print("=" * 54)
    print(f" 이 PC에서 보기        : http://localhost:{PORT}")
    print(f" 같은 와이파이 기기에서 : http://{lan_ip}:{PORT}")
    print()
    print(" 매물/블로그를 갱신했다면 새로고침만 하면 바로 반영됩니다.")
    print(" 이 창을 닫으면 서버가 꺼집니다. (최소화는 괜찮습니다)")
    print("=" * 54)

    threading.Thread(target=open_browser_later, daemon=True).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n서버를 종료합니다.")


if __name__ == "__main__":
    main()
