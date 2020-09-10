#!/bin/bash

for f in `ls | grep resnet-imagenet | grep -v 'OOM\|txt'`; do
  echo "$f"
  grep -B 1 "val_sparse_categorical_accuracy" "$f"/1/rank.0/stderr | grep -v "\-\-" | sed 'N;s/\n/ /' | sed 's/Epoch \([0-9]*\)\/90 .* val_sparse_categorical_accuracy: \([\.0-9]*\).*/\1 \2/g' > "${f}.txt"
  grep "val_sparse_categorical_accuracy" "$f"/1/rank.0/stderr | awk '{cum_sum += $3; $3 = cum_sum}1' | sed 's/ - val_loss: \([0-9\.]*\)//g' | awk '{print $3 " " $NF}' > "${f}-time.txt"
  FINAL_ACCURACY="$(tail -n 1 ${f}-time.txt | awk '{print $2}')"
  AVG_THROUGHPUT="$(grep "TimeHistory" "$f"/1/rank.0/stderr | awk '{sum += $8} END {print sum/NR}')"
  echo "$AVG_THROUGHPUT $FINAL_ACCURACY" > "${f}-throughput.txt"
done

