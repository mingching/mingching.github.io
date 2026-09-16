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
    <a class="btn-pill btn-pill--paper" href="{{ '/CV_Ming-Ching_Chang.pdf' | relative_url }}" download><i class="fas fa-file-download" aria-hidden="true"></i> Curriculum Vitae</a>
  </div>
</div>


<span class='anchor' id='publications'></span>


# 📝 Recent Publications with PDFs


{% include pub-groups.html %}


<span class='anchor' id='complete-publication-record'></span>


# 📚 All Publications

## Browse by research topic

{% include scholar-pub-groups.html %}

## Browse by year

<div class="publication-year-index">
{% assign scholar_year_groups = site.data.scholar_publications | group_by: "year" | sort: "name" | reverse %}
{% for group in scholar_year_groups %}
{% if group.name != "" %}<a href="#scholar-year-{{ group.name }}">{{ group.name }}</a>{% unless forloop.last %} · {% endunless %}{% endif %}
{% endfor %}
</div>

{% for group in scholar_year_groups %}
<details class="pub-topic" id="scholar-year-{% if group.name == "" %}undated{% else %}{{ group.name }}{% endif %}">
  <summary class="pub-topic__toggle">
    <span>{% if group.name == "" %}Undated{% else %}{{ group.name }}{% endif %}</span>
    <span class="pub-topic__count">{{ group.items | size }} publications</span>
  </summary>
  <div class="pub-topic__scroll">
    <ol class="scholar-pub-list">
    {% for item in group.items %}
      <li>
        <a href="{{ item.scholar_url }}" target="_blank" rel="noopener">{{ item.title }}</a>
        <span class="scholar-pub-meta">{{ item.authors }}. {{ item.venue }}{% if item.year %} ({{ item.year }}){% endif %}.</span>
      </li>
    {% endfor %}
    </ol>
  </div>
</details>
{% endfor %}
