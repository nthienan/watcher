FROM nthienan/python:3.6.6-alpine3.8-onbuild as builder

RUN python setup.py clean bdist_wheel

FROM alpine:3.10.1

ENV TZ=Asia/Bangkok
ENV WATCH_DIR=/var/watcher

RUN apk --no-cache update && \
    apk --no-cache upgrade && \
    apk --no-cache add tzdata python3 curl && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [ ! -e /usr/bin/python ]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -rf /var/cache/apk/* && \
    rm -rf /root/.cache && \
    mkdir -p /var/watcher /etc/watcher

WORKDIR /var/watcher

COPY --from=builder /usr/src/app/dist/watcher*.whl .
RUN pip install --no-cache-dir watcher*.whl && \
    rm -f watcher*.whl

ENTRYPOINT ["watcher"]
