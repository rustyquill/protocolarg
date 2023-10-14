# final-page

Viewer Request lambda ensuring people are only accessing the final page of the ARG
via the Magnus Archives Database website!

"Only" is maybe the wrong word as one can still fake the request.

The lambda does two things. If the request is arriving before the specified
minimum date (2023-10-08) it will automatically be denied.

If the request arrives after the specified date the lambda will check for a custom debugging header
in the request or for a hashed timestamp in the query string

If the timestamp can be decoded and is at max 30sec in the past we allow the request.
