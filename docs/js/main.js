(function () {
  "use strict";

  function esc(s) {
    return (s === null || s === undefined ? "" : String(s)).replace(/[&<>]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c];
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
    loadBlog();
  });
})();
