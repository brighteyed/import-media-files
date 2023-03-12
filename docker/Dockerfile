FROM python:3-alpine3.17

RUN apk add --no-cache ffmpeg

RUN addgroup -g 1000 -S app \
  && adduser -u 1000 -S app -G app 

RUN mkdir /output && chown app:app /output \
  && mkdir /logs && chown app:app /logs

WORKDIR /usr/src/app

COPY . ./
RUN pip install --no-cache-dir -r requirements.txt \
  && chmod +x ./import_files.sh

VOLUME ["/source", "/output", "/logs"]

CMD [ "/bin/sh", "./import_files.sh" ]
