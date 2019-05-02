#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import sys

# ==========================================================
# This expects an input data file with the following format
#
#   timestamp rx_bytes tx_bytes
#   1556302951638 144060846523 143809860001
#   1556302951645 144060846523 143809860001
#   1556302951651 144060846577 143809860001
#   1556302951658 144060846577 143809860001
#
# where rx_bytes and tx_bytes are computed using 'ethtool'
# and thus are cumulative (i.e. monotonically increasing).
# ==========================================================

def make_plot(data_file, min_x, max_x):
  out_file = "output/%s.pdf" % data_file.replace(".txt", "")
  fig = plt.figure()
  ax = fig.add_subplot(1, 1, 1)
  ax.set_xlabel("time elapsed (ms)")
  ax.set_ylabel("bytes")
  ax.set_title(data_file, y=1.08)
  # Parse raw data
  x_data, rx_data, tx_data = [], [], []
  with open(data_file) as f:
    for line in f.readlines()[1:]: # skip header
      split = line.split()
      (ts, rx, tx) = (int(split[0]), int(split[1]), int(split[2]))
      x_data.append(ts)
      rx_data.append(rx)
      tx_data.append(tx)
  # Try deleting unique values?
  unique_indices = []
  last_rx = None
  for i in range(len(rx_data)):
    if rx_data[i] != last_rx:
      unique_indices.append(i)
    last_rx = rx_data[i]
  x_data = np.array(x_data)[unique_indices].tolist()
  rx_data = np.array(rx_data)[unique_indices].tolist()
  tx_data = np.array(tx_data)[unique_indices].tolist()
  # Subtract all timestamps by the first one
  # Network stats are cumulative counters, so turn them into deltas
  x_data = np.array(x_data)
  x_data = (x_data - x_data[0]).tolist()
  rx_data = [0] + np.diff(rx_data).tolist()
  tx_data = [0] + np.diff(tx_data).tolist()
  # Optionally zoom in
  if min_x is not None and max_x is not None:
    x_data = np.array(x_data)
    zoom_indices = np.where((x_data >= min_x) & (x_data < max_x))
    x_data = np.array(x_data)[zoom_indices].tolist()
    rx_data = np.array(rx_data)[zoom_indices].tolist()
    tx_data = np.array(tx_data)[zoom_indices].tolist()
  # Plot
  ax.plot(x_data, rx_data, "-x", label="rx_bytes")
  ax.plot(x_data, tx_data, "-x", label="tx_bytes")
  ax.legend()
  plt.tight_layout()
  fig.savefig(out_file)
  print("Wrote to %s." % out_file)

def main():
  args = sys.argv
  if not (len(args) == 2 or len(args) == 4):
    print("Usage: plot_network.py [data_file] <[min] [max]>")
    sys.exit(1)
  min_x, max_x = None, None
  if len(args) == 4:
    min_x = int(args[2])
    max_x = int(args[3])
  make_plot(args[1], min_x, max_x)

if __name__ == "__main__":
  main()

