FROM b1tw153/overpass-api@sha256:b5b458688c20844630caea4b81f619545ddbc0a1f771ee42b82f3a1fff2a6188

# Paths (relative to the build context) of the nginx files baked into the image.
# Override them at build time to use your own, e.g. in compose.yml `build.args`
# or with `docker build --build-arg NGINX_TEMPLATE=path/to/my.conf.template .`
ARG NGINX_TEMPLATE=nginx/nginx.conf.template
ARG NGINX_USER_AGENTS_DIR=nginx/user-agents

# The template is rendered by the image entrypoint with envsubst at startup,
# so ${NGINX_*} placeholders in it keep working.
COPY ${NGINX_TEMPLATE} /etc/nginx/nginx.conf.template

# Default User-Agent whitelist: a baseline so the image works on its own.
# compose.yml bind-mounts the same directory over it for live editing.
COPY ${NGINX_USER_AGENTS_DIR}/ /etc/nginx/user-agents/
