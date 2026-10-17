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

> [!NOTE]
> Ansible may break especially on the docker deploy part, you can run them manually directly on the server via `docker compose up import` or `docker compose up api -d`
