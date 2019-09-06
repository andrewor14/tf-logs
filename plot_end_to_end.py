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
  total_times = {} # num starting workers => total time
  for experiment_name in experiment_names:
    if mode not in experiment_name:
      continue
    experiment_name = experiment_name.lstrip("data/").rstrip("/")
    experiment_dir = "data/%s" % experiment_name
    # Parse
    print("Parsing total time from %s" % experiment_dir)
    parsed = parse.parse_dir(experiment_dir, value_to_parse="total_time")[1]
    total_time = None
    if len(parsed) == 1:
      total_time = float(parsed[0])
    else:
      print("Warning: total time not parsed from %s" % experiment_dir)
    split = experiment_name.split("-")
    num_starting_workers = int(split[3])
    total_times[num_starting_workers] = total_time
  print(total_times)
  # Plot
  num_starting_workers = list(total_times.keys())
  num_starting_workers.sort()
  total_times_sorted = [total_times[w] for w in num_starting_workers]
  ax.errorbar(num_starting_workers, total_times_sorted,\
    fmt="-x", linewidth=4, markeredgewidth=4, markersize=15, label=mode)

# Actually plot it
def do_plot(experiment_names):
  out_file = "output/end_to_end.pdf"
  fig = plt.figure()
  ax = fig.add_subplot(1, 1, 1)
  plt.xticks(fontsize=20)
  plt.yticks(fontsize=20)
  ax.set_xlabel("Starting number of workers", fontsize=24, labelpad=15)
  ax.set_ylabel("Time to complete 200 epochs (s)", fontsize=24, labelpad=15)
  really_do_plot(ax, experiment_names, "static")
  really_do_plot(ax, experiment_names, "autoscaling")
  plt.xlim(xmin=1)
  ax.legend(fontsize=24, loc="best")
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(out_file, bbox_inches="tight")
  print("Wrote to %s." % out_file)

def main():
  args = sys.argv
  if len(args) < 2:
    print("Usage: plot_end_to_end.py [experiment_name1] <[experiment_name2] ...>")
    sys.exit(1)
  experiment_names = [x for x in args[1:] if "tgz" not in x]
  do_plot(experiment_names)

if __name__ == "__main__":
  main()

