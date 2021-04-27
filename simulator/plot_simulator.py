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
  output_file = "%s.pdf" % log_dir.strip("/")

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

  # Plot it
  fig = plt.figure(figsize=(6.5, 2.75))
  ax = plt.axes()
  jphs = [j for j, _ in het_average_jcts]
  gavel = [jct for _, jct in no_het_average_jcts]
  gavel_ht = [jct for _, jct in het_average_jcts]
  percentage_decrease = [(gavel[i] - gavel_ht[i]) / gavel[i] * 100 for i in range(len(jphs))]
  for i in [3]:
    plt.annotate("-%.3g%%" % percentage_decrease[i], (jphs[i], gavel_ht[i]),
      textcoords="offset points", xytext=(0,-18), ha='center', fontsize=10)
  ax.plot(jphs, gavel, linewidth=2, marker="x", markeredgewidth=3, markersize=8, label="Gavel")
  ax.plot(jphs, gavel_ht, linewidth=2, marker="x", markeredgewidth=3, markersize=8, label="Gavel + HT")
  ax.set_ylabel("Avg JCT (s)", fontsize=16, labelpad=12)
  ax.set_xlabel("Jobs per hour", fontsize=16, labelpad=12)
  ax.set_ylim(ymin=0, ymax=max(gavel) * 1.1)
  ax.legend(loc="lower right", fontsize=14, ncol=2)
  plt.xticks(fontsize=14)
  plt.yticks(fontsize=14)
  plt.savefig(output_file, bbox_inches="tight")
  for i in range(len(jphs)):
    print("%s jobs per hour => %.3g%% decrease" % (jphs[i], percentage_decrease[i]))
  print("Saved to %s" % output_file)

if __name__ == "__main__":
  main()

