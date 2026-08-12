# writeupforge

Turn CTF notes into clean, structured writeups — fast.

Interactive CLI that walks you through a box (platform, target, recon,
exploitation, privesc, flags, lessons) and produces consistent markdown
writeups with proper front matter. Built for TryHackMe, HackTheBox, and
self-hosted labs. Zero dependencies.

## Features

- **Interactive builder** — asks section-by-section, skips what you don't have
- **Consistent structure** — front matter + summary + flags table + recon /
  exploitation / privesc / lessons sections (exactly what employers read)
- **`init` mode** — scaffolds a blank writeup skeleton to fill in later
- **`list` mode** — shows saved writeups
- **Smart status** — auto-marks a writeup `complete` when you add flags
- YAML front matter (title, platform, difficulty, target, date, status)
- Files organized as `writeups/<box-name>/writeup.md`

## Example writeup

See a complete, real writeup in [`examples/hh-beachbar.md`](examples/hh-beachbar.md) —
a TryHackMe room exploited via unsafe YAML deserialization. Run the tool
yourself to reproduce that structure.

## Usage

```sh
# interactive build
python3 writeupforge.py new

# scaffold a blank skeleton for later
python3 writeupforge.py init hh-beachbar --platform thm --difficulty easy

# list what you've written
python3 writeupforge.py list

# non-default options
python3 writeupforge.py new --platform htb --difficulty hard
```

## Example output (front matter + flags table)

```markdown
---
title: beachbar-demo
platform: TryHackMe
difficulty: easy
target: 10.80.190.106
date: 2026-08-12
status: complete
---

## Flags

| # | Value |
|---|-------|
| 1 | `THM{y4ml_pl4yl1st_pwns_th3_b34ch}` |
```

## Requirements

Python 3.8+. No third-party packages.

## Tests

```sh
python3 -m unittest test_writeupforge -v
```

## Roadmap

- [ ] Export to HTML/PDF for easy sharing
- [ ] Flag registry (track all flags across writeups)
- [ ] `--append` mode to add findings to an existing writeup
- [ ] Writeup template gallery (THM / HTB / custom styles)

## Why writeups

Writing up your boxes is how you turn TryHackMe hours into an interview
story. A clean, honest writeup on GitHub shows recruiters you can think
methodically — the skill they actually hire for.
