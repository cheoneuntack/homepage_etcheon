# 푸르지오뱅크 천은택 부동산 홈페이지

정적 파일(HTML/CSS/JS)로 만든 홈페이지입니다. 지금은 **이 PC를 임시 웹서버로 사용**할 수
있고, **Firebase Hosting(무료)** 로 인터넷에 정식 공개할 수도 있습니다.

## 폴더 구성

```
public/index.html               홈페이지 본문 (Firebase/서버가 실제로 보여주는 폴더)
public/css/style.css             디자인
public/js/main.js                 매물/블로그 목록을 화면에 그려주는 스크립트
public/data/listings.json         매물 데이터 (이 파일만 바뀌면 홈페이지 매물이 바뀝니다)
public/data/blog.json             블로그 최근글 데이터
firebase.json / .firebaserc      Firebase Hosting 설정 (프로젝트: theedufore-505c8)
홈페이지_서버_시작.bat            이 PC를 서버로 실행 (시작 메뉴에도 등록되어 있음)
배포_Firebase.bat                Firebase에 배포 (CLI 설치 후 사용)
scripts/run_server.py            위 .bat이 실행하는 실제 서버 코드
scripts/update_blog.py           블로그 최신글로 public/data/blog.json 갱신
scripts/update_listings.py       네이버 부동산 매물로 public/data/listings.json 갱신 (토큰 필요)
```

## 0. 이 PC를 서버로 사용하기 (지금 바로 되는 방법)

**시작 메뉴 → "천은택 부동산 홈페이지" 폴더 → "홈페이지 서버 시작"** 을 누르면 됩니다.

실행하면 검은 창(콘솔)이 뜨고 브라우저가 자동으로 열리며 홈페이지가 보입니다.
- `http://localhost:8090` — 이 PC 전용
- `http://192.168.x.x:8090` — 같은 와이파이 기기에서도 접속 가능 (인터넷 전체 공개는 아님)

이 창을 닫으면 서버가 꺼집니다. 손님에게 인터넷으로 공개하려면 아래 Firebase Hosting을
쓰시면 됩니다.

## 1. Firebase Hosting으로 인터넷에 무료 공개하기

Firebase 프로젝트 `theedufore-505c8` (Spark 무료 요금제)에 연결하도록 이미 설정
(`firebase.json`, `.firebaserc`)해 두었습니다. 아래 순서만 진행하시면 됩니다.
**로그인은 사장님 구글 계정으로 진행되는 부분이라 직접 하셔야 합니다.**

1. **Node.js 설치** (Firebase CLI 실행에 필요, 한 번만): PowerShell에서
   ```
   winget install OpenJS.NodeJS.LTS
   ```
   설치 후 **터미널(PowerShell)을 새로 열어야** 인식됩니다.

2. **Firebase CLI 설치**:
   ```
   npm install -g firebase-tools
   ```

3. **로그인** (브라우저가 열리며 구글 계정 로그인 화면이 뜹니다. 사장님 계정으로 직접
   진행해 주세요):
   ```
   firebase login
   ```

4. **배포** — 프로젝트 폴더(`부동산_홈페이지`)에서:
   ```
   firebase deploy --only hosting
   ```
   또는 `배포_Firebase.bat`을 더블클릭해도 동일합니다.

배포가 끝나면 아래 주소로 바로 접속할 수 있습니다 (완전 무료, SSL 자동 적용).
- `https://theedufore-505c8.web.app`
- `https://theedufore-505c8.firebaseapp.com`

배포는 몇 초면 끝나고, 몇 번이고 다시 실행해도 안전합니다(덮어쓰기). 매물/블로그를
갱신한 뒤 `firebase deploy --only hosting`을 다시 실행하면 그 내용이 반영됩니다.

### (선택) 로컬 미리보기

배포 전에 Firebase 에뮬레이터로 미리 확인하고 싶으면 프로젝트 폴더에서:
```
firebase emulators:start
```

### (선택) 나만의 도메인 연결

