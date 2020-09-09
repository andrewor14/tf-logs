#!/bin/bash

CURRENT_DIR="$(basename $PWD)"
GLUE_TASKS="${GLUE_TASKS:=SST-2 QNLI CoLA MNLI MRPC QQP RTE}"
cd ../..

export SPACE_XTICKS_APART="true"
export GROUP_BARS="true"
for glue_task in $GLUE_TASKS; do
  if [[ "$glue_task" == "RTE" ]]; then
    export NUM_TOTAL_EXAMPLES="$((2490 * 20))"
  elif [[ "$glue_task" == "SST-2" ]]; then
    export NUM_TOTAL_EXAMPLES="$((6735 * 20))"
  elif [[ "$glue_task" == "QNLI" ]]; then
    export NUM_TOTAL_EXAMPLES="$((10474 * 20))"
  elif [[ "$glue_task" == "CoLA" ]]; then
    export NUM_TOTAL_EXAMPLES="$((8551 * 20))"
    export YLIM="0.5,0.85"
  elif [[ "$glue_task" == "MNLI" ]]; then
    export NUM_TOTAL_EXAMPLES="$((3927 * 20))"
  elif [[ "$glue_task" == "MRPC" ]]; then
    export NUM_TOTAL_EXAMPLES="$((3668 * 20))"
  elif [[ "$glue_task" == "QQP" ]]; then
    export NUM_TOTAL_EXAMPLES="$((3638 * 20))"
  fi
  export TITLE="BERT-BASE finetuning on $glue_task"
  export DATA_FILE_PREFIX="logs/${CURRENT_DIR}/bert-glue-${glue_task}_"
  OUTPUT_FILE_PREFIX="bert-base-glue-${glue_task}-V100"
  OUTPUT_FILE="${OUTPUT_FILE_PREFIX}.pdf"\
    ./plot_accuracy.py $(ls ${DATA_FILE_PREFIX}*vn*txt | grep -v time | xargs)
  OUTPUT_FILE="${OUTPUT_FILE_PREFIX}-time.pdf" XLABEL="Time elapsed (s)"\
    DATA_FILE_SUFFIX="-time.txt" ./plot_accuracy.py "$DATA_FILE_PREFIX"*-time*.txt
  export LEGEND_NCOL="2"
  export YLIM_FACTOR="1.45"
  OUTPUT_FILE="${OUTPUT_FILE_PREFIX}-time-2.pdf" FIGURE_SIZE="8,4"\
    ./plot_time.py "$DATA_FILE_PREFIX"*-time.txt
  unset LEGEND_NCOL
  unset YLIM_FACTOR
  unset YLIM
done

