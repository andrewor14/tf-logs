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

def plot(scheduler_logs):
  output_file = os.getenv("OUTPUT_FILE", "jct_cdf.pdf")
  title = os.getenv("TITLE")
  fig = plt.figure()
  ax = fig.add_subplot(1, 1, 1)
  ax.set_xlabel("Duration (s)", fontsize=24, labelpad=15)
  ax.set_ylabel("JCT CDF", fontsize=24, labelpad=15)

  for scheduler_log in scheduler_logs:
    label = scheduler_log.replace(".log", "").split("/")[-1]
    job_times = parse_job_times(scheduler_log)
    all_jcts = []
    for job_id in job_times.keys():
      submit, start, end = job_times[job_id]
      all_jcts.append(end - submit)
    all_jcts = np.sort(all_jcts)
    cdf = 1. * np.arange(len(all_jcts)) / (len(all_jcts) - 1)
    ax.plot(all_jcts, cdf, label=label, linewidth=3)
  ax.legend(fontsize=12)
  plt.xticks(fontsize=16)
  plt.yticks(fontsize=16)
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
  plot(args[1:])

if __name__ == "__main__":
  main()
