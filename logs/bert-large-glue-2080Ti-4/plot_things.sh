#!/bin/bash

CURRENT_DIR="$(basename $PWD)"
GLUE_TASKS="${GLUE_TASKS:=QQP MNLI SST-2 RTE CoLA MRPC}"
cd ../..

export LEGEND_BASELINE_FIRST="true"
export BOLD_BASELINE="true"
export PLOT_THROUGHPUT="true"
for glue_task in $GLUE_TASKS; do
  if [[ "$glue_task" == "RTE" ]]; then
    export LEGEND_NCOL="2"
    export YLIM="0.25,0.75"
  elif [[ "$glue_task" == "MRPC" ]]; then
    export YLIM="0.5,0.9"
    export LEGEND_NCOL="2"
  fi
  export TITLE="BERT-LARGE finetuning on $glue_task"
  export DATA_FILE_PREFIX="logs/${CURRENT_DIR}/bert-glue-${glue_task}_"
  OUTPUT_FILE_PREFIX="bert-large-glue-${glue_task}-2080Ti"
  OUTPUT_FILE="${OUTPUT_FILE_PREFIX}.pdf"\
    ./plot_accuracy.py $(ls ${DATA_FILE_PREFIX}*vn*txt | grep -v time | grep -v throughput | xargs)
  OUTPUT_FILE="${OUTPUT_FILE_PREFIX}-time.pdf" XLABEL="Time elapsed (s)"\
    DATA_FILE_SUFFIX="-time.txt" ./plot_accuracy.py "$DATA_FILE_PREFIX"*time.txt
  OUTPUT_FILE="${OUTPUT_FILE_PREFIX}-throughput.pdf" DATA_FILE_SUFFIX="-time.txt"\
    HATCH_MAX_ACCURACY="true" ./plot_time.py "$DATA_FILE_PREFIX"*throughput.txt
  unset LEGEND_NCOL
  unset NUM_TOTAL_EXAMPLES
  unset YLIM
  if [[ "$glue_task" == "RTE" ]]; then
    OUTPUT_FILE="${OUTPUT_FILE_PREFIX}-2lines.pdf" LEGEND_FONT_SIZE=16\
      ./plot_accuracy.py "$DATA_FILE_PREFIX"4bs*vn_baseline.txt "$DATA_FILE_PREFIX"16bs*vn.txt
  fi
done

