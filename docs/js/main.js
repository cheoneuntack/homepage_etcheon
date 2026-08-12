(function () {
  "use strict";

  var state = { listings: [], filter: "전체" };

  function esc(s) {
    return (s === null || s === undefined ? "" : String(s)).replace(/[&<>]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c];
    });
  }

  function timeAgo(iso) {
    if (!iso) return null;
    var diffMs = Date.now() - new Date(iso).getTime();
    var min = Math.floor(diffMs / 60000);
    if (min < 1) return "방금 전 업데이트";
    if (min < 60) return min + "분 전 업데이트";
    var hr = Math.floor(min / 60);
    if (hr < 24) return hr + "시간 전 업데이트";
    var day = Math.floor(hr / 24);
    return day + "일 전 업데이트";
  }

  function renderUpdateNote(data) {
    var el = document.getElementById("updateNoteText");
    var banner = document.getElementById("sampleBanner");
    if (data.isSampleData || !data.updatedAt) {
      el.textContent = "예시 데이터 표시 중";
      banner.style.display = "block";
    } else {
      el.textContent = timeAgo(data.updatedAt) || "업데이트 정보 없음";
      banner.style.display = "none";
    }
  }

  function listingCard(item) {
    var tags = (item.tags || []).map(function (t) {
      return '<span class="tag-pill">' + esc(t) + "</span>";
    }).join("");

    return (
      '<div class="listing-card" data-deal="' + esc(item.dealType) + '">' +
        '<div class="top-row">' +
          '<span class="deal-badge ' + esc(item.dealType) + '">' + esc(item.dealType) + "</span>" +
          '<span class="price">' + esc(item.price) + "</span>" +
        "</div>" +
        '<div class="complex-name">' + esc(item.complex) + "</div>" +
        '<div class="meta">' +
          "<span>" + esc(item.areaType) + " (" + esc(item.areaM2) + "㎡)</span>" +
          "<span>" + esc(item.floor) + "</span>" +
          "<span>" + esc(item.direction) + "</span>" +
        "</div>" +
        (item.desc ? '<div class="desc">' + esc(item.desc) + "</div>" : "") +
        (tags ? '<div class="tag-row">' + tags + "</div>" : "") +
        '<div class="card-foot">' +
          '<a class="btn btn-outline btn-sm" href="' + esc(item.naverLink) + '" target="_blank" rel="noopener">네이버부동산에서 보기</a>' +
          '<a class="btn btn-primary btn-sm" href="tel:01082519133">전화문의</a>' +
        "</div>" +
      "</div>"
    );
  }

  function renderListings() {
    var grid = document.getElementById("listingGrid");
    var empty = document.getElementById("emptyState");
    var items = state.listings.filter(function (it) {
      return state.filter === "전체" || it.dealType === state.filter;
    });
    grid.innerHTML = items.map(listingCard).join("");
    empty.style.display = items.length ? "none" : "block";
  }

  function initFilters() {
    var row = document.getElementById("filterRow");
    row.addEventListener("click", function (e) {
      var btn = e.target.closest(".filter-chip");
      if (!btn) return;
      row.querySelectorAll(".filter-chip").forEach(function (b) { b.classList.remove("active"); });
      btn.classList.add("active");
      state.filter = btn.dataset.filter;
      renderListings();
    });
  }

  function loadListings() {
    fetch("data/listings.json", { cache: "no-store" })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        state.listings = data.listings || [];
        renderUpdateNote(data);
        renderListings();
      })
      .catch(function () {
        document.getElementById("updateNoteText").textContent = "매물 데이터를 불러오지 못했습니다";
      });
  }

  function blogCard(post) {
    return (
      '<a class="blog-card" href="' + esc(post.link) + '" target="_blank" rel="noopener">' +
        '<span class="cat">' + esc(post.category || "부동산 뉴스") + "</span>" +
        '<span class="title">' + esc(post.title) + "</span>" +
        '<span class="date">' + esc(post.date) + "</span>" +
      "</a>"
    );
  }

  function loadBlog() {
    fetch("data/blog.json", { cache: "no-store" })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var grid = document.getElementById("blogGrid");
        grid.innerHTML = (data.posts || []).map(blogCard).join("");
      })
      .catch(function () {
        document.getElementById("blogGrid").innerHTML =
          '<div class="empty-state">블로그 글을 불러오지 못했습니다. <a href="https://blog.naver.com/apt9133" target="_blank">네이버 블로그 바로가기</a></div>';
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initFilters();
    loadListings();
    loadBlog();
  });
})();
