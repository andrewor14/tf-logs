#!/usr/bin/env python3

import datetime
import os
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from find_alloc import parse_timestamp, prettify_bytes
from unreleased_allocations import get_allocations_by_category, ALLOCATION_TIMESTAMPS

def print_peak_breakdown(time_elapsed, allocations_by_category):
  peak_index = None
  peak_memory = None
  # Find peak memory
  for i in range(len(time_elapsed)):
    memory_used = sum([allocs[i] for _, allocs in allocations_by_category.items()])
    if peak_memory is None or memory_used > peak_memory:
      peak_index = i
      peak_memory = memory_used
  if peak_index is None or peak_memory is None:
    raise ValueError("No peak memory found?")
  # Print breakdown
  print("----------------------------------------------------")
  print("Peak memory at %.3fs: %s" %\
    (time_elapsed[peak_index], prettify_bytes(peak_memory)))
  for category in allocations_by_category.keys():
    num_bytes = prettify_bytes(allocations_by_category[category][peak_index])
    print("  %s: %s" % (category, num_bytes))
  print("----------------------------------------------------")

def do_plot(log_file, zoom_start=None, zoom_end=None):
  out_file = "output/%s.pdf" % os.path.basename(os.path.splitext(log_file)[0])
  fig = plt.figure()
  ax1 = fig.add_subplot(1, 1, 1)
  ax1.set_xlabel("Time elapsed (s)", fontsize=24, labelpad=15)
  ax1.set_ylabel("Num bytes in memory", fontsize=24, labelpad=15)
  allocations_by_category = get_allocations_by_category(log_file)
  # Convert timestamps to time elapsed
  timestamps = allocations_by_category[ALLOCATION_TIMESTAMPS]
  first_timestamp = parse_timestamp(timestamps[0])
  time_elapsed = [(parse_timestamp(t) - first_timestamp).total_seconds()\
      for t in timestamps]
  del allocations_by_category[ALLOCATION_TIMESTAMPS]
  # Plot all lines
  all_categories = allocations_by_category.keys()
  all_allocations = [allocations_by_category[c] for c in all_categories]
  ax1.stackplot(time_elapsed, *all_allocations, labels=all_categories)
  ax1.legend(all_categories, loc='upper left')
  print_peak_breakdown(time_elapsed, allocations_by_category)
  plt.xticks(fontsize=20)
  plt.yticks(fontsize=20)
  # Optionally zoom
  if zoom_start is not None and zoom_end is not None:
    plt.xlim(zoom_start, zoom_end)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(out_file, bbox_inches="tight")
  print("Wrote to %s." % out_file)

def main():
  args = sys.argv
  if len(args) != 2 and len(args) != 4:
    print("Usage: plot_alloc_breakdown.py [log_file] <[zoom start] [zoom end]>")
    sys.exit(1)
  zoom_start = float(args[2]) if len(args) == 4 else None
  zoom_end = float(args[3]) if len(args) == 4 else None
  do_plot(args[1], zoom_start, zoom_end)

if __name__ == "__main__":
  main()

