FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
LABEL title="chatgpaint"
LABEL authors="Wolfiii, Nicked"
LABEL version="1.0.0"

COPY . /bot

WORKDIR /bot

RUN uv pip install -r requirements.txt
ENV DOCKER=true
ENV STATUS_UPDATE_PORT=7958

VOLUME ["/db"]
EXPOSE 7958

ENTRYPOINT ["python", "fabaxi.py"]

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/"$TZ" /etc/localtime && echo "$TZ" > /etc/timezone