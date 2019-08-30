#!/usr/bin/env python

import os
import re
import sys
import glob

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import parse


GLOBAL_BATCH_SIZE = 8192

# Plot one experiment identified by the given name
def plot_experiment(ax, experiment_name, zoom_worker_minimum=None, zoom_worker_maximum=None):
  data = {}
  for log_file in glob.glob("data/%s/*-0.out" % experiment_name):
    match = re.match(".*batch_size_micro_(\d+)-.*", log_file)
    if match is None:
      continue
    local_batch_size = int(match.groups()[0])
    step_times = parse.parse_step_times(log_file)
    if len(step_times) == 0:
      print("Warning: no data points for %s. Skipping." % log_file)
      continue
    # Expected computation time is computed by drawing G/l samples from the step time distribution
    # derived from a single node, where G = global batch size and l = local batch size
    mean = np.mean(step_times)
    stddev = np.std(step_times)
    if stddev == 0.0:
      print("Warning: not enough data points for %s. Skipping." % log_file)
      continue
    num_workers = GLOBAL_BATCH_SIZE / local_batch_size
    expected_computation_time = max([np.random.normal(mean, stddev) for i in range(num_workers)])
    if num_workers in data:
      raise ValueError("Two log files map to the same local batch size?")
    data[num_workers] = expected_computation_time
  x = sorted(data.keys())
  y = [data[i] for i in x]
  perfect_scaling = [y[0] * x[0] / i for i in x]
  # Maybe zoom
  if zoom_worker_minimum is not None:
    zoom_worker_maximum = zoom_worker_maximum or 2**32
    start_index = np.where(np.array(x) >= zoom_worker_minimum)[0][0]
    end_index = np.where(np.array(x) <= zoom_worker_maximum)[0][-1] + 1
    x = x[start_index:end_index]
    y = y[start_index:end_index]
    perfect_scaling = perfect_scaling[start_index:end_index]
  ax.set_xticks(x)
  ax.errorbar(x, y, fmt="-x", linewidth=2, label="actual")
  ax.errorbar(x, perfect_scaling, fmt="--", linewidth=2, label="perfect scaling")

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
def do_plot(experiment_name, zoom_worker_minimum=None, zoom_worker_maximum=None):
  out_file = "output/%s.pdf" % experiment_name
  fig = plt.figure()
  plt.xticks(fontsize=15)
  plt.yticks(fontsize=15)
  ax = fig.add_subplot(1, 1, 1)
  ax.set_xlabel("Num workers", fontsize=20, labelpad=15)
  ax.set_xscale("log")
  ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
  ax.set_ylabel("Expected computation time (s)", fontsize=20, labelpad=20)
  plot_experiment(ax, experiment_name, zoom_worker_minimum, zoom_worker_maximum)
  ax.legend(prop={'size': 20})
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(out_file)
  print("Wrote to %s." % out_file)

def main():
  args = sys.argv
  if len(args) < 2 or len(args) > 4:
    print("Usage: plot.py [experiment_name] <[zoom_worker_minimum] [zoom_worker_maximum]>")
    sys.exit(1)
  experiment_name = args[1]
  zoom_worker_minimum = None
  zoom_worker_maximum = None
  if len(args) > 2:
    zoom_worker_minimum = int(args[2])
    if len(args) > 3:
      zoom_worker_maximum = int(args[3])
  do_plot(experiment_name, zoom_worker_minimum, zoom_worker_maximum)

if __name__ == "__main__":
  main()

