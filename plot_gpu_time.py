#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import math
import json
import os
import re
import sys

import parse

MAX_NUM_WORKERS = 50

# Plot one experiment identified by the given name
def really_do_plot(ax, experiment_names, mode):
  gpu_times = {} # num starting workers => gpu time
  for experiment_name in experiment_names:
    if mode not in experiment_name:
      continue
    experiment_name = experiment_name.lstrip("data/").rstrip("/")
    log_file = "data/%s/1/rank.0/stderr" % experiment_name
    if not os.path.isfile(log_file):
      log_file = "data/%s/1/rank.00/stderr" % experiment_name
    # Parse
    print("Parsing start times from %s" % log_file)
    start_times = parse.parse_file(log_file, value_to_parse="start_times")
    # Add a point at the end to show when the experiment ended
    print("Parsing total time from %s" % log_file)
    total_time = parse.parse_file(log_file, value_to_parse="total_time")[0][1][0]
    start_times.append((start_times[-1][0], [total_time]))
    gpu_time = 0
    for i in range(1, len(start_times)):
      prev_num_workers, prev_start_time = start_times[i-1]
      this_num_workers, this_start_time = start_times[i]
      if len(prev_start_time) < 1 or len(this_start_time) < 1:
        raise ValueError("Wrong length: %s, %s" % (prev_start_time, this_start_time))
      gpu_time += (this_start_time[-1] - prev_start_time[-1]) * prev_num_workers
    split = experiment_name.split("-")
    num_starting_workers = int(split[3])
    gpu_times[num_starting_workers] = gpu_time
  # Plot
  fmt = "-x" if mode == "autoscaling" else "-o"
  markeredgewidth = 4 if mode == "autoscaling" else 0
  num_starting_workers = list(gpu_times.keys())
  num_starting_workers.sort()
  gpu_times_sorted = [gpu_times[w] for w in num_starting_workers]
  ax.errorbar(num_starting_workers, gpu_times_sorted,\
    fmt=fmt, linewidth=4, markeredgewidth=markeredgewidth, markersize=20, label=mode)
  if mode == "static":
    ax.set_xticks(num_starting_workers)
    ax.margins(0.1)

# Actually plot it
def do_plot(experiment_names):
  if "cifar10" in experiment_names[0]:
    out_file = "output/cifar10_gpu_time.pdf"
  elif "imagenet" in experiment_names[0]:
    out_file = "output/imagenet_gpu_time.pdf"
  else:
    out_file = "output/gpu_time.pdf"
  fig = plt.figure()
  ax = fig.add_subplot(1, 1, 1)
  plt.xticks(fontsize=20)
  plt.yticks(fontsize=20)
  ax.set_xlabel("Starting number of workers", fontsize=24, labelpad=15)
  ax.set_ylabel("GPU time (s)", fontsize=24, labelpad=15)
  really_do_plot(ax, experiment_names, "static")
  really_do_plot(ax, experiment_names, "autoscaling")
  #plt.xlim(xmin=1)
  ax.legend(fontsize=24, loc="best")
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(out_file, bbox_inches="tight")
  print("Wrote to %s." % out_file)

def main():
  args = sys.argv
  if len(args) < 2:
    print("Usage: plot_gpu_time.py [experiment_name1] <[experiment_name2] ...>")
    print("  (e.g. ./plot_gpu_time.py data/cifar10*")
    sys.exit(1)
  experiment_names = [x for x in args[1:] if "tgz" not in x]
  do_plot(experiment_names)

if __name__ == "__main__":
  main()

