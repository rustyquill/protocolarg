# bonzobazaar.co.uk

bonzobazaar.co.uk Website

to run the live site and test the javascript functions use a docker container
```bash
cd src/live
docker run --rm -ti -v "${PWD}":/usr/share/nginx/html:ro -p 4000:80 nginx
```
