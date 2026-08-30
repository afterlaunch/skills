#!/bin/sh
# Copy the canonical skill from the monorepo into this staged repo. The
# monorepo copy (.claude/skills/reddit-desk) is the ONE source; this script is
# how it gets here, so the two cannot drift by hand-editing.
set -e
cd "$(dirname "$0")"
rm -rf skills/reddit-desk
mkdir -p skills
cp -R ../../.claude/skills/reddit-desk skills/reddit-desk
echo "synced: $(find skills/reddit-desk -type f | wc -l | tr -d ' ') files"
