#!/bin/bash

for f in $(ls | grep bert | grep -v txt); do
  echo "$f"
  grep val_test_accuracy "$f"/1/rank.0/stderr | nl | sed 's/ - val_loss: [\.0-9]*//g' | awk '{print $1 " " $NF}' > "${f}.txt"
  grep val_test_accuracy "$f"/1/rank.0/stderr | awk '{cum_sum += $4; $4 = cum_sum}1' | sed 's/ - val_loss: [\.0-9]*//g' | awk '{print $4 " " $NF}' > "${f}-time.txt"
done

