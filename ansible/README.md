# Ansible Certificate Monitor Setup

This folder shows how Ansible could install and configure the Python certificate expiry monitor.

It uses placeholder/public endpoints only. Do not commit real internal endpoints, credentials, tokens, or secrets.

## What It Demonstrates

- Inventory for a target host group.
- Variables for install path, thresholds, schedule, and endpoints.
- Template rendering for endpoint configuration.
- Idempotent tasks for directory creation and file copying.
- A scheduling example that could become a cron job on Linux targets.

## Files

- `inventory.ini` - Defines the local target group.
- `vars.yml` - Defines configurable values.
- `templates/endpoints.txt.j2` - Renders endpoint list from variables.
- `install_cert_monitor.yml` - Installs the script and rendered config.

## Run Syntax Check

Ansible is most natural from Linux/macOS. On this Windows lab machine, use WSL:

```powershell
wsl -d AlmaLinux-9 -- bash -lc "cd '/mnt/<drive>/<path>/mobile-platform-reliability-lab' && ~/.local/bin/ansible-playbook -i ansible/inventory.ini ansible/install_cert_monitor.yml --syntax-check"
```

## Run Locally

From WSL:

```bash
ansible-playbook -i ansible/inventory.ini ansible/install_cert_monitor.yml
```

For a temporary demo install path:

```bash
ansible-playbook -i ansible/inventory.ini ansible/install_cert_monitor.yml -e install_dir=/tmp/mobile-platform-cert-monitor-demo
```

Run the playbook twice to confirm idempotency. The second run should report:

```text
changed=0
```

## Explanation

> I used Ansible to show how a reliability script can be installed and configured repeatably. The playbook creates an install directory, copies the certificate monitor, renders the endpoint config from variables, and shows how it would be scheduled. The key idea is idempotency: running the playbook repeatedly should keep the target in the desired state without manual steps.
