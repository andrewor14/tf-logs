#!/bin/bash

CURRENT_DIR="$(basename $PWD)"
GLUE_TASKS="CoLA QNLI SST-2"
cd ../..

export SPACE_XTICKS_APART="true"
export GROUP_BARS="true"
export PLOT_THROUGHPUT="true"
for glue_task in $GLUE_TASKS; do
  if [[ "$glue_task" == "CoLA" ]]; then
    export YLIM="0.5,0.86"
  fi
  export TITLE="BERT-BASE finetuning on $glue_task"
  export DATA_FILE_PREFIX="logs/${CURRENT_DIR}/bert-glue-${glue_task}_"
  OUTPUT_FILE_PREFIX="bert-base-glue-${glue_task}-V100"
  OUTPUT_FILE="${OUTPUT_FILE_PREFIX}.pdf"\
    ./plot_accuracy.py $(ls ${DATA_FILE_PREFIX}*vn*txt | grep -v time | grep -v throughput | xargs)
  export LEGEND_NCOL="2"
  export YLIM_FACTOR="1.25"
  OUTPUT_FILE="${OUTPUT_FILE_PREFIX}-throughput.pdf" FIGURE_SIZE="6.5,4"\
    ./plot_time.py "$DATA_FILE_PREFIX"*-throughput.txt
  unset LEGEND_NCOL
  unset YLIM_FACTOR
  unset YLIM
done

