#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt

import math
import os
import re
import sys

import parse


# Plot one experiment identified by the given name
def plot_experiment(ax, experiment_name, mode):
  averages = {} # num workers -> averages
  experiment_dir = "data/%s" % experiment_name
  for log_dir in os.listdir(experiment_dir):
    #num_workers = int(re.match(".*horovod.*_(\d+)workers", log_dir).groups()[0])
    num_workers = int(re.match(".*checkpoint-restart-(\d+)-*", log_dir).groups()[0])
    if num_workers < 2 or num_workers > 45:
      continue
    if num_workers not in averages:
      averages[num_workers] = []
    log_dir = os.path.join(experiment_dir, log_dir)
    (average, variance) = parse_average_and_variance(experiment_name, mode, log_dir)
    averages[num_workers].append(average)
  (avg_x_data, avg_y_data, avg_y_min, avg_y_max) = extract_plot_data(averages)
  perfect_scaling = [min(avg_y_data)] * len(avg_x_data)
  ax.errorbar(avg_x_data, avg_y_data, fmt="-x", linewidth=2, label="actual")
  ax.errorbar(avg_x_data, perfect_scaling, fmt="--", linewidth=2, label="perfect scaling")

# Parse the average and variance of the metric specified by mode
# Return a 2-tuple of (average, variance)
def parse_average_and_variance(experiment_name, mode, log_dir):
  if mode == "step":
    return parse.get_step_time_average_and_variance(log_dir)
  elif mode == "communication":
    tag = "Const" if "fake-allreduce" in experiment_name else ""
    return parse.get_allreduce_time_average_and_variance(log_dir, tag)
  else:
    raise ValueError("Error: mode must be either 'step' or 'communication' (was '%s')" % mode)

# Return x, y, y_min and y_max for the specified data, which has the format {key -> [list of values]}
def extract_plot_data(data):
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
  return (x_data, y_data, y_lower, y_upper)

# Actually plot it
def do_plot(experiment_name, mode):
  out_file = "output/%s-%s-times.pdf" % (experiment_name, mode)
  fig = plt.figure()
  plt.xticks(fontsize=20)
  plt.yticks(fontsize=20)
  ax = fig.add_subplot(1, 1, 1)
  axes = plt.gca()
  axes.set_ylim([0.002,0.026])
  ax.set_xlabel("Num workers", fontsize=24, labelpad=15)
  ax.set_ylabel("Average communication time (s)", fontsize=24, labelpad=15)
  plot_experiment(ax, experiment_name, mode)
  ax.legend(loc="best", prop={'size': 24})
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(out_file, bbox_inches='tight')
  print("Wrote to %s." % out_file)

def main():
  args = sys.argv
  if len(args) != 3:
    print("Usage: plot.py [mode] [experiment_name] (where mode = 'step', 'communication', or 'all')")
    sys.exit(1)
  mode = args[1]
  experiment_name = args[2]
  if mode == "all":
    do_plot(experiment_name, "step")
    do_plot(experiment_name, "communication")
  else:
    do_plot(experiment_name, mode)

if __name__ == "__main__":
  main()

