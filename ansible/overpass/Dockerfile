FROM b1tw153/overpass-api@sha256:b5b458688c20844630caea4b81f619545ddbc0a1f771ee42b82f3a1fff2a6188

RUN sed 's/server {/server { if ($http_user_agent = "") { return 403; } if ($http_referer = "") { return 403; }/' /etc/nginx/nginx.conf.template > /tmp/nginx.conf.template.new
RUN cat /tmp/nginx.conf.template.new > /etc/nginx/nginx.conf.template
