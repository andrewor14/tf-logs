#!/usr/bin/env python

import matplotlib
import matplotlib.pyplot as plt

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
  out_file = data_file.replace(".txt", "") + ".pdf"
  fig = plt.figure()
  ax = fig.add_subplot(1, 1, 1)
  ax.set_xlabel("time elapsed (ms)")
  ax.set_ylabel("bytes")
  ax.set_title(data_file, y=1.08)
  # Parse data
  with open(data_file) as f:
    x_data, rx_data, tx_data = [], [], []
    first_ts, previous_rx, previous_tx = None, None, None
    for line in f.readlines()[1:]: # skip header
      split = line.split()
      (ts, rx, tx) = (int(split[0]), int(split[1]), int(split[2]))
      first_ts = first_ts or ts
      previous_rx = previous_rx or rx
      previous_tx = previous_tx or tx
      # Subtract all timestamps by the first one
      x_data.append(ts - first_ts)
      # Network stats are cumulative counters, so turn them into deltas
      rx_data.append(rx - previous_rx)
      tx_data.append(tx - previous_tx)
      previous_rx = rx
      previous_tx = tx
  # Filter out some data based on min_x and max_x
  if min_x is not None and max_x is not None:
    start_index, end_index = None, None
    for i in range(len(x_data)):
      if start_index is None and x_data[i] >= min_x:
        start_index = i
      if end_index is None and x_data[i] > max_x:
        end_index = i
    x_data = x_data[start_index:end_index]
    rx_data = rx_data[start_index:end_index]
    tx_data = tx_data[start_index:end_index]
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

