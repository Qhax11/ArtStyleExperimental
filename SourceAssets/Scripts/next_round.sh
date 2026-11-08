#!/bin/bash
# Usage: next_round.sh <round> <mode> <blob-prefix-suffix pairs...>  (paths relative to tool-results)
cd "/c/Users/samil/.claude/projects/D--Projects-ArtStyleExperimental/eefd7457-c5b7-495c-8e73-e87620be5456/tool-results"
r=$1; m=$2; shift 2
python /d/Projects/ArtStyleExperimental/SourceAssets/Scripts/vroid_round_plan.py $r $m "$@"
