#!/bin/bash

CURRENT_DIR="$(basename $PWD)"
GLUE_TASKS="${GLUE_TASKS:=RTE WNLI CoLA MRPC}"
cd ../..

export LEGEND_BASELINE_FIRST="true"
export BOLD_BASELINE="true"
for glue_task in $GLUE_TASKS; do
  if [[ "$glue_task" == "RTE" ]]; then
    export YLIM="0.35,0.75"
  else
    unset YLIM
  fi
  export TITLE="BERT (large) GLUE $glue_task on 1 GPU"
  export DATA_FILE_PREFIX="logs/${CURRENT_DIR}/bert-glue-${glue_task}_"
  OUTPUT_FILE_PREFIX="bert-large-glue-${glue_task}-2080Ti"
  OUTPUT_FILE="${OUTPUT_FILE_PREFIX}.pdf"\
    ./plot_accuracy.py $(ls ${DATA_FILE_PREFIX}*vn*txt | grep -v time | xargs)
  OUTPUT_FILE="${OUTPUT_FILE_PREFIX}-time.pdf" XLABEL="Time elapsed (s)"\
    DATA_FILE_SUFFIX="-time.txt" ./plot_accuracy.py "$DATA_FILE_PREFIX"*time.txt
  OUTPUT_FILE="${OUTPUT_FILE_PREFIX}-time-2.pdf" DATA_FILE_SUFFIX="-time.txt"\
    HATCH_MAX_ACCURACY="true" ./plot_time.py "$DATA_FILE_PREFIX"*time.txt
done

