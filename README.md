# Remote

A native app to control your SmartCast TV, navigate apps, and type on your TV from your computer over local network. Pairs once over your local network during first launch.

## Install

**Requirements:** Python 3.11+ · TV and computer on the same Wi-Fi

```bash
git clone https://github.com/iviraa/remote.git
cd remote
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
tv-app
```

## Config

Credentials stored at `~/.config/tvremote/config.json`. Delete to re-pair.
