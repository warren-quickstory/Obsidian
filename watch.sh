#!/bin/bash
VAULT=/home/admin/obsidian-vault

cd "$VAULT"

echo "[$(date)] Obsidian vault watcher started"

inotifywait -m -r -e modify,create,delete,move \
  --exclude '\.git' \
  "$VAULT" | while read -r dir event file; do
    echo "[$(date)] $event: $dir$file"
    sleep 2  # 短暂等待，合并连续写入
    git pull --rebase origin main 2>/dev/null
    git add -A
    if ! git diff --cached --quiet; then
      git commit -m "sync: $(date '+%Y-%m-%d %H:%M:%S') - $file"
      git push origin main
      echo "[$(date)] Pushed: $file"
    fi
done
