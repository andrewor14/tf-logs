#!/usr/bin/env python3

import datetime
import os
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np


def parse(data_file):
  """
  Parse memory usage over time from `data_file`, a path to a space separated file
  with four fields: (timestamp, [Allocate|Deallocate], num_bytes, allocation_id).
  Timestamp is expected to be in the format (hour:minute:seconds), e.g.
  15:13:03.741560.

  Return two lists: (time elapsed in seconds, memory usage in bytes).
  """
  first_timestamp = None
  time_elapsed = []
  memory_used = []
  max_cumulative_memory = -1
  max_cumulative_memory_timestamp = None
  with open(data_file) as f:
    for line in f.readlines():
      split = tuple(line.split(" "))
      raw_timestamp = split[0]
      allocate_or_deallocate = split[1]
      num_bytes = split[2]
      # Parse timestamp
      timestamp = datetime.datetime.strptime(raw_timestamp, "%H:%M:%S.%f")
      if first_timestamp is None:
        first_timestamp = timestamp
      time_elapsed.append((timestamp - first_timestamp).total_seconds())
      # Parse new memory usage
      current_memory = memory_used[-1] if len(memory_used) > 0 else 0
      delta_bytes = int(num_bytes)
      allocate_or_deallocate = allocate_or_deallocate.lower()
      if allocate_or_deallocate == "deallocate":
        delta_bytes *= -1
      elif allocate_or_deallocate != "allocate":
        raise ValueError("Malformed line: %s" % line)
      memory_used.append(current_memory + delta_bytes)
      # Save max cumulative memory and the corresponding timestamp
      if memory_used[-1] > max_cumulative_memory:
        max_cumulative_memory = memory_used[-1]
        max_cumulative_memory_timestamp = raw_timestamp
  print("Max memory timestamp: %s" % max_cumulative_memory_timestamp)
  return time_elapsed, memory_used

def do_plot(data_file, zoom_start=None, zoom_end = None):
  out_file = "output/%s.pdf" % os.path.basename(os.path.splitext(data_file)[0])
  fig = plt.figure()
  plt.xticks(fontsize=20)
  plt.yticks(fontsize=20)
  ax1 = fig.add_subplot(1, 1, 1)
  ax1.set_xlabel("Time elapsed (s)", fontsize=24, labelpad=15)
  ax1.set_ylabel("Num bytes in memory", fontsize=24, labelpad=15)
  time_elapsed, memory_used = parse(data_file)
  # Optionally zoom
  if zoom_start is not None and zoom_end is not None:
    start_index = np.where(np.array(time_elapsed) > zoom_start)[0][0]
    end_index = np.where(np.array(time_elapsed) < zoom_end)[0][-1]
    time_elapsed = time_elapsed[start_index:end_index]
    memory_used = memory_used[start_index:end_index]
  # Draw memory line
  ax1.errorbar(time_elapsed, memory_used, fmt="-")
  # Draw vertical line at the max
  plt.axvline(x=time_elapsed[np.argmax(memory_used)], linestyle="--", color="r")
  plt.xticks(fontsize=20)
  plt.yticks(fontsize=20)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(out_file, bbox_inches="tight")
  print("Wrote to %s." % out_file)

def main():
  args = sys.argv
  if len(args) != 2 and len(args) != 4:
    print("Usage: plot_alloc.py [data.txt] <[zoom start] [zoom end]>")
    sys.exit(1)
  zoom_start = float(args[2]) if len(args) == 4 else None
  zoom_end = float(args[3]) if len(args) == 4 else None
  do_plot(args[1], zoom_start, zoom_end)

if __name__ == "__main__":
  main()

