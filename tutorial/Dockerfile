FROM golang:1.21-alpine as builder

RUN apk add --update --no-cache --repository=https://dl-cdn.alpinelinux.org/alpine/edge/community \
    hugo

WORKDIR /opt/app

COPY . .

RUN wget -qO- https://github.com/McShelby/hugo-theme-relearn/archive/main.zip | busybox unzip -d themes -

RUN hugo

FROM nginx:1.25-alpine as rt

ARG USER=otel

WORKDIR /usr/share/nginx/html

COPY --from=builder /opt/app/public .

EXPOSE 80/tcp