#
# build the internetnews service
# two stage build, first stage prepares the whole innd
# system with all the files and directories and fills in data
# the second stage just copies the files from the first stage
# and starts the service
#

FROM ubuntu:22.04 as builder

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y inn gettext python3 python3-pip git make gcc \
  && rm -rf /var/lib/apt/lists/*

# install faketime lib to fake the date
# to import news articles from the past
RUN git clone https://github.com/wolfcw/libfaketime.git /tmp/libfaketime \
  && cd /tmp/libfaketime \
  && make install \
  && rm -rf /tmp/libfaketime

# setup innd configuration
RUN mkdir /run/innd
COPY etc/ /etc
COPY var/ /var

# copy bootstrap files and configure fake date time library
RUN pip install nntplib pyyaml python-dateutil psutil
COPY bootstrap/ /bootstrap
WORKDIR /bootstrap
ENV LD_PRELOAD=/usr/local/lib/faketime/libfaketime.so.1
ENV FAKETIME_NO_CACHE=1
RUN python3 bootstrap.py


FROM ubuntu:22.04 as runner

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y inn gettext rsyslog \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir /run/innd

COPY --from=builder /etc/news/ /etc/news/
COPY --from=builder /var/lib/news/ /var/lib/news/
COPY --from=builder /var/spool/news/ /var/spool/news/

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "/usr/sbin/innd", "-f" ]
