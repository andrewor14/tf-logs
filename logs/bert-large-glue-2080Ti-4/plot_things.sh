#!/bin/bash

CURRENT_DIR="$(basename $PWD)"
GLUE_TASKS="RTE WNLI CoLA MRPC"
cd ../..

export BOLD_BASELINE="true"
for glue_task in $GLUE_TASKS; do
  if [[ "$glue_task" == "RTE" ]]; then
    export PUT_LEGEND_OUTSIDE="true"
  else
    unset PUT_LEGEND_OUTSIDE
  fi
  export TITLE="BERT (large) GLUE $glue_task on 1 GPU"
  export DATA_FILE_PREFIX="logs/${CURRENT_DIR}/bert-glue-${glue_task}_"
  OUTPUT_FILE_PREFIX="bert-large-glue-${glue_task}-2080Ti"
  OUTPUT_FILE="${OUTPUT_FILE_PREFIX}.pdf"\
    ./plot_accuracy.py $(ls ${DATA_FILE_PREFIX}*vn*txt | grep -v time | xargs)
  OUTPUT_FILE="${OUTPUT_FILE_PREFIX}-time.pdf" XLABEL="Time elapsed (s)"\
    DATA_FILE_SUFFIX="-time.txt" ./plot_accuracy.py "$DATA_FILE_PREFIX"*time.txt
done

