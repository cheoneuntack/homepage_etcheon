# -*- coding: utf-8 -*-
"""네이버 부동산에서 내 매물을 가져와 data/listings.json을 갱신한다.

★ 먼저 읽어주세요 ★
네이버 부동산은 개인이 자동으로 매물을 가져갈 수 있는 "공식 API"를 제공하지
않는다. 이 스크립트는 네이버 부동산 웹사이트가 내부적으로 쓰는 주소를 그대로
흉내내는 방식이라, 네이버가 사이트 구조를 바꾸면 언제든 멈출 수 있다.
그래서 아래 두 가지를 꼭 지켜야 한다.

  1) TOKEN(인증값)이 필요하다 — naver_token.txt 에 붙여넣는다.
     구하는 법 (README.md에도 그림 설명 있음):
       ① 크롬으로 https://new.land.naver.com/complexes/23880 접속 후 로그인 없이 그대로 둔다
       ② F12 → Network(네트워크) 탭 열기
       ③ 매물 목록이 있는 화면에서 새로고침
       ④ 목록에서 "articles?..." 로 시작하는 요청을 클릭
       ⑤ Headers(헤더) 안의 "authorization" 값을 통째로 복사
       ⑥ scripts/naver_token.txt 파일에 붙여넣고 저장 (다른 내용은 지우기)
     이 토큰은 보통 몇 시간~하루 정도 지나면 만료되므로, 오류가 나면 다시
     구해서 넣어줘야 한다.

  2) 너무 자주 실행하지 않는다 — 5~10분보다 짧은 간격으로 반복 실행하면
     네이버 쪽에서 일시적으로 차단(429 오류)할 수 있다. 10~30분 간격 정도의
     "작업 스케줄러" 등록을 권장한다 (README.md 참고).

토큰을 구하기 번거롭거나 자꾸 만료돼서 불편하면, data/listings.json 파일을
메모장으로 직접 열어 매물을 손으로 추가/수정해도 된다. 그게 가장 확실하다.
"""
import json
import os
import time
import urllib.error
import urllib.request

# ── 설정 ──────────────────────────────────────────────────────────
REALTOR_ID = "apt1800"  # 홈페이지 만들 때 알려주신 링크에서 확인한 중개사무소 식별자
COMPLEX_NUMBERS = ["23880"]  # 매물이 올라오는 단지 코드. new.land.naver.com/complexes/뒤의 숫자.
                              # 다른 단지도 다루신다면 여기에 콤마로 추가하세요. 예: ["23880", "12345"]
TRADE_TYPES = "A1:B1:B2"  # A1=매매, B1=전세, B2=월세 (네이버 부동산 내부 코드)
DEAL_TYPE_LABEL = {"A1": "매매", "B1": "전세", "B2": "월세"}
REQUEST_DELAY_SEC = 2  # 여러 단지를 조회할 때 요청 사이 대기 시간(과다요청 방지)
# ──────────────────────────────────────────────────────────────────

HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(HERE, "naver_token.txt")
OUT_PATH = os.path.join(HERE, "..", "docs", "data", "listings.json")

OFFICE_INFO = {
    "name": "푸르지오뱅크 공인중개사사무소",
    "agent": "천은택 공인중개사",
    "phone": "031-296-1800",
    "regNo": "가3678-4404",
    "address": "경기도 수원시 장안구 화산로 87, 상가102호 (천천푸르지오상가)",
    "naverRealtorId": REALTOR_ID,
}


def load_token():
    if not os.path.exists(TOKEN_PATH):
        return None
    with open(TOKEN_PATH, "r", encoding="utf-8") as f:
        token = f.read().strip()
    return token or None


def fetch_articles(complex_no, token):
    url = (
        "https://new.land.naver.com/api/articles?"
        f"realEstateType=APT&tradeType={TRADE_TYPES}"
        "&tag=%3A%3A%3A%3A%3A%3A%3A%3A&rentPriceMin=0&rentPriceMax=900000000"
        "&priceMin=0&priceMax=900000000&areaMin=0&areaMax=900000000"
        f"&priceType=RETAIL&page=1&complexNo={complex_no}&order=rank"
    )
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": f"https://new.land.naver.com/complexes/{complex_no}",
        "Accept": "application/json, text/plain, */*",
        "authorization": token,
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def to_listing(article, complex_name):
    deal_code = article.get("tradeTypeCode", "")
    return {
        "id": str(article.get("articleNo")),
        "complex": complex_name or article.get("articleName", ""),
        "dealType": DEAL_TYPE_LABEL.get(deal_code, deal_code),
        "price": article.get("dealOrWarrantPrc", "-"),
        "areaType": article.get("areaName", "-"),
        "areaM2": article.get("area1", "-"),
        "floor": article.get("floorInfo", "-"),
        "direction": article.get("direction", "-"),
        "desc": (article.get("articleFeatureDesc") or "").strip(),
        "tags": article.get("tagList", []) or [],
        "naverLink": (
            f"https://new.land.naver.com/complexes/{article.get('hscpNo', '')}"
            f"?articleNo={article.get('articleNo', '')}&realtorId={REALTOR_ID}"
        ),
    }


def main():
    token = load_token()
    if not token:
        print("naver_token.txt 가 없거나 비어 있습니다. README.md의 안내대로 토큰을 먼저 넣어주세요.")
        print("(토큰 없이는 실행할 수 없습니다. data/listings.json은 그대로 둡니다.)")
        return

    all_listings = []
    errors = []

    for i, complex_no in enumerate(COMPLEX_NUMBERS):
        if i > 0:
            time.sleep(REQUEST_DELAY_SEC)
        print(f"단지 {complex_no} 매물 조회 중...")
        try:
            data = fetch_articles(complex_no, token)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                errors.append(f"[{complex_no}] 요청이 너무 잦습니다(429). 잠시 후 다시 시도하세요.")
            elif e.code == 401:
                errors.append(f"[{complex_no}] 토큰이 만료됐습니다(401). naver_token.txt를 새로 채워주세요.")
            else:
                errors.append(f"[{complex_no}] 오류: HTTP {e.code}")
            continue
        except Exception as e:
            errors.append(f"[{complex_no}] 오류: {e}")
            continue

        articles = data.get("articleList", []) if isinstance(data, dict) else []
        mine = [a for a in articles if str(a.get("realtorId", "")) == REALTOR_ID]
        complex_name = articles[0].get("articleName") if articles else complex_no
        all_listings.extend(to_listing(a, complex_name) for a in mine)
        print(f"  → 전체 {len(articles)}건 중 내 매물 {len(mine)}건 확인")

    if errors:
        print("\n※ 일부 문제 발생:")
        for e in errors:
            print("  -", e)

    if not all_listings:
        print("\n확인된 내 매물이 없습니다. data/listings.json을 갱신하지 않고 종료합니다.")
        print("(토큰 문제이거나, 정말 매물이 없는 경우일 수 있습니다)")
        return

    result = {
        "office": OFFICE_INFO,
        "updatedAt": None,
        "isSampleData": False,
        "listings": all_listings,
    }
    from datetime import datetime, timezone, timedelta
    result["updatedAt"] = datetime.now(timezone(timedelta(hours=9))).isoformat()

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n완료: 매물 {len(all_listings)}건을 data/listings.json 에 저장했습니다.")
    print("이제 호스팅 서비스에 data/listings.json 파일을 다시 업로드하면 홈페이지에 반영됩니다.")


if __name__ == "__main__":
    main()
