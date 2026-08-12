# -*- coding: utf-8 -*-
"""네이버 블로그 RSS를 읽어 data/blog.json을 최신 글로 갱신한다.

사용법: 이 파일을 더블클릭하거나, 명령프롬프트에서
    python update_blog.py
로 실행하면 된다. 파이썬 기본 모듈만 사용하므로 별도 설치가 필요 없다.
"""
import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

RSS_URL = "https://rss.blog.naver.com/apt9133.xml"
MAX_POSTS = 8

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "..", "docs", "data", "blog.json")

KST = timezone(timedelta(hours=9))


def strip_cdata_and_query(text):
    if text is None:
        return ""
    return text.split("?")[0].strip()


def fetch_rss():
    req = urllib.request.Request(
        RSS_URL,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read()


def parse_pubdate(raw):
    # 예: "Fri, 07 Aug 2026 16:36:21 +0900"
    try:
        dt = datetime.strptime(raw, "%a, %d %b %Y %H:%M:%S %z")
        return dt.astimezone(KST).strftime("%Y-%m-%d")
    except Exception:
        return raw


def main():
    print("네이버 블로그 RSS 확인 중...")
    try:
        xml_bytes = fetch_rss()
    except Exception as e:
        print("RSS를 가져오지 못했습니다:", e)
        return

    root = ET.fromstring(xml_bytes)
    channel = root.find("channel")
    if channel is None:
        print("RSS 형식이 예상과 다릅니다.")
        return

    posts = []
    for item in channel.findall("item")[:MAX_POSTS]:
        title = (item.findtext("title") or "").strip()
        link = strip_cdata_and_query(item.findtext("link"))
        category = (item.findtext("category") or "부동산 뉴스").strip()
        pub_raw = (item.findtext("pubDate") or "").strip()
        posts.append({
            "title": title,
            "link": link,
            "date": parse_pubdate(pub_raw),
            "category": category,
        })

    data = {
        "channel": {
            "title": (channel.findtext("title") or "").strip(),
            "tagline": "성공적인 부동산파트너",
            "url": "https://blog.naver.com/apt9133",
            "rss": RSS_URL,
        },
        "updatedAt": datetime.now(KST).isoformat(),
        "posts": posts,
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"완료: {len(posts)}개 글을 data/blog.json 에 저장했습니다.")
    print("이제 호스팅 서비스에 data/blog.json 파일을 다시 업로드하면 홈페이지에 반영됩니다.")


if __name__ == "__main__":
    main()
