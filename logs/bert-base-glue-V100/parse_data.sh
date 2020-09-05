#!/bin/bash

for f in $(ls | grep bert | grep -v txt); do
  echo "$f"
  grep val_test_accuracy "$f"/1/rank.0/stderr | nl | sed 's/ - val_loss: [\.0-9]*//g' | awk '{print $1 " " $NF}' > "${f}.txt"
  grep val_test_accuracy "$f"/1/rank.0/stderr | awk '{cum_sum += $4; $4 = cum_sum}1' | sed 's/ - val_loss: [\.0-9]*//g' | awk '{print $4 " " $NF}' > "${f}-time.txt"
done

# HACK: Truncate some baseline logs because we accidentally ran them for too long
for f in $(ls bert*baseline*txt); do
  NUM_GPUS="$(echo "$f" | sed 's/.*_\([0-9]*\)gpu_.*/\1/g')"
  NUM_LINES="$((50 / NUM_GPUS))"
  echo "Truncating $f to $NUM_LINES lines"
  head -n "$NUM_LINES" "$f" > temp.txt
  mv temp.txt "$f"
done

