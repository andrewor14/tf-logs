#!/usr/bin/env python3

import os
import re
import sys

import matplotlib.pyplot as plt
import numpy as np

def main():
  args = sys.argv
  if len(args) == 1:
    print("Usage: ./plot_time.py [data1.txt] [data2.txt] [data3.txt] ...")
    print("  Each data file contains two columns: cumulative time and validation accuracy")
    sys.exit(1)
  data_files = args[1:]
  title = os.getenv("TITLE", "ResNet-50 on ImageNet")
  output_file = os.getenv("OUTPUT_FILE", "output.pdf")
  data_file_prefix = os.getenv("DATA_FILE_PREFIX", "resnet-imagenet-")
  data_file_suffix = os.getenv("DATA_FILE_SUFFIX", ".txt")
  figure_size = os.getenv("FIGURE_SIZE")
  time_unit = os.getenv("TIME_UNIT", "s")
  hatch_max_accuracy = os.getenv("HATCH_MAX_ACCURACY", "").lower() == "true"

  # Sort the labels
  def sort_key(label):
    label = label.replace(data_file_prefix, "")
    m = re.match("([0-9]+)bs_([0-9]+)gpu.*", label)
    if m is not None:
      batch_size, num_gpus = m.groups()
    else:
      batch_size = int(re.match("([0-9]+)bs.*", label).groups()[0])
      num_gpus = 1
    return (int(batch_size) * 10 + int(num_gpus)) *\
      (0 if "baseline" in label else 1)

  data_files.sort(key=sort_key)

  def get_label(data_file):
    label = data_file.replace(data_file_prefix, "").replace(data_file_suffix, "")
    m = re.match("([0-9]+)bs_([0-9]+)gpu_([0-9]+)vn.*", label)
    if m is not None:
      batch_size, num_gpus, num_vns = re.match("([0-9]+)bs_([0-9]+)gpu_([0-9]+)vn.*", label).groups()
      num_gpus = "%s GPU%s" % (num_gpus, "s" if int(num_gpus) > 1 else "")
      batch_size = "%sbs" % batch_size
      num_vns = "%sVN" % num_vns
      maybe_baseline = "(baseline)" if "baseline" in data_file else ""
      return "%s\n%s\n%s\n%s" % (num_gpus, batch_size, num_vns, maybe_baseline)
    else:
      batch_size, num_vns = re.match("([0-9]+)bs_([0-9]+)vn.*", label).groups()
      batch_size = "%sbs" % batch_size
      num_vns = "%sVN" % num_vns
      maybe_baseline = "(baseline)" if "baseline" in data_file else ""
      return "%s\n%s\n%s" % (batch_size, num_vns, maybe_baseline)

  # Plot it
  if figure_size is not None:
    width = float(figure_size.split(",")[0])
    height = float(figure_size.split(",")[1])
    fig = plt.figure(figsize=(width, height))
  else:
    fig = plt.figure()
  ax = fig.add_subplot(1, 1, 1)
  ax.set_xlabel("Configuration", fontsize=24, labelpad=15)
  ax.set_ylabel("Completion time (%s)" % time_unit, fontsize=24, labelpad=15)
  labels = []
  colors = []
  elapsed_time = []
  final_accuracies = []
  for data_file in data_files:
    labels.append(get_label(data_file))
    with open(data_file) as f:
      split = f.readlines()[-1].strip().split(" ")
      elapsed_seconds = int(split[0])
      if time_unit == "s":
        elapsed_time.append(elapsed_seconds)
      else:
        elapsed_time.append(elapsed_seconds / 60)
      final_accuracies.append(float(split[1]))
      colors.append("cornflowerblue" if "baseline" in data_file else "orange")
  bars = []
  for i in range(len(labels)):
    hatch = "/" if hatch_max_accuracy and i == int(np.argmax(final_accuracies)) else ""
    bars.append(ax.bar(labels[i], elapsed_time[i], color=colors[i], hatch=hatch, width=0.7))
  for i, bar in enumerate(bars):
    rect = bar.patches[0]
    plt.text(rect.get_x() + rect.get_width() / 2.0, rect.get_height(),\
      "%.3f" % final_accuracies[i], ha='center', va='bottom')
  plt.xticks(fontsize=16)
  plt.yticks(fontsize=16)
  plt.ylim(0, max(elapsed_time) * 1.1)
  plt.title(title, fontsize=24, pad=20)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(output_file, bbox_inches="tight")
  print("Saved to %s" % output_file)

if __name__ == "__main__":
  main()

