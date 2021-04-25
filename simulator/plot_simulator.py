#!/usr/bin/env python3

import glob
import re
import sys

import matplotlib.pyplot as plt

def main():
  args = sys.argv
  if len(args) != 2:
    print("Usage: plot_simulator.py [log_dir]")
    sys.exit(1)
  log_dir = args[1]
  output_file = "out.pdf"

  # Parse average JCT from all logs
  het_average_jcts = []
  no_het_average_jcts = []
  for log_file in glob.glob("%s/*txt" % log_dir):
    with open(log_file) as f:
      jph = int(re.match(".*_(.*)jph-.*", log_file).groups()[0])
      average_jct = None
      for line in f.readlines():
        m = re.match("Average JCT: (.*) seconds", line)
        if m is not None:
          average_jct = float(m.groups()[0])
          break
      if average_jct is None:
        raise ValueError("Did not find average JCT in %s" % log_file)
      jcts = no_het_average_jcts if "no-het" in log_file else het_average_jcts
      jcts.append((jph, average_jct))
  het_average_jcts.sort()
  no_het_average_jcts.sort()

  # Calculate percent decrease
  jct_decrease = []
  for i in range(len(het_average_jcts)):
    no_het = no_het_average_jcts[i][1]
    het = het_average_jcts[i][1]
    jct_decrease.append((no_het - het) / no_het * 100)

  # Plot it
  fig = plt.figure()
  ax = plt.axes()
  jphs = [jph for jph, _ in het_average_jcts]
  ax.plot(jphs, jct_decrease, linewidth=2)
  ax.set_ylabel("% decrease in average JCT", fontsize=16, labelpad=16)
  ax.set_xlabel("Jobs per hour", fontsize=16, labelpad=16)
  plt.xticks(fontsize=14)
  plt.yticks(fontsize=14)
  plt.savefig(output_file, bbox_inches="tight")
  print("Saved to %s" % output_file)

if __name__ == "__main__":
  main()

