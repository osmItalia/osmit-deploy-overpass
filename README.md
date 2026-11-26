# osmit-deploy-overpass

## Description

This repo contains IaC and configuration scripts for deploying an overpass API instance on OpenStack using Pulumi and Ansible.

## Requirements

You will need these tools in order to fully deploy the instance, they should be easily retrievable from your trusted package manager:

- [uv](https://docs.astral.sh/uv/)
- [Pulumi](https://www.pulumi.com)
- [Ansible](https://docs.ansible.com)

### Recommended hardware requirements

See [`__main__.py`](__main__.py) in the `Volume` and `Instance` creation for the recommended hardware.

## How to use

Unfortunately many steps are still manual, please follow all steps carefully. If unsure, better to ask maintainers.

### Create an OpenStack API key

1. Get yourself an API key for your OpenStack instance, you should be able to generate a `clouds.yaml` file;
2. Place the `clouds.yaml` file inside `~/.config/openstack/`.

### Run pulumi

1. Login to your Pulumi state backend;
2. Chose the correct stack via `pulumi stack select <stack-name>`;
3. Run a refresh in order to safely get new changes that may have been made via the OpenStack GUI `pulumi refresh`;
4. Run `pulumi up` to deploy your latest changes.

### Configure with Ansible

Unfortunately, deploying infrastructure is not enough. We need to deploy the actual application.

1. Get your instance name via `pulumi stack output instance-host`;
2. Change directory to `cd ./ansible/`
3. Generate yourself an `inventory.yaml` as follows:
   ```yaml
   webservers:
     hosts:
       <instance-name>:
         ansible_ssh_extra_args: "-J <your-bastion-username>@bastion.wmcloud.org"
         ansible_user: <your-bastion-username>
   ```
4. Run `ansible-playbook -i inventory.yml playbook.yml

### Customize nginx (access rules)

The `api` image ships its own nginx config, kept in [`ansible/overpass/nginx/`](ansible/overpass/nginx/):

- [`nginx.conf.template`](ansible/overpass/nginx/nginx.conf.template): a copy of the upstream image's `/etc/nginx/nginx.conf.template` with our access rules added, copied into the image at build time. It is still rendered by the image entrypoint with `envsubst`, so the `${NGINX_*}` placeholders keep working;
- [`user-agents/`](ansible/overpass/nginx/user-agents/): custom User-Agent whitelist, every `*.conf` file in it is loaded (see [`whitelist.conf`](ansible/overpass/nginx/user-agents/whitelist.conf) for the syntax). It is baked into the image as a default **and** bind-mounted read-only by `compose.yml`, so it can be edited live on the server (`/opt/overpass/nginx/user-agents/`) without rebuilding or restarting.

After editing the whitelist, validate and reload nginx (an invalid file is rejected and the running config is kept):

```sh
docker compose exec api sh -c 'nginx -t && nginx -s reload'
```

> [!WARNING]
> - Always run `nginx -t` after an edit: if the container restarts with an invalid whitelist, nginx won't start;
> - files must stay world-readable (e.g. `0644`), nginx runs as a non-root user inside the container;
> - re-running the Ansible playbook overwrites the server copy with the one in this repo, so commit whitelist changes here too.

Current access rules:

1. requests whose User-Agent is neither a major browser (loosely detected: Firefox, Chrome/Chromium, Safari, Edge, Opera, Samsung Internet, Vivaldi, Yandex, IE) nor whitelisted in `user-agents/` get a `403`;
2. browsers must also send a `Referer`, otherwise `403`;
3. whitelisted agents (`allowed`) don't need a `Referer`;
4. requests from inside the container (loopback) are always allowed, so the image's healthcheck keeps working.

To bake completely different defaults into the image, change the `NGINX_TEMPLATE` / `NGINX_USER_AGENTS_DIR` build args in [`compose.yml`](ansible/overpass/compose.yml) (paths are relative to `ansible/overpass/`) and rebuild with `docker compose build api`.

> [!IMPORTANT]
> When bumping the upstream image digest, re-sync the template with the new upstream one and re-apply the access-control section:
> ```sh
> docker run --rm --entrypoint cat b1tw153/overpass-api@sha256:<digest> /etc/nginx/nginx.conf.template
> ```

> [!NOTE]
> Ansible may break especially on the docker deploy part, you can run them manually directly on the server via `docker compose up import` or `docker compose up api -d`
