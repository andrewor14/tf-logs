#!/usr/bin/env python

import datetime
import os
import sys

# Validate the specified log dir and return the log files.
# The structure should be log_dir/1/rank.x, where x+1 is the number of nodes used in the job.
def validate_log_dir(log_dir):
  temp_dir = os.listdir(log_dir)
  if temp_dir != ["1"]:
    raise ValueError("ERROR: expected structure log_dir/1, was %s" % temp_dir)
  log_dir = os.path.join(log_dir, temp_dir[0])
  for d in os.listdir(log_dir):
    if not d.startswith("rank"):
      raise ValueError("ERROR: expected structure log_dir/1/rank.x, was %s" % d)
    log_files = os.listdir(os.path.join(log_dir, d))
    if sorted(log_files) != ["stderr", "stdout"]:
      raise ValueError("ERROR: expected log dir to contain 'stderr' and 'stdout' only, was %s" % log_files)
  log_files = [os.path.join(os.path.join(log_dir, d), "stderr") for d in os.listdir(log_dir)]
  return log_files

def parse_step_time(log_file):
  with open(log_file) as f:
    lines = [l for l in f.readlines() if "images/sec" in l]
    timestamps = [" ".join(l.split()[:2]) for l in lines]
    timestamps = [datetime.datetime.strptime(ts, "I%m%d %H:%M:%S.%f") for ts in timestamps]
    deltas = []
    for i in range(1, len(timestamps)):
      deltas.append(float((timestamps[i] - timestamps[i - 1]).total_seconds()))
    average_delta = sum(deltas) / len(deltas)
    step_time = average_delta / 10 # prints once every 10 steps
    return step_time

# Return the step time (seconds) averaged across all nodes running in a job, and across all jobs
def get_average_step_time(log_dirs):
  step_times = []
  for log_dir in log_dirs:
    log_files = validate_log_dir(log_dir)
    for log_file in log_files:
      step_time = parse_step_time(log_file)
      step_times.append(step_time)
  average_step_time = sum(step_times) / len(step_times)
  return average_step_time

def main():
  args = sys.argv
  if len(args) < 2:
    print("Usage: parse_mpi_logs [log_dir] <[log_dir2], [log_dir3] ...>")
    sys.exit(1)
  print(get_average_step_time(args[1:]))

if __name__ == "__main__":
  main()

