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
def plot_experiment(ax, experiment_name):
  experiment_dir = "data/%s" % experiment_name
  # Parse
  throughput_name = "throughput"
  num_workers, throughputs = parse.parse_dir(experiment_dir, value_to_parse=throughput_name)
  num_workers = num_workers[:MAX_NUM_WORKERS]
  throughputs = throughputs[:MAX_NUM_WORKERS]
  # Labels
  split = experiment_name.split("-")
  multiplier = round(1 / float(split[1]), 2)
  replaced = "replaced" if "replace" in experiment_name else "straggler"
  label = "%sx %s" % (multiplier, replaced)
  fmt = None
  marker = None
  color = None
  linewidth = 4
  zorder = 1
  if "straggler-4" in experiment_name:
    color="c"
    marker="x"
  elif "straggler-2" in experiment_name:
    color="r"
    marker="o"
  elif "straggler-1.3" in experiment_name:
    color="b"
    marker="v"
  elif "straggler-1" in experiment_name:
    color="k"
    linewidth = 16
    label = "No stragglers"
    zorder = 0
  if "replace" in experiment_name or "straggler-1-" in experiment_name:
    fmt="-"
  else:
    fmt="--"
  if marker is not None:
    fmt = "%s%s" % (fmt, marker)
  markeredgewidth = 4 if marker == "x" else 0
  ax.errorbar(num_workers, throughputs, fmt=fmt, linewidth=linewidth, markeredgewidth=markeredgewidth,
    markersize=16, color=color, label=label, markevery=4, zorder=zorder)

# Plot one experiment identified by the given name
def plot_experiment2(ax, experiment_names):
  labels = {}
  for i, e in enumerate(experiment_names):
    e = e.lstrip("data/").rstrip("/")
    # Parse
    log_file = "data/%s/1/rank.0/stderr" % e
    print("Parsing total time from %s" % log_file)
    total_time = parse.parse_file(log_file, value_to_parse="total_time")[0][1][0]
    # Labels
    replace = "replace" in e
    multiplier = round(1 / float(e.split("-")[1]), 2)
    label = "%sx" % multiplier
    if label not in labels:
      labels[label] = (None, None)
    if replace:
      labels[label] = (labels[label][0], total_time)
    else:
      labels[label] = (total_time, labels[label][1])
  # Plot
  stragglers = []
  replaced = []
  labels_sorted = list(labels.keys())
  labels_sorted.sort()
  for l in labels_sorted:
    s, r = labels[l]
    if r is None:
      r = 0
    stragglers.append(s)
    replaced.append(r)
  width = 0.35
  print(stragglers, replaced)
  labels_range = np.arange(len(labels_sorted))
  ax.bar(labels_range - width/2, stragglers, width, label="Stragglers", color="mediumblue", edgecolor="none")
  ax.bar(labels_range + width/2, replaced, width, label="Replaced", color="orange", edgecolor="none")
  ax.set_xticks(labels_range)
  ax.set_xticklabels(labels_sorted)
  ax.legend()

# Actually plot it
def do_plot(experiment_names):
  out_file = "output/stragglers_eval.pdf"
  fig = plt.figure()
  ax = fig.add_subplot(1, 1, 1)
  plt.xticks(fontsize=20)
  plt.yticks(fontsize=20)
  ax.set_xlabel("Number of workers", fontsize=24, labelpad=15)
  ax.set_ylabel("Average throughput (img/s)", fontsize=24, labelpad=15)
  for i, e in enumerate(experiment_names):
    print(e)
    e = e.lstrip("data/").rstrip("/")
    plot_experiment(ax, e)
  plt.xlim(xmin=1)
  ax.legend(fontsize=24, loc="center", bbox_to_anchor=(1.35, 0.5))
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(out_file, bbox_inches="tight")
  print("Wrote to %s." % out_file)

def do_plot2(experiment_names):
  out_file = "output/stragglers_times_eval.pdf"
  fig = plt.figure()
  ax = fig.add_subplot(1, 1, 1)
  plt.xticks(fontsize=20)
  plt.yticks(fontsize=20)
  ax.set_xlabel("Slowdown", fontsize=24, labelpad=15)
  ax.set_ylabel("Completion time (s)", fontsize=24, labelpad=15)
  ax.yaxis.set_major_locator(plt.MaxNLocator(4))
  plot_experiment2(ax, experiment_names)
  ax.legend(fontsize=24, loc="best")
  fig.set_size_inches(8, 4)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(out_file, bbox_inches="tight")
  print("Wrote to %s." % out_file)

def main():
  args = sys.argv
  if len(args) < 2:
    print("Usage: plot_stragglers.py [experiment_name1] <[experiment_name2] ...>")
    print("  (e.g. ./plot_stragglers.py data/*straggler*)")
    sys.exit(1)
  experiment_names = [x for x in args[1:] if "tgz" not in x]
  do_plot(experiment_names)
  do_plot2(experiment_names)

if __name__ == "__main__":
  main()

