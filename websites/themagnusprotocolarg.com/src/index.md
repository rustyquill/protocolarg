---
layout: default
show-cookie-banner: true
---

{:.text-center}
# Welcome to the Hub of the The Magnus Protocol ARG

Welcome to the Hub of the The Magnus Protocol ARG - an Alternate Reality Game, based on Rusty Quill’s upcoming podcast, [The Magnus Protocol](https://rustyquill.com/show/the-magnus-protocol/). 

Here, Rusty Quill will share updates on how the ARG is progressing, and let you know when key, time-based puzzles have been solved so that you don’t miss out on some solution to the real-world aspects. The Hub will also allow anyone who misses the beginning of the ARG to still join in the fun.

The ARG is a work of fiction and although it may reference real-life elements it primarily features fictional characters, companies, and locations.

No information contained in the hub should be considered part of any puzzle or secret. This is intended only for real updates. Similarly, all Rusty Quill official social media accounts, the Rusty Quill website and the Rusty Quill Patreon will NOT participate in the ARG and should not be considered to contributing as part of any puzzle or secret. Remember this Hub website is a place for real updates relating to the ARG including updates on any unlikely technical issues.

By participating in this ARG, you agree with and are familiar with the [Terms and Conditions, as well as the Code of Conduct](/terms.html) we have provided. Due legal considerations and real-world aspects, we require that all players confirm they are 18 or over.

If you have any questions during the ARG please contact us at [arg@rustyquill.com](mailto:arg@rustyquill.com). Be aware, however, we will not help you solve puzzles.

No part of the ARG will require you to enter private property without express permission and at no point will you need to damage to any items, locations or property. We require that you remain polite, courteous and kind with anyone you interact with as part of the ARG, including other players online, in digital spaces and in person. Any bigotry, discrimination or other offensive behaviour will not be tolerated. Please ensure you have read the Terms and Conditions in full before you participate.

Stay safe and have fun.



{% if site.posts.size > 0 %}
---

## Latest Updates

<ol class="updates latest-updates">
  {% for post in site.posts limit:5 %}
    <li class="update latest-update">
      <a href="{{ post.url }}">{{ post.title }} ({{ post.date | date: "%-d %B %Y" }})</a>
    </li>
  {% endfor %}
</ol>

{:.cursive-text}
Show [all updates](/updates.html)

{% endif %}
