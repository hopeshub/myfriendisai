# SSH Setup: Remote Access to Mac Mini

## Context

Walker is traveling to Portland and needs to be able to check on his Mac Mini remotely from his laptop. The Mac Mini runs a daily launchd job that collects Reddit data. He needs to be able to SSH in to check logs and verify collection is running.

## Steps (do these manually, not via CC)

### 1. Enable Remote Login on the Mac Mini

- Open **System Settings → General → Sharing**
- Turn on **Remote Login**
- Note your Mac Mini's local username (run `whoami` in terminal)

### 2. Find your Mac Mini's local IP

Run this in terminal:

```
ipconfig getifaddr en0
```

Note the IP (something like 192.168.1.xxx). This only works on the same network though — for remote access from Portland you need the next step.

### 3. Set up remote access with Tailscale (easiest option)

Tailscale creates a private network between your devices — no port forwarding, no router config, works through NAT. Free for personal use.

**On the Mac Mini:**
1. Go to https://tailscale.com and create an account
2. Download and install Tailscale for Mac
3. Sign in — it will assign your Mac Mini a Tailscale IP (like 100.x.x.x)
4. Note this IP

**On your laptop:**
1. Download and install Tailscale
2. Sign in with the same account
3. Your laptop gets its own Tailscale IP

**Test it (while still at home):**
```
ssh your-username@100.x.x.x
```

If you get a terminal prompt on the Mac Mini, you're set.

### 4. Check collection logs remotely

Once SSH'd in from Portland, run:

```
# Check if collection ran today
cat ~/projects/myfriendisai/logs/collect-$(date +%Y-%m-%d).log

# Or check the most recent log
ls -lt ~/projects/myfriendisai/logs/ | head -5

# Check if the launchd job is loaded
launchctl list | grep myfriendisai

# Run collection manually if needed
cd ~/projects/myfriendisai && python scripts/collect_posts.py
```

Note: the log path above is a guess based on the run_collect.sh wrapper. Check the actual path before you leave by running:

```
cat scripts/run_collect.sh
```

### 5. Before you leave checklist

- [ ] Tailscale installed and signed in on BOTH machines
- [ ] SSH works from laptop → Mac Mini via Tailscale IP
- [ ] "Prevent automatic sleeping" is ON in System Settings → Energy
- [ ] Mac Mini is plugged in, powered on, not going to be unplugged
- [ ] Run one manual collection to verify pipeline is healthy
- [ ] Check the log path so you know where to look remotely
