FROM ubuntu:22.04 as builder

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y cvs git make gcc python3 python3-pip \
  && rm -rf /var/lib/apt/lists/*

# install faketime lib to fake the date
RUN git clone https://github.com/wolfcw/libfaketime.git /tmp/libfaketime \
  && cd /tmp/libfaketime \
  && make install \
  && rm -rf /tmp/libfaketime

# copy bootstrap code
COPY bootstrap/ /bootstrap
WORKDIR /bootstrap

# compile the playfair code and setup python requirements
RUN cd playfair \
  && gcc main.c -o playfair \
  && chmod +x playfair \
  && mv playfair /usr/local/bin
RUN cd translation-table \
  && pip3 install -r requirements.txt \
  && chmod +x translation_table.py \
  && mv translation_table.py /usr/local/bin/translation-table

# copy bootstrap files and configure fake date time library
ENV FAKETIME_NO_CACHE=1
ENV LANG=C.UTF-8
# use the second challenge version, if set to 1 uses the simpler one!
ENV USE_CHALLENGE=2
# the cipher codeword
ENV CIPHER="mymindisallcorners"
# and cleartext word which needs to be encoded
ENV INPUT="ddrdonottrustachtneun"
ENV INPUT_CORRUPTED="ERR: DATEN KORRUMPIERT"
RUN bash bootstrap.sh

FROM ubuntu:22.04 as runner

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y apache2 cvsweb zip \
  && rm -rf /var/lib/apt/lists/*

ENV LANG=C.UTF-8

COPY --from=builder --chown=www-data:www-data /cvs/ /var/lib/cvs
COPY etc/ /etc
COPY var/ /var

RUN cp -a /usr/share/cvsweb /var/www/html/resources \
  && a2enmod cgi \
  && a2disconf serve-cgi-bin \
  && cp -a /usr/lib/cgi-bin/cvsweb /var/www/html/index.html


COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "/usr/sbin/apachectl", "-D", "FOREGROUND" ]
