#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt

import math
import sys

# Set label
args = sys.argv
labels = []
if len(args) > 1:
  labels = args[1:]
else:
  labels = ["cifar10-trivial", "synthetic-resnet50", "cifar10-resnet56"]

# Plot one experiment
def plot_experiment(ax, file_name, label):
  data = {}
  with open(file_name) as f:
    for l in f.readlines():
      split = l.split(" ")
      assert len(split) == 2
      x = int(split[0])
      y = float(split[1])
      if x not in data:
        data[x] = []
      data[x].append(y)
  # Flatten data: average by key + include min and max
  for k, v in data.items():
    data[k] = (sum(v) / len(v), min(v), max(v))
  # Sort and separate
  data = data.items()
  data.sort()
  x_data, y_data, y_lower, y_upper = [], [], [], []
  for (x, (y, y_min, y_max)) in data:
    x_data.append(x)
    y_data.append(y)
    y_lower.append(y - y_min)
    y_upper.append(y_max - y)
  if label == "cifar10-trivial":
    ax.set_xscale("log")
    ax.set_xticks(x_data)
  else:
    ## Drop some ticks to avoid overlapping
    xtick_start_index = int(math.log(max(y_data), 2)) - 3 # kind of arbitrary
    ax.set_xticks([1] + x_data[xtick_start_index:])
  ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
  ax.errorbar(x_data, y_data, yerr=[y_lower, y_upper], fmt="-x", label=label)

# Plot it
def make_plot(label):
  in_file = "%s-data.txt" % label
  out_file = "%s-throughput.pdf" % label
  fig = plt.figure()
  ax = fig.add_subplot(1, 1, 1)
  ax.set_xlabel("batch size per device")
  ax.set_ylabel("throughput (images/sec)")
  ax.set_title("1 ps + 2 workers (1 K40 GPU each) on a single node")
  plot_experiment(ax, in_file, label)
  legend = ax.legend(loc="best")
  fig.savefig(out_file, bbox_extra_artists=(legend,))
  print("Wrote to %s." % out_file)

if __name__ == "__main__":
  for label in labels:
    make_plot(label)

