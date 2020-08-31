#!/bin/bash

for f in `ls | grep resnet-imagenet-8192bs | grep -v 'OOM\|txt'`; do
  echo "$f"
  grep -B 1 "val_sparse_categorical_accuracy" "$f"/1/rank.0/stderr | grep -v "\-\-" | sed 'N;s/\n/ /' | sed 's/Epoch \([0-9]*\)\/90 .* val_sparse_categorical_accuracy: \([\.0-9]*\).*/\1 \2/g' > "${f}.txt"
done

