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
  <h1 class="hero__name">Dr. Ming-Ching Chang</h1>

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

  {% include stats-row.html %}

  <div style="margin-top: 0.8em;">
    <a class="btn-pill btn-pill--paper" href="{{ '/CV_Ming-Ching_Chang.pdf' | relative_url }}" download="CV_Ming-Ching_Chang.pdf"><i class="fas fa-file-download" aria-hidden="true"></i> Download Curriculum Vitae</a>
  </div>
</div>

<span class='anchor' id='publications'></span>

# 📝 Recent Publications with PDFs

{% include pub-groups.html %}

<span class='anchor' id='journal-publications'></span>

# 📖 Journal Papers

{% include journal-publications.html %}

<span class='anchor' id='papers-with-code'></span>

# 💻 Papers with Code

{% include resource-publications.html items=site.data.paper_resources.code_papers label="Papers with verified GitHub code" icon="github" %}

<span class='anchor' id='papers-with-datasets'></span>

# 🗂️ Papers with Datasets

{% include resource-publications.html items=site.data.paper_resources.dataset_papers label="Papers with publicly available datasets" icon="dataset" %}

<span class='anchor' id='patents'></span>

# ⚖️ Patents <span class="pub-topic__count">{{ site.data.publication_stats.patents }} formal records</span>

{% include patent-records.html country="US" label="US Patent Records" %}

{% include patent-records.html country="Taiwan" label="Taiwan Patent Records" %}

{% include patent-records.html country="China" label="China Patent Records" %}

<span class='anchor' id='disclosures'></span>

# 📄 Patent Disclosures <span class="pub-topic__count">{{ site.data.patent_disclosures | size }} records</span>

{% include patent-disclosures.html %}

# 📚 All Publications

## Browse by research topic

{% include scholar-pub-groups.html %}

<span class='anchor' id='browse-by-year'></span>

## All Publications: Browse by Year

{% include legacy-pub-years.html %}

<span class='anchor' id='global-reach'></span>

# 🌍 Global Reach

<div class="global-reach" markdown="1">
  <div class="global-reach__intro">
    <p class="global-reach__eyebrow">LIVE VISITOR COUNTER</p>
    <h2>Where visitors come from</h2>
    <p>Country-level visits to this website. Select the counter to view its public geographic summary.</p>
  </div>
  <a class="global-reach__counter" href="https://info.flagcounter.com/5V0F" target="_blank" rel="noopener" aria-label="View public geographic visitor summary from Flag Counter">
    <img src="https://s05.flagcounter.com/count2/5V0F/bg_FFFFFF/txt_000000/border_CCCCCC/columns_2/maxflags_10/viewers_0/labels_0/pageviews_0/flags_0/percent_0/" alt="Visitor countries and total visits" loading="lazy">
  </a>
</div>
