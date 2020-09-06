#!/usr/bin/env python3

import os
import sys

import matplotlib.pyplot as plt

def main():
  args = sys.argv
  if len(args) == 1:
    print("Usage: ./plot_accuracy.py [data1.txt] [data2.txt] [data3.txt] ...")
    print("  Each data file contains two columns: epoch and validation accuracy")
    sys.exit(1)
  data_files = args[1:]
  smooth_factor = int(os.getenv("SMOOTH_FACTOR", -1))
  title = os.getenv("TITLE", "ResNet-50 on ImageNet")
  output_file = os.getenv("OUTPUT_FILE", "output/resnet_accuracy.pdf")
  data_file_prefix = os.getenv("DATA_FILE_PREFIX", "resnet-imagenet-")
  data_file_suffix = os.getenv("DATA_FILE_SUFFIX", ".txt")

  # Allow the user to plot other dimensions/units
  steps_per_epoch = int(os.getenv("STEPS_PER_EPOCH", -1))
  xlabel = "Step" if steps_per_epoch > 0 else "Epoch"
  xlabel = os.getenv("XLABEL", xlabel)
  ylabel = os.getenv("YLABEL", "Validation accuracy")
  space_xticks_apart = os.getenv("SPACE_XTICKS_APART", "").lower() == "true"
  put_legend_outside = os.getenv("PUT_LEGEND_OUTSIDE", "").lower() == "true"
  bold_baseline = os.getenv("BOLD_BASELINE", "").lower() == "true"

  # Plot it
  fig = plt.figure()
  ax = fig.add_subplot(1, 1, 1)
  ax.set_xlabel(xlabel, fontsize=24, labelpad=15)
  ax.set_ylabel(ylabel, fontsize=24, labelpad=15)
  for data_file in data_files:
    epochs = []
    validation_accuracies = []
    label = data_file.replace(data_file_prefix, "").replace(data_file_suffix, "")
    with open(data_file) as f:
      for i, line in enumerate(f.readlines()):
        if smooth_factor > 0 and i % smooth_factor == 0:
          continue
        split = line.strip().split(" ")
        if len(split) != 2:
          raise ValueError("Expected two columns in data file: %s" % data_file)
        epochs.append(int(split[0]))
        validation_accuracies.append(float(split[1]))
    if steps_per_epoch > 0:
      # The baseline may have more steps per epoch because the batch sizes are smaller
      baseline_steps_multiplier = int(os.getenv("BASELINE_STEPS_MULTIPLIER", 1))\
        if "baseline" in data_file else 1
      x = [steps_per_epoch * baseline_steps_multiplier * e for e in epochs]
    else:
      x = epochs
    y = validation_accuracies
    # Style the lines
    baseline_linestyle = "-" if bold_baseline else "--"
    baseline_linewidth = 6 if bold_baseline else 2
    virtual_linestyle = "--" if bold_baseline else "-"
    virtual_linewidth = 2 if bold_baseline else 3
    virtual_marker = "" if bold_baseline else "x"
    if "baseline" in data_file:
      ax.plot(x, y, label=label, linestyle=baseline_linestyle, linewidth=baseline_linewidth)
    else:
      ax.plot(x, y, label=label, linestyle=virtual_linestyle, linewidth=virtual_linewidth,\
        marker=virtual_marker, markeredgewidth=3)

  # Legend
  def sort_key(tup):
    label = tup[0]
    return int(label.split("bs_")[0]) * (1 if "baseline" in label else 100)
  def format_label(label):
    return label.replace("_baseline", " (baseline)")
  handles, labels = ax.get_legend_handles_labels()
  labels, handles = zip(*sorted(zip(labels, handles), key=sort_key))
  labels = [format_label(l) for l in labels]
  if put_legend_outside:
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(handles, labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=12)
  else:
    ax.legend(handles, labels, fontsize=12)

  if space_xticks_apart:
    ax.set_xticks([max(xx, 0) for xx in ax.get_xticks()[::2]])
  plt.xticks(fontsize=16)
  plt.yticks(fontsize=16)
  plt.title(title, fontsize=24, pad=20)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(output_file, bbox_inches="tight")
  print("Saved to %s" % output_file)

if __name__ == "__main__":
  main()

