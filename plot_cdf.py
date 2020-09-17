#!/usr/bin/env python3

import os
import re
import sys

import matplotlib.pyplot as plt
import numpy as np

def parse_job_times(scheduler_log):
  """
  Parse the (submit, start, end) times for all jobs.
  Return a dictionary mapping from job ID to this 3-tuple.
  """
  # Job ID to (submit, start, end)
  job_times = {}
  with open(scheduler_log) as f:
    for line in f.readlines():
      # Filter out lines without timestamps
      m = re.match("\[([\.\d\s]*)\] (.*)", line)
      if m is None:
        continue
      job_id = None
      num_gpus = None
      seconds_elapsed, msg = m.groups()
      seconds_elapsed = float(seconds_elapsed)
      job_submit_match = re.match("Job (.*) submitted.*", msg)
      job_start_match = re.match("Job (.*) started.*", msg)
      job_end_match = re.match("Job (.*) finished.*", msg)
      if job_submit_match is not None:
        job_id = job_submit_match.groups()[0]
        list_index = 0
      elif job_start_match is not None:
        job_id = job_start_match.groups()[0]
        list_index = 1
      elif job_end_match is not None:
        job_id = job_end_match.groups()[0]
        list_index = 2
      if job_id is not None:
        job_id = int(job_id)
        if job_id not in job_times:
          job_times[job_id] = [None, None, None]
        job_times[job_id][list_index] = seconds_elapsed
  return job_times

def plot(scheduler_logs, metric="jct"):
  output_file = os.getenv("OUTPUT_FILE", "9-14-2/elasticity-20jobs-%s.pdf" % metric)
  space_xticks_apart = os.getenv("SPACE_XTICKS_APART", "").lower() == "true"

  title = os.getenv("TITLE")
  fig = plt.figure(figsize=(3,2.5))
  ax = fig.add_subplot(1, 1, 1)
  ax.set_xlabel("Duration (s)", fontsize=14, labelpad=10)
  ylabel = "JCT CDF" if metric == "jct" else "Queuing delay CDF"
  ax.set_ylabel(ylabel, fontsize=14, labelpad=10)

  for scheduler_log in scheduler_logs:
    if "WFS" in scheduler_log:
      label = "VF"
    elif "Priority" in scheduler_log:
      label = "Priority"
    else:
      label = scheduler_log.replace(".log", "").split("/")[-1]
    job_times = parse_job_times(scheduler_log)
    all_values = []
    for job_id in job_times.keys():
      submit, start, end = job_times[job_id]
      if metric == "jct":
        all_values.append(end - submit)
      else:
        all_values.append(start - submit)
    all_values = np.sort(all_values)
    print("%s median: %s" % (label, all_values[int(len(all_values)/2)]))
    cdf = 1. * np.arange(len(all_values)) / (len(all_values) - 1)
    style = "-" if label == "VF" else "--"
    width = 3 if label == "VF" else 1.5
    ax.plot(all_values, cdf, label=label, linestyle=style, linewidth=width)
  ax.legend(fontsize=12, handlelength=1)
  if space_xticks_apart:
    ax.set_xticks([max(xx, 0) for xx in ax.get_xticks()[::3]])
  plt.xticks(fontsize=10)
  plt.yticks(fontsize=10)
  if title is not None:
    plt.title(title, fontsize=20, pad=15)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(output_file, bbox_inches="tight")
  print("Saved to %s" % output_file)

def main():
  args = sys.argv
  if len(args) < 2:
    print("Usage: ./plot_cdf.py [scheduler1.log] [scheduler2.log] ...")
    sys.exit(1)
  plot(args[1:], "jct")
  plot(args[1:], "queuing")

if __name__ == "__main__":
  main()
