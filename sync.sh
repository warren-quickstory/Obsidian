#!/bin/bash
cd /home/admin/obsidian-vault
git pull --rebase origin main 2>/dev/null
git add -A
if ! git diff --cached --quiet; then
  git commit -m "sync: $(date '+%Y-%m-%d %H:%M:%S')"
  git push origin main
fi
