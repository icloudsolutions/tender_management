# Deploy to Odoo 18 test server

Update **ics_tender_management** and **ics_etimad_tenders_crm** on the test server when changes are pushed to `main` on [github.com/icloudsolutions/tender_management](https://github.com/icloudsolutions/tender_management) (only when [ics_tender_management](https://github.com/icloudsolutions/tender_management/tree/main/ics_tender_management) or [ics_etimad_tenders_crm](https://github.com/icloudsolutions/tender_management/tree/main/ics_etimad_tenders_crm) are modified).

## Server

- **Host:** `38.242.237.64`
- **Addons path:** `/root/libya/dev-18/addons` (existing folders `ics_etimad_tenders_crm` and `ics_tender_management` are updated in place)
- **Stack:** Docker Compose (PostgreSQL 17 + Odoo 18)

## One-time server setup

1. On the server, ensure the addons directory exists:
   ```bash
   ssh root@38.242.237.64 "mkdir -p /root/libya/dev-18/addons"
   ```

2. Mount addons into the Odoo container (if not already):
   - Copy `deploy/docker-compose.override.example.yml` to the server as `docker-compose.override.yml` in `/root/libya/dev-18`, or add to your existing compose:
   ```yaml
   # In odoo18 service:
   volumes:
     - ./addons:/mnt/extra-addons
   command: --addons-path=/mnt/extra-addons
   ```
   - Restart: `docker compose up -d`

3. In Odoo: Apps → Update Apps List, then install/upgrade **ICS Etimad Tenders CRM** and **ICS Tender Management**.

## GitHub Actions CI/CD

### Required secrets

In the repo: **Settings → Secrets and variables → Actions** add **Secrets** (and optionally **Variables**):

| Secret                    | Description                           | Example        |
|---------------------------|---------------------------------------|----------------|
| `DEPLOY_HOST`             | Server IP or hostname                 | `38.242.237.64` |
| `DEPLOY_USER`             | SSH user (e.g. root)                  | `root`         |
| `DEPLOY_SSH_KEY`          | Private SSH key (full PEM content)    | See below      |
| `DEPLOY_SSH_PORT`         | (Optional) SSH port                   | `22`           |
| `DEPLOY_ODOO_DATABASE`    | (Optional) **Variable** (not secret): Odoo DB name to run upgrade after deploy | `postgres` or your DB name |

#### How to generate `DEPLOY_SSH_KEY`

1. **Generate a new SSH key pair** (on your PC or any machine; use a passphrase or leave empty for automation):

   ```bash
   ssh-keygen -t ed25519 -C "github-actions-deploy" -f deploy_key -N ""
   ```

   This creates `deploy_key` (private) and `deploy_key.pub` (public). Use a different path if you prefer (e.g. `~/.ssh/deploy_tender_management`).

2. **Add the public key to the server** so it accepts logins from GitHub Actions:

   - **From your PC** (if you can SSH to the server): run `deploy\setup-server-authorized-key.ps1` in PowerShell, or:
     ```powershell
     Get-Content deploy_key.pub | ssh root@38.242.237.64 "mkdir -p ~/.ssh; cat >> ~/.ssh/authorized_keys"
     ```
   - **If you're already logged in on the server**, paste this line into the server (replace with the contents of `deploy_key.pub` if needed):
     ```bash
     echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIN7S2Pl5MT0p9qNUFZlBMOlJ6R3om6it/0lr5MgJ28I3 github-actions-deploy" >> ~/.ssh/authorized_keys
     ```

3. **Add the private key to GitHub** as the secret `DEPLOY_SSH_KEY`:
   - Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**
   - Name: `DEPLOY_SSH_KEY`
   - Value: paste the **entire** contents of `deploy_key` (the private file), including the lines `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----`.

4. **Security:** Delete the private key from your machine after adding it to GitHub if you no longer need it locally: `del deploy_key deploy_key.pub` (Windows) or `rm deploy_key deploy_key.pub` (Linux/macOS).

### When it runs

- **Push to `main`** on [icloudsolutions/tender_management](https://github.com/icloudsolutions/tender_management) when files under `ics_tender_management/`, `ics_etimad_tenders_crm/`, or the workflow file change.
- **Manual:** Actions → Deploy to Odoo Test Server → Run workflow.

### What it does

1. Checkout the repository.
2. Rsync `ics_tender_management` and `ics_etimad_tenders_crm` into `/root/libya/dev-18/addons/` on the server (updates the two modules in place).
3. Restart the `odoo18` container so new code is loaded.
4. If the **variable** `DEPLOY_ODOO_DATABASE` is set: run `odoo -u ics_etimad_tenders_crm,ics_tender_management` so the two modules are upgraded in that database (no need to upgrade from Apps UI).

## Local deploy (optional)

From the project root, with SSH access to the server:

```bash
# From repo root
rsync -avz --delete ics_tender_management/ user@38.242.237.64:/root/libya/dev-18/addons/ics_tender_management/
rsync -avz --delete ics_etimad_tenders_crm/ user@38.242.237.64:/root/libya/dev-18/addons/ics_etimad_tenders_crm/
ssh user@38.242.237.64 "cd /root/libya/dev-18 && docker compose restart odoo18"
```

Replace `user` with your SSH user (e.g. `root`).
