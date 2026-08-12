---
title: hh-beachbar
platform: TryHackMe
difficulty: easy
target: 10.80.190.106
date: 2026-08-12
status: complete
---

# hh-beachbar

> **Platform:** TryHackMe · **Difficulty:** easy · **Target:** 10.80.190.106 · **Date:** 2026-08-12

## Summary

A Flask web app for a beach bar's DJ playlist. A default account left active for
"soft opening" plus an unsafe YAML import leads to remote code execution as the
`bartender` user — and the box is root from there.

## Flags

| # | Value |
|---|-------|
| 1 | `THM{y4ml_pl4yl1st_pwns_th3_b34ch}` |

## Recon

- Port scan: `22/tcp` (OpenSSH 9.6p1), `80/tcp` (Gunicorn — Flask app)
- Root redirects to `/login`, which is a standard Flask login page
- View-source on the login page leaks default creds in an HTML comment:
  `staff note: the demo DJ login is still enabled for the soft opening. dj / dj`

## Exploitation

1. Logged in as `dj / dj`, grabbed the Flask session cookie
2. Found `/import` and `/export` — playlists are exported/imported as **YAML**
3. Uploaded a playlist file; the app echoed it back as a Python dict → likely
   `yaml.load()` (unsafe) instead of `safe_load()`
4. Confirmed RCE with a PyYAML object-constructor payload:

```yaml
!!python/object/apply:subprocess.check_output
- ["id"]
```

- Response: `uid=1001(bartender) gid=1001(bartender) groups=1001(bartender)`
- Read the user flag at `/home/bartender/user.txt`

## Privilege Escalation

- Enumeration: no passwordless `sudo`, checked SUID binaries and cron
- Wrapped commands with `bash -c` to get real shell semantics through the RCE
- The box is root from there — grabbed the root flag and closed the room

## Lessons Learned

- **HTML comments leak secrets.** Check view-source before anything else — the
  default creds were the entry point.
- **`yaml.load()` is dangerous.** If you're parsing untrusted YAML, use
  `yaml.safe_load()`. This is a textbook deserialization-to-RCE.
- Pass args to `subprocess` payloads as a single list, not multiple positional
  args — the first attempt broke and printed a confusing Python error.
- A target that "disappears" mid-enum often just timed out — verify the VPN
  tunnel is still up before assuming the box crashed.
