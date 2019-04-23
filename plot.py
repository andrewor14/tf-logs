#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt

import parse_step_times

import math
import os
import re
import sys

# Plot one experiment
def plot_experiment(ax, label):
  step_times = {} # num workers -> step times
  for log_dir in os.listdir(label):
    num_workers = int(re.match("mpi-horovod_(\d+)workers", log_dir).groups()[0])
    if num_workers not in step_times:
      step_times[num_workers] = []
    log_dir = os.path.join(label, log_dir)
    step_time = parse_step_times.get_average_step_time(log_dir)
    step_times[num_workers].append(step_time)
  # Flatten data: average by key + include min and max
  for k, v in step_times.items():
    step_times[k] = (sum(v) / len(v), min(v), max(v))
  # Sort and separate
  step_times = step_times.items()
  step_times.sort()
  x_data, y_data, y_lower, y_upper = [], [], [], []
  for (x, (y, y_min, y_max)) in step_times:
    x_data.append(x)
    y_data.append(y)
    y_lower.append(y - y_min)
    y_upper.append(y_max - y)
  ax.set_xticks(x_data)
  ax.errorbar(x_data, y_data, yerr=[y_lower, y_upper], fmt="-x", label=label)

# Plot it
def make_plot(label):
  out_file = "%s-step-times.pdf" % label
  fig = plt.figure()
  ax = fig.add_subplot(1, 1, 1)
  ax.set_xlabel("num workers")
  ax.set_ylabel("average step time (s)")
  ax.set_title("horovod step time with increasing number of workers")
  plot_experiment(ax, label)
  legend = ax.legend(loc="best")
  fig.savefig(out_file, bbox_extra_artists=(legend,))
  print("Wrote to %s." % out_file)

def main():
  args = sys.argv
  labels = []
  if len(args) > 1:
    labels = args[1:]
  else:
    labels = ["cifar10-trivial", "synthetic-andrew-trivial"]
  for label in labels:
    make_plot(label)

if __name__ == "__main__":
  main()

