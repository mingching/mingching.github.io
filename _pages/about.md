---
permalink: /
title: ""
excerpt: ""
author_profile: true
redirect_from: 
  - /about/
  - /about.html
---

<span class='anchor' id='about-me'></span>

<div class="hero">
  <span class="hero__blob hero__blob--1" aria-hidden="true"></span>
  <span class="hero__blob hero__blob--2" aria-hidden="true"></span>
  <p class="hero__greet">Welcome</p>
  <h1 class="hero__name">Ming-Ching Chang, Ph.D.</h1>
  <p class="hero__typing-line"><span id="hero-typing" data-roles='["Associate Professor @ UAlbany, SUNY","Computer Vision &amp; AI Researcher","Video Analytics Researcher","IEEE Senior Member"]'></span><span class="hero__cursor" aria-hidden="true"></span></p>

  <div class="hero__intro" markdown="1">
I am an Associate Professor with tenure in the [Department of Computer Science](https://www.albany.edu/computer-science) at the [University at Albany, State University of New York](https://www.albany.edu/). My research interests include video analytics, computer vision, image processing, and artificial intelligence.

Before joining UAlbany, I was a Computer Scientist at GE Global Research Center and an Assistant Researcher at the Industrial Technology Research Institute in Taiwan. I received my Ph.D. from Brown University, and my M.S. and B.S. degrees from National Taiwan University.

I lead research spanning intelligent video understanding, visual perception, and practical AI systems, with projects supported by government, industry, and academic partners.
  </div>

  <div class="hero__interests">
    <span class="tag-chip">Video Analytics</span>
    <span class="tag-chip">Computer Vision</span>
    <span class="tag-chip">Image Processing</span>
    <span class="tag-chip">Artificial Intelligence</span>
  </div>

  <div style="margin-top: 0.8em;">
    <a class="btn-pill btn-pill--paper" href="{{ '/CV_Ming-Ching_Chang.pdf' | relative_url }}" download><i class="fas fa-file-download" aria-hidden="true"></i> Curriculum Vitae</a>
  </div>
</div>

{% include stats-row.html %}

# 🔥 News

{% include news-timeline.html limit=8 %}

# 📝 Selected Publications

{% include pub-cards.html data=site.data.publications %}

# 🎖 Honors and Awards

{% include awards-list.html %}

# 🔨 Projects

{% include pub-cards.html data=site.data.research_projects %}

## 💼 Funded & Industry Projects

{% include funded-list.html %}

# 📖 Education

{% include edu-list.html %}

# 💼 Academic Services

{% include services-list.html %}

# 🌍 Global Collaborations

<div class="globe-card reveal" style="width:100%; max-width:1000px; margin: 10px auto 30px; text-align:center;">
<div id="visitor-map-holder" style="margin:0 auto;">
<script type="text/javascript" id="mapmyvisitors" src="//mapmyvisitors.com/map.js?d=8ADnNsCiMHFDsAXXuNSPeDLnFpxr3cBBct0zxB4WkaQ&cl=ffffff&w=a"></script>
</div>
<script>
(function () {
  /* mapmyvisitors requests its land-outline PNG at the measured container
     width; fractional widths (browser zoom, fluid layouts) make the server
     return HTTP 500 and the map loses its continents. Pin the holder to an
     integer pixel width before the widget measures it. */
  var h = document.getElementById('visitor-map-holder');
  if (!h) return;
  function pin() {
    h.style.width = '';
    var w = Math.floor(h.getBoundingClientRect().width);
    if (w > 0) { h.style.width = w + 'px'; }
  }
  pin();
  window.addEventListener('resize', pin);
})();
</script>
</div>
