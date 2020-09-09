#!/bin/bash

CURRENT_DIR="$(basename $PWD)"
GLUE_TASKS="SST-2 QNLI CoLA"
export BASELINE_STEPS_MULTIPLIER=8
cd ../..

export SPACE_XTICKS_APART="true"
export GROUP_BARS="true"
for glue_task in $GLUE_TASKS; do
  if [[ "$glue_task" == "CoLA" ]]; then
    export YLIM="0.5,0.85"
  fi
  export TITLE="BERT-BASE finetuning on $glue_task"
  export DATA_FILE_PREFIX="logs/${CURRENT_DIR}/bert-glue-${glue_task}_"
  OUTPUT_FILE_PREFIX="bert-base-glue-${glue_task}-V100"
  OUTPUT_FILE="${OUTPUT_FILE_PREFIX}.pdf" STEPS_PER_EPOCH="100"\
    ./plot_accuracy.py $(ls ${DATA_FILE_PREFIX}*vn*txt | grep -v time | xargs)
  OUTPUT_FILE="${OUTPUT_FILE_PREFIX}-time.pdf" XLABEL="Time elapsed (s)"\
    DATA_FILE_SUFFIX="-time.txt" ./plot_accuracy.py "$DATA_FILE_PREFIX"*-time*.txt
  OUTPUT_FILE="${OUTPUT_FILE_PREFIX}-time-2.pdf" FIGURE_SIZE="13,6"\
    ./plot_time.py "$DATA_FILE_PREFIX"*-time.txt
  unset YLIM
done

