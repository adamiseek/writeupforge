#!/usr/bin/env python3
"""
writeupforge — turn CTF notes into clean, structured writeups.

Interactive CLI that walks you through a box (platform, target, recon,
exploitation, privesc, flags, lessons) and produces a consistent markdown
writeup — the kind that gets hired. Works for TryHackMe, HackTheBox, and
self-hosted labs.

USAGE:
    writeupforge                 # interactive writeup builder
    writeupforge init NAME       # scaffold a blank writeup skeleton
    writeupforge list            # show saved writeups
"""

import argparse
import datetime as dt
import os
import re
import sys

PROG = "writeupforge"
VERSION = "0.1.0"
DEFAULT_DIR = "writeups"

PLATFORMS = {
    "thm": "TryHackMe",
    "htb": "HackTheBox",
    "lab": "Self-hosted lab",
    "other": "Other / personal",
}

DIFFICULTIES = ["easy", "medium", "hard", "insane"]

SECTIONS = [
    ("summary", "Summary (one paragraph: what the box is, the vuln in one line)"),
    ("recon", "Recon (ports, services, versions, what looked interesting)"),
    ("enumeration", "Enumeration (directories, files, users, anything juicy)"),
    ("exploitation", "Exploitation (the entry point, the payload, the proof)"),
    ("privesc", "Privilege Escalation (how you got from user to root)"),
    ("lessons", "Lessons Learned (what you'd do different / will remember)"),
]

# ---------------------------------------------------------------- helpers

def _slug(name):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "writeup"


def _ask(prompt, default=None):
    suffix = f" [{default}]" if default else ""
    while True:
        ans = input(f"  {prompt}{suffix}: ").strip()
        if ans:
            return ans
        if default:
            return default
        print("    (can't be empty — press Ctrl+C to abort)")


def _ask_multi(prompt, default=None):
    """Collect a list; blank line ends. Returns [] when skipped."""
    print(f"  {prompt} (one per line, blank line to finish)")
    items = []
    while True:
        raw = input("    > ").rstrip()
        if not raw:
            break
        items.append(raw)
    return items


def _yesno(prompt, default=False):
    hint = "y/N" if not default else "Y/n"
    ans = input(f"  {prompt} [{hint}]: ").strip().lower()
    if not ans:
        return default
    return ans in ("y", "yes")


def _front_matter(meta, body):
    lines = ["---"]
    lines += [f"{k}: {v}" for k, v in meta.items()]
    lines += ["---", "", body]
    return "\n".join(lines)


# -------------------------------------------------------------- builders

def build_skeleton(name, platform, target=None, difficulty=None):
    meta = {
        "title": name,
        "platform": PLATFORMS.get(platform, platform),
        "difficulty": difficulty or "unknown",
        "target": target or "N/A",
        "date": dt.date.today().isoformat(),
        "status": "in-progress",
    }
    parts = [f"# {name}", ""]
    parts.append(f"> **Platform:** {meta['platform']} · **Difficulty:** {meta['difficulty']}"
                 f" · **Target:** {meta['target']} · **Date:** {meta['date']}")
    parts += ["", "## Flags", "", "| Flag | Type | Value |", "|------|------|-------|",
              "| User |   |   |", "| Root |   |   |", ""]
    for key, hint in SECTIONS:
        parts += [f"## {key.capitalize()}", f"<!-- {hint} -->", ""]
    return _front_matter(meta, "\n".join(parts))


def build_interactive(name, platform, difficulty, target):
    print(f"\n  Writeup for {name} — fill in what you found. Blank a section to skip.")
    print("  " + "-" * 56)

    summary = _ask("Summary", "One-line win: 'RCE via unsafe YAML deserialization in /import'")
    summary_text = _ask_multi("Discovery / recon notes")
    explo_text = _ask_multi("Exploitation steps (commands, payloads, output)")
    priv_text = _ask_multi("Privilege escalation steps")
    less_text = _ask_multi("Lessons learned")
    flags = []
    print("  Flags found (one per line, blank to finish)")
    while True:
        raw = input("    > ").strip()
        if not raw:
            break
        flags.append(raw)

    meta = {
        "title": name,
        "platform": PLATFORMS.get(platform, platform),
        "difficulty": difficulty,
        "target": target or "N/A",
        "date": dt.date.today().isoformat(),
        "status": "complete" if flags else "in-progress",
    }

    parts = [f"# {name}", ""]
    parts.append(f"> **Platform:** {meta['platform']} · **Difficulty:** {difficulty}"
                 f" · **Target:** {meta['target']} · **Date:** {meta['date']}")
    parts += ["", "## Summary", "", summary, ""]

    parts += ["## Flags", "", "| # | Value |", "|---|-------|"]
    if flags:
        for i, f in enumerate(flags, 1):
            parts.append(f"| {i} | `{f}` |")
    else:
        parts.append("| — | — |")
    parts += [""]

    sections = [
        ("Recon", summary_text),
        ("Exploitation", explo_text),
        ("Privilege Escalation", priv_text),
        ("Lessons Learned", less_text),
    ]
    for title, notes in sections:
        parts += [f"## {title}", ""]
        if notes:
            for n in notes:
                parts.append(("- " if not n.startswith(("```", "  ")) else "") + n)
        else:
            parts.append("_Skipped._")
        parts += [""]

    return _front_matter(meta, "\n".join(parts))


