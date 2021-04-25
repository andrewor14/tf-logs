#!/usr/bin/env python3

import glob
import re
import sys

import matplotlib.pyplot as plt

def main():
  args = sys.argv
  if len(args) < 2:
    print("Usage: plot_simulator.py [log_dir] <jph1> <jph2> <jph3> ...")
    sys.exit(1)
  log_dir = args[1]
  jph_filter = set([int(x) for x in args[2:]])
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
  jphs = []
  jct_decrease = []
  for i in range(len(het_average_jcts)):
    jph, no_het = no_het_average_jcts[i]
    _, het = het_average_jcts[i]
    if len(jph_filter) > 0 and jph not in jph_filter:
      continue
    jphs.append(jph)
    jct_decrease.append((no_het - het) / no_het * 100)

  # Plot it
  fig = plt.figure()
  ax = plt.axes()
  ax.plot(jphs, jct_decrease, linewidth=2, marker="x", markeredgewidth=3, markersize=8)
  ax.set_ylabel("% decrease in average JCT", fontsize=16, labelpad=16)
  ax.set_xlabel("Jobs per hour", fontsize=16, labelpad=16)
  ax.set_ylim(ymin=min(jct_decrease + [0]))
  plt.xticks(fontsize=14)
  plt.yticks(fontsize=14)
  plt.savefig(output_file, bbox_inches="tight")
  print("Saved to %s" % output_file)

if __name__ == "__main__":
  main()

