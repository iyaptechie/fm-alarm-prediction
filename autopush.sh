#!/bin/bash
cd /workspaces/fm-alarm-prediction/fm-alarm-prediction
while true; do
    git add .
    git commit -m "auto-save: $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null
    git push origin master 2>/dev/null
    echo "✅ Auto-pushed at $(date '+%H:%M:%S')"
    sleep 300
done
