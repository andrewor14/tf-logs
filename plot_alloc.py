#!/usr/bin/env python3

import datetime
import os
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from find_alloc import parse_memory_over_time_elapsed, parse_markers


def do_plot(data_file, zoom_start=None, zoom_end=None):
  out_file = "output/%s.pdf" % os.path.basename(os.path.splitext(data_file)[0])
  fig = plt.figure()
  plt.xticks(fontsize=20)
  plt.yticks(fontsize=20)
  ax1 = fig.add_subplot(1, 1, 1)
  ax1.set_xlabel("Time elapsed (s)", fontsize=24, labelpad=15)
  ax1.set_ylabel("Num bytes in memory", fontsize=24, labelpad=15)
  time_elapsed, memory_used = parse_memory_over_time_elapsed(data_file)
  marker_times = parse_markers(data_file)
  # Draw memory line
  ax1.errorbar(time_elapsed, memory_used, fmt="-")
  # Draw vertical lines at both the max and where the markers are
  plt.axvline(x=time_elapsed[np.argmax(memory_used)], linestyle="--", color="r")
  for t in marker_times:
    plt.axvline(x=t, linestyle="--", color="b")
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
    print("Usage: plot_alloc.py [data.txt] <[zoom start] [zoom end]>")
    sys.exit(1)
  zoom_start = float(args[2]) if len(args) == 4 else None
  zoom_end = float(args[3]) if len(args) == 4 else None
  do_plot(args[1], zoom_start, zoom_end)

if __name__ == "__main__":
  main()

