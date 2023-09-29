FROM alpine:3.16.2

RUN apk add curl

CMD curl -sL \
    -X PATCH \
    -H "Authorization: Bearer ${AUTH_TOKEN}" \
    -H "Content-Type: application/json" \
    --data "{\"content\": \"$(curl -sL https://ident.me)\"}" \
    "https://api.cloudflare.com/client/v4/zones/${DNS_ZONE_ID}/dns_records/${DNS_RECORD_ID}"
