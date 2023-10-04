FROM golang:1.21.1-alpine AS builder

RUN apk add git && \
    git clone https://github.com/rafaelvieiras/jellyfin-exporter.git && \
    cd jellyfin-exporter && \
    go build

FROM alpine:3.18.4

COPY --from=builder /go/jellyfin-exporter/jellyfin-exporter .

ENTRYPOINT [ "./jellyfin-exporter" ]
