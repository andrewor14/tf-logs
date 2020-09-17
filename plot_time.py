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
  group_bars = os.getenv("GROUP_BARS", "").lower() == "true"
  plot_throughput = os.getenv("PLOT_THROUGHPUT", "").lower() == "true"
  space_yticks_apart = os.getenv("SPACE_YTICKS_APART", "").lower() == "true"
  legend_ncol = int(os.getenv("LEGEND_NCOL", "1"))
  ylim_factor = float(os.getenv("YLIM_FACTOR", 1.05))

  # Sort the labels
  def sort_key(label):
    label = label.replace(data_file_prefix, "")
    m = re.match("([0-9]+)bs_([0-9]+)gpu.*", label)
    if m is not None:
      batch_size, num_gpus = m.groups()
      return (int(num_gpus) * 100000 + int(batch_size)) + (0 if "baseline" in label else 1)
    else:
      batch_size = int(re.match("([0-9]+)bs.*", label).groups()[0])
      num_gpus = 1
      return int(batch_size) + (0 if "baseline" in label else 1)

  data_files.sort(key=sort_key)

  def get_label(data_file):
    label = data_file.replace(data_file_prefix, "").replace(data_file_suffix, "")
    m = re.match("([0-9]+)bs_([0-9]+)gpu_([0-9]+)vn.*", label)
    if m is not None:
      batch_size, num_gpus, num_vns = re.match("([0-9]+)bs_([0-9]+)gpu_([0-9]+)vn.*", label).groups()
      num_gpus = "%s GPU%s" % (num_gpus, "s" if int(num_gpus) > 1 else "")
      batch_size = "%sbs" % batch_size
      num_vns = "%sVN" % num_vns if int(num_vns) > 1 else "(TF)"
      return "%s\n%s\n%s" % (num_gpus, batch_size, num_vns)
    else:
      batch_size, num_vns = re.match("([0-9]+)bs_([0-9]+)vn.*", label).groups()
      batch_size = "%sbs" % batch_size
      num_vns = "%sVN" % num_vns if int(num_vns) > 1 else "(TF)"
      return "%s\n%s" % (batch_size, num_vns)

  # Optionally resize figure
  if figure_size is not None:
    width = float(figure_size.split(",")[0])
    height = float(figure_size.split(",")[1])
    fig = plt.figure(figsize=(width, height))
  else:
    fig = plt.figure()

  # Y-axis can be either completion time or throughput
  if plot_throughput:
    ylabel = "Throughput\n(examples/s)"
  else:
    ylabel = "Completion time (%s)" % time_unit

  ax = fig.add_subplot(1, 1, 1)
  ax.set_xlabel("Configuration", fontsize=24, labelpad=15)
  ax.set_ylabel(ylabel, fontsize=24, labelpad=15)
  labels = []
  colors = []
  values = []
  final_accuracies = []
  for data_file in data_files:
    labels.append(get_label(data_file))
    with open(data_file) as f:
      split = f.readlines()[-1].strip().split(" ")
      value = float(split[0])
      if time_unit == "s" or plot_throughput:
        values.append(value)
      else:
        values.append(value / 60)
      final_accuracies.append(float(split[1]))
      colors.append("paleturquoise" if "baseline" in data_file else "lightsalmon")

  # Plot the bars
  bars = []
  bar_width = 0.35 if group_bars else 0.7
  y_values = values
  for i in range(len(labels)):
    if group_bars:
      r1 = np.arange(int(len(labels)/2))
      r2 = [x + bar_width for x in r1]
      if i == 8:
        x_value = 4
      else:
        x_value = r1[int(i/2)] if "baseline" in data_files[i] else r2[int(i/2)]
      label = "baseline" if "baseline" in data_files[i] else "virtual node"
    else:
      x_value = labels[i]
      label = None
    hatch = "/" if hatch_max_accuracy and i == int(np.argmax(final_accuracies)) else ""
    bars.append(ax.bar(x_value, y_values[i], color=colors[i], hatch=hatch,\
      width=bar_width, label=label, edgecolor="white"))

  # Add final accuracy on top of each bar
  for i, bar in enumerate(bars):
    rect = bar.patches[0]
    text = "%.2f" % final_accuracies[i]
    if i == 0:
      text = "Acc\n%s" % text
    plt.text(rect.get_x() + rect.get_width() / 2.0, 0,\
      text, ha='center', va='bottom', fontsize=12)

  # If we grouped the bars, just display num GPUs and add a legend
  if group_bars:
    positions = [r.patches[0].get_x() for i, r in enumerate(bars)\
      if "baseline" not in data_files[i]]
    if len(labels) % 2 == 1:
      positions[-1] += bar_width / 2
    merged_labels = []
    for i, df in enumerate(data_files):
      if "baseline" in df:
        continue
      merged_labels.append(labels[i].split("\n")[0])
    plt.xticks(positions, merged_labels, fontsize=16)
    ax.legend(["TF*", "VF"], fontsize=16, loc="upper left", ncol=legend_ncol)
  else:
    plt.xticks(fontsize=16)
    ax.legend(["TF", "VF"], fontsize=16, loc="upper left", ncol=legend_ncol)

  if space_yticks_apart:
    ax.set_yticks([max(yy, 0) for yy in ax.get_yticks()[::2]])
  plt.yticks(fontsize=16)
  plt.ylim(0, max(y_values) * ylim_factor)
  plt.title(title, fontsize=24, pad=20)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(output_file, bbox_inches="tight")
  print("Saved to %s" % output_file)

if __name__ == "__main__":
  main()