def _resolve_outdir(name, directory):
    path = os.path.join(directory, _slug(name))
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, "writeup.md")


# ----------------------------------------------------------------- main

def cmd_list(directory):
    if not os.path.isdir(directory):
        print("[-] No writeups yet.")
        return 0
    found = []
    for root, _dirs, files in os.walk(directory):
        for f in files:
            if f == "writeup.md":
                rel = os.path.relpath(root, directory)
                found.append(rel)
    if not found:
        print("[-] No writeups yet.")
        return 0
    print(f"\n  writeupforge — {len(found)} writeup(s) in {directory}/:")
    for name in sorted(found):
        print(f"    • {name}")
    print()
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="writeupforge — CTF notes into structured markdown writeups.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("command", nargs="?", default="new",
                        choices=["new", "init", "list", "append"],
                        help="new = interactive build, init = blank skeleton, list = saved writeups, append = add findings to existing")
    parser.add_argument("name", nargs="?", help="room/box name")
    parser.add_argument("--platform", default="thm", choices=list(PLATFORMS.keys()),
                        help="platform for front matter")
    parser.add_argument("--difficulty", default=None, choices=DIFFICULTIES,
                        help="difficulty rating")
    parser.add_argument("--target", default=None, help="target IP or host")
    parser.add_argument("--dir", default=DEFAULT_DIR, help="output directory")
    args = parser.parse_args()

    if args.command == "list":
        return cmd_list(args.dir)

    if args.command == "init":
        name = args.name or sys.exit("[-] init needs a name: writeupforge init hh-beachbar")
        body = build_skeleton(name, args.platform, args.target, args.difficulty)
        out = _resolve_outdir(name, args.dir)
        with open(out, "w") as f:
            f.write(body)
        print(f"[+] Skeleton written to {out}")
        return 0

    if args.command == "append":
        name = args.name or sys.exit("[-] append needs a name: writeupforge append hh-beachbar")
        # find the writeup file
        slug = _slug(name)
        candidate = os.path.join(args.dir, slug, "writeup.md")
        if not os.path.isfile(candidate):
            candidate = os.path.join(args.dir, name, "writeup.md")
        if not os.path.isfile(candidate):
            sys.exit(f"[-] No writeup found for '{name}'. Run 'list' to see available writeups.")
        with open(candidate) as f:
            content = f.read()
        sections = ["recon", "exploitation", "privesc", "lessons", "enumeration"]
        print(f"  Appending to: {candidate}")
        print(f"  Available sections: {', '.join(sections)}")
        target_section = _ask("Section to append to", "exploitation").lower()
        if target_section not in sections:
            sections.append(target_section)
        notes = _ask_multi("New findings (one per line, blank to finish)")
        if not notes:
            print("[-] Nothing to append.")
            return 0
        # find the target section header and insert after it
        marker = f"## {target_section.capitalize()}"
        lines = content.split("\n")
        insert_idx = None
        for i, line in enumerate(lines):
            if line.strip().lower().startswith(marker.lower()):
                # find the end of the section (next ## or end of file)
                for j in range(i + 1, len(lines)):
                    if lines[j].strip().startswith("## ") or j == len(lines) - 1:
                        insert_idx = j
                        break
                break
        if insert_idx is None:
            print(f"[-] Section '{target_section}' not found in writeup.")
            return 0
        for note in notes:
            lines.insert(insert_idx, f"- {note}")
            insert_idx += 1
        with open(candidate, "w") as f:
            f.write("\n".join(lines))
        print(f"[+] Appended {len(notes)} line(s) to {target_section} section")
        return 0

    # interactive build
    print(r"""
  __        __  __ _        _____ ___ ____  ______ ____
  \ \      / / |  | |      | ____|_ _|  _ \|  ____| __ ) ______ _ _ __ _
   \ \ /\ / /  |  | | |   |  _|  | | | |_) | |_  |  _ \|_  / _` | '__| | |
    \ V  V /   |  |__| |__| | |___ | | |  __/|  _| | |_) |/ / (_| | |  |_|_|
     \_/\_/     \____/|____|_____|___|_|   |_|   |____/___\__,_|_|  (_)
    """)
    if not args.name:
        name = _ask("Box / room name", None)
    else:
        name = args.name
    if not args.difficulty:
        args.difficulty = _ask("Difficulty (easy/medium/hard/insane)", "easy").lower()
        if args.difficulty not in DIFFICULTIES:
            args.difficulty = "easy"
    if not args.target:
        args.target = _ask("Target IP (optional)", None) or None

    body = build_interactive(name, args.platform, args.difficulty, args.target)
    out = _resolve_outdir(name, args.dir)
    with open(out, "w") as f:
        f.write(body)
    print(f"\n[+] Writeup saved to {out}")

    # echo the important part so it's visible immediately
    print("\n  -------- summary --------")
    for line in body.splitlines():
        if line.startswith(("|", ">", "#")) or line.strip():
            if not line.startswith(("---", "title:", "platform:", "difficulty:",
                                    "target:", "date:", "status:")):
                print("  " + line)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[-] Interrupted.")
        sys.exit(130)