`theedufore-505c8.web.app` 대신 사장님 소유 도메인(예: 후이즈에서 구매한 도메인)을
쓰고 싶으시면 Firebase 콘솔의 Hosting 메뉴에서 "맞춤 도메인 연결"로 진행하면 됩니다.
도메인을 알려주시면 DNS 설정까지 같이 도와드릴 수 있습니다.

## 2. 매물 업데이트하기 (실시간이 아니라 "주기적 갱신"입니다)

네이버 부동산은 개인이 자동으로 매물을 가져갈 수 있는 공식 API가 없습니다. 그래서
"매물이 올라가는 즉시 홈페이지에 반영"은 불가능하고, 대신 아래 방식으로 근접하게 흉내냅니다.

1. `scripts/update_listings.py`를 실행하면 `public/data/listings.json`이 최신 매물로
   갱신됩니다.
2. 이 PC 서버(0번)로 보고 있다면 새로고침만 하면 바로 반영됩니다. Firebase에 올린
   사이트에 반영하려면 `firebase deploy --only hosting`(또는 `배포_Firebase.bat`)을
   한 번 더 실행해야 합니다.
3. 위 실행+배포를 이 PC의 "작업 스케줄러"에 10~30분 간격으로 등록해두면 사람이 직접
   손대지 않아도 자동으로 반복되게 만들 수 있습니다 (원하시면 다음 단계로 만들어
   드리겠습니다).

### 토큰(인증값) 구하는 법

`update_listings.py`가 사용하는 주소는 네이버 부동산 웹페이지가 내부적으로 쓰는 주소라서,
접속하려면 "토큰"이 필요합니다. 아래처럼 구합니다.

1. 크롬 브라우저로 `https://new.land.naver.com/complexes/23880` 접속
2. 키보드 F12 → 상단 메뉴에서 "Network"(네트워크) 클릭
3. 매물 목록이 보이는 상태에서 새로고침(F5)
4. 왼쪽 목록에서 `articles?...`로 시작하는 항목 클릭
5. 오른쪽 "Headers" 안에서 `authorization` 값을 통째로 복사 (Bearer로 시작하는 긴 문자열)
6. `scripts/naver_token.txt` 파일을 새로 만들어(메모장) 그 값만 붙여넣고 저장

이 토큰은 보통 몇 시간~하루 정도 지나면 만료됩니다. 만료되면 스크립트 실행 시
"토큰이 만료됐습니다" 라고 안내되며, 위 순서대로 다시 구해서 넣어주면 됩니다.
`naver_token.txt`는 절대 홈페이지에 올라가지 않습니다(`public/` 밖에 있음).

**주의**: 너무 자주 실행하면(예: 1분 간격) 네이버 쪽에서 일시적으로 차단할 수 있습니다.
10~30분 간격을 권장합니다.

### 토큰 없이 매물 관리하는 법 (가장 확실한 방법)

토큰 구하는 게 번거로우시면, `public/data/listings.json`을 메모장으로 열어 직접
추가/수정하셔도 됩니다. 항목 하나의 형식은 다음과 같습니다.

```json
{
  "id": "고유번호(아무 문자열)",
  "complex": "화서역푸르지오더에듀포레",
  "dealType": "매매",
  "price": "9억 5,000",
  "areaType": "84A",
  "areaM2": "84.98",
  "floor": "12/25층",
  "direction": "남향",
  "desc": "역세권, 판상형 구조",
  "tags": ["역세권", "판상형"],
  "naverLink": "https://new.land.naver.com/complexes/23880?realtorId=apt1800"
}
```

파일 맨 위 `"isSampleData": true`를 `false`로 바꾸면 "예시 데이터입니다" 안내 배너가
사라집니다. 수정 후에는 Firebase에도 반영하려면 `firebase deploy --only hosting`을
실행해야 합니다.

## 3. 블로그 글 업데이트하기

`scripts/update_blog.py`를 실행하면 네이버 블로그(apt9133)의 최신 글 8개를 자동으로
가져와 `public/data/blog.json`을 갱신합니다. 이건 토큰이 필요 없고 안정적으로 동작합니다.
역시 Firebase에 반영하려면 `firebase deploy --only hosting`을 실행해야 합니다.
