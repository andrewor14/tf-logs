#!/usr/bin/env python3

import os
import re
import sys

import matplotlib.pyplot as plt

def parse_gpu_allocations(scheduler_log):
  """
  Parse the scheduler log for events containing information about GPU allocation.

  Return a map from job ID to a list of 2-tuples (time, num GPUs), where time is the
  number of seconds elapsed since the scheduler started running.
  """
  gpu_allocations = {}
  with open(scheduler_log) as f:
    lines = f.readlines()
    for line in lines:
      # Filter out lines without timestamps
      m = re.match("\[([\.\d\s]*)\] (.*)", line)
      if m is None:
        continue
      job_id = None
      num_gpus = None
      seconds_elapsed, msg = m.groups()
      seconds_elapsed = float(seconds_elapsed)
      # Match the lines of interest and extract job ID and num GPUs
      job_start_match = re.match("Job (.*) started with (.*) GPU.*", msg)
      job_end_match = re.match("Job (.*) finished.*", msg)
      job_resize_match = re.match("Job (.*) successfully resized to (.*) GPU.*", msg)
      if job_start_match is not None:
        job_id, num_gpus = job_start_match.groups()
      elif job_end_match is not None:
        job_id = job_end_match.groups()[0]
        num_gpus = 0
      elif job_resize_match is not None:
        job_id, num_gpus = job_resize_match.groups()
      # Record timestamp and allocation
      if job_id is not None:
        job_id = int(job_id)
        num_gpus = int(num_gpus)
        if job_id not in gpu_allocations:
          gpu_allocations[job_id] = []
        gpu_allocations[job_id].append((seconds_elapsed, num_gpus))

    # Make the end points connect by adding points at the start and at the end
    m = re.match("\[(.*)\] Exiting event loop.*", lines[-1])
    if m is None:
      raise ValueError("Last line was unexpected: %s" % lines[-1])
    last_timestamp = float(m.groups()[0])
    for job_id, allocs in gpu_allocations.items():
      allocs.insert(0, (0, 0))
      allocs.append((last_timestamp, 0))

  return gpu_allocations

def align_time(gpu_allocations):
  """
  Align the allocations of all jobs by the same x-axis by adding points.
  """
  all_timestamps = []
  for job_id, allocs in gpu_allocations.items():
    all_timestamps.extend([t for t, _ in allocs])
  all_timestamps = list(set(all_timestamps))
  all_timestamps.sort()
  # Add points to the allocations of each job
  for job_id, allocs in gpu_allocations.items():
    new_allocs = []
    i = 0
    j = 0
    while i < len(all_timestamps) or j < len(allocs):
      if i < len(all_timestamps) and j < len(allocs):
        pick_i = all_timestamps[i] < allocs[j][0]
      else:
        pick_i = i < len(all_timestamps)
      if pick_i:
        # Don't add a point we already added previously
        if len(new_allocs) > 0 and new_allocs[-1][0] != all_timestamps[i]:
          prev_alloc = allocs[j-1][1] if j > 0 else 0
          new_allocs.append((all_timestamps[i], prev_alloc))
        i += 1
      else:
        new_allocs.append(allocs[j])
        j += 1
    gpu_allocations[job_id] = new_allocs
  return gpu_allocations

def plot(scheduler_log):
  """
  Plot GPU allocations over time, one line per job.
  """
  gpu_allocations = align_time(parse_gpu_allocations(scheduler_log))
  output_file = scheduler_log.replace(".log", ".pdf")
  title = os.getenv("TITLE", scheduler_log.split("/")[-1].replace(".log", ""))

  # Optionally resize figure
  if "3jobs" in scheduler_log:
    fig = plt.figure(figsize=(7,3.5))
    title = ""
  else:
    fig = plt.figure()
  ax = fig.add_subplot(1, 1, 1)
  ax.set_xlabel("Time (s)", fontsize=28, labelpad=15)
  ax.set_ylabel("GPUs allocated", fontsize=28, labelpad=15)

  # Find max num GPUs to set the y-axis
  max_num_gpus = -1
  the_x = None
  all_ys = []
  all_labels = []
  if "3jobs" in scheduler_log:
    colors = ["lightskyblue", "orange", "pink"]
  else:
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color'] * 10
  for job_id in gpu_allocations.keys():
    # For every change in allocation, append a fake point right before it so
    # matplotlib draws a "vertical" line connecting the two points
    x, y = [], []
    for i, (seconds_elapsed, num_gpus) in enumerate(gpu_allocations[job_id]):
      x.append(seconds_elapsed)
      y.append(num_gpus)
      if i+1 < len(gpu_allocations[job_id]):
        x.append(gpu_allocations[job_id][i+1][0] - 0.00001)
        y.append(num_gpus)
      max_num_gpus = max(num_gpus, max_num_gpus)
    assert(the_x is None or the_x == x)
    the_x = x
    all_ys.append(y)
    all_labels.append("Job %s" % job_id)
  stacks = ax.stackplot(the_x, *all_ys, labels=all_labels, colors=colors)

  if "3jobs" in scheduler_log:
    # Set some hatches
    hatches = ["", "\\", "."]
    for i, stack in enumerate(stacks):
      stack.set_hatch(hatches[i])
      stack.set_edgecolor("white")
    # Plot submitted times as vertical dotted lines
    from plot_cdf import parse_job_times
    job_times = parse_job_times(scheduler_log)
    for job_id in job_times.keys():
      if job_id == 0:
        continue
      submitted_time = job_times[job_id][0]
      plt.axvline(x=submitted_time, linewidth=3, linestyle="--", color="black")
      ax.text(submitted_time - 130, 4.5, "J%s" % job_id, size=24, verticalalignment='center')
    plt.ylim(0, 4)

  # If this is WFS, try to find the Priority version of the same log and use
  # its end time as the x max
  xmax = os.getenv("XMAX")
  if xmax is None:
    other_log = scheduler_log.replace("WFS", "Priority")
    if os.path.isfile(other_log):
      with open(other_log) as f:
        m = re.match("\[(.*)\] Exiting event loop.*", f.readlines()[-1])
        if m is not None:
          xmax = float(m.groups()[0])
  if xmax is not None:
    plt.xlim(0, int(xmax))

  plt.yticks(range(0, max_num_gpus+1))
  if len(all_ys) <= 10:
    ax.legend(fontsize=20)
  plt.xticks(fontsize=20)
  plt.yticks(fontsize=20)
  plt.title(title.replace(r'\n', "\n"), fontsize=32, pad=25)
  fig.set_tight_layout({"pad": 1.5})
  fig.savefig(output_file, bbox_inches="tight")
  print("Saved to %s" % output_file)

def main():
  args = sys.argv
  if len(args) != 2:
    print("Usage: ./plot_gpu_allocations.py [scheduler.log]")
    sys.exit(1)
  plot(args[1])

if __name__ == "__main__":
  main()
