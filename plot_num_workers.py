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
  for experiment_name in experiment_names:
    if mode not in experiment_name:
      continue
    experiment_name = experiment_name.lstrip("data/").rstrip("/")
    log_file = "data/%s/1/rank.0/stderr" % experiment_name
    # Parse
    print("Parsing start times from %s" % log_file)
    x, y = [], []
    for (num_workers, start_time) in parse.parse_file(log_file, value_to_parse="start_times"):
      x.append(start_time[0])
      y.append(num_workers)
    # Add a point at the end to show when the experiment ended
    # Note: we expect the caller to fix the x range!
    print("Parsing total time from %s" % log_file)
    total_time = parse.parse_file(log_file, value_to_parse="total_time")[0][1][0]
    x.append(total_time)
    y.append(y[-1])
    # Plot
    label = experiment_name.split("-")[3]
    ax.errorbar(x, y, fmt="-x", linewidth=4, markeredgewidth=4, markersize=15, label=label)

# Actually plot it
def do_plot(experiment_names):
  if "cifar10" in experiment_names[0]:
    out_file = "output/cifar10_num_workers.pdf"
  elif "imagenet" in experiment_names[0]:
    out_file = "output/imagenet_num_workers.pdf"
  else:
    out_file = "output/num_workers.pdf"
  fig = plt.figure()
  ax = fig.add_subplot(1, 1, 1)
  plt.xticks(fontsize=20)
  plt.yticks(fontsize=20)
  ax.set_xlabel("Time elapsed (s)", fontsize=24, labelpad=15)
  ax.set_ylabel("Number of workers", fontsize=24, labelpad=15)
  really_do_plot(ax, experiment_names, "autoscaling")
  plt.xlim(xmin=1, xmax=120)
  ax.legend(fontsize=24, loc="best")
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(out_file, bbox_inches="tight")
  print("Wrote to %s." % out_file)

def main():
  args = sys.argv
  if len(args) < 2:
    print("Usage: plot_num_workers.py [experiment_name1] <[experiment_name2] ...>")
    print("  (e.g. ./plot_num_workers.py data/cifar10*")
    sys.exit(1)
  experiment_names = [x for x in args[1:] if "tgz" not in x]
  do_plot(experiment_names)

if __name__ == "__main__":
  main()

