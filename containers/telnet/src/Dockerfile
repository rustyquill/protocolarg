#
# build the internetnews service
# two stage build, first stage prepares the whole innd
# system with all the files and directories and fills in data
# the second stage just copies the files from the first stage
# and starts the service
#

FROM python:3.10

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt \
  && rm -f /requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY app /app
WORKDIR /app

ENTRYPOINT [ "/entrypoint.sh" ]
CMD ["python3", "main.py"]
