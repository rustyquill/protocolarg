---
layout: default
---

# ARG Updates

We will post updates while The Magnus Protocol ARG is running on this page.

Bookmark this page or subscribe to the [RSS feed](/feed.xml) to stay up to date.

---

<ol class="updates">
  {% for post in site.posts %}
    <li class="update">
      <a href="{{ post.url }}">{{ post.title }} ({{ post.date | date: "%-d %B %Y" }})</a>
    </li>
  {% endfor %}
</ol>
