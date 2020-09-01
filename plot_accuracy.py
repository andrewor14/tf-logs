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

  # Allow the user to plot other dimensions/units
  steps_per_epoch = int(os.getenv("STEPS_PER_EPOCH", -1))
  xlabel = "Step" if steps_per_epoch > 0 else "Epoch"
  xlabel = os.getenv("XLABEL", xlabel)
  ylabel = os.getenv("YLABEL", "Validation accuracy")

  # Plot it
  fig = plt.figure()
  ax = fig.add_subplot(1, 1, 1)
  ax.set_xlabel(xlabel, fontsize=24, labelpad=15)
  ax.set_ylabel(ylabel, fontsize=24, labelpad=15)
  for data_file in data_files:
    epochs = []
    validation_accuracies = []
    label = data_file.replace(data_file_prefix, "").replace("-time", "").replace(".txt", "")
    with open(data_file) as f:
      for i, line in enumerate(f.readlines()):
        if smooth_factor > 0 && i % smooth_factor == 0:
          continue
        split = line.strip().split(" ")
        if len(split) != 2:
          raise ValueError("Expected two columns in data file: %s" % data_file)
        epochs.append(int(split[0]))
        validation_accuracies.append(float(split[1]))
    x = [steps_per_epoch * e for e in epochs] if steps_per_epoch > 0 else epochs
    y = validation_accuracies
    ax.plot(x, y, label=label, marker="x", linewidth=3, markeredgewidth=3)
  ax.legend(fontsize=12)
  plt.xticks(fontsize=16)
  plt.yticks(fontsize=16)
  plt.title(title, fontsize=24, pad=20)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(output_file, bbox_inches="tight")

if __name__ == "__main__":
  main()

