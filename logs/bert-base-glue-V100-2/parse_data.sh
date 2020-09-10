#!/bin/bash

for f in $(ls | grep bert | grep -v txt); do
  echo "$f"
  grep val_test_accuracy "$f"/1/rank.0/stderr | nl | sed 's/ - val_loss: [\.0-9]*//g' | awk '{print $1 " " $NF}' > "${f}.txt"
  grep val_test_accuracy "$f"/1/rank.0/stderr | awk '{cum_sum += $4; $4 = cum_sum}1' | sed 's/ - val_loss: [\.0-9]*//g' | awk '{print $4 " " $NF}' > "${f}-time.txt"
  FINAL_ACCURACY="$(tail -n 1 ${f}-time.txt | awk '{print $2}')"
  BATCH_SIZE="$(grep TRAIN_BATCH_SIZE "$f"/1/rank.0/stderr | awk -F '=' '{print $2}')"
  AVG_EPOCH_TIME_S="$(grep val_test "$f"/1/rank.0/stderr | awk '{sum += $4} END {print sum/NR}')"
  NUM_STEPS_PER_EPOCH="$(grep val_test "$f"/1/rank.0/stderr | head -n 1 | awk -F '/' '{print $2}' | awk '{print $1}')"
  AVG_THROUGHPUT="$(python3 -c "print($BATCH_SIZE / ($AVG_EPOCH_TIME_S / $NUM_STEPS_PER_EPOCH))")"
  echo "$AVG_THROUGHPUT $FINAL_ACCURACY" > "${f}-throughput.txt"
done

