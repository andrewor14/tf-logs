#!/usr/bin/env python

import datetime
import math
import os
import sys

import numpy as np

VERBOSE = False

# Validate the specified log dir and return the log files.
# The structure should be log_dir/1/rank.x, where x+1 is the number of nodes used in the job.
def validate_log_dir(log_dir):
  temp_dir = os.listdir(log_dir)
  if "1" not in temp_dir:
    raise ValueError("ERROR: expected structure log_dir/1, was %s" % temp_dir)
  log_dir = os.path.join(log_dir, "1")
  for d in os.listdir(log_dir):
    if not d.startswith("rank"):
      raise ValueError("ERROR: expected structure log_dir/1/rank.x, was %s" % d)
    log_files = os.listdir(os.path.join(log_dir, d))
    if "stderr" not in log_files:
      raise ValueError("ERROR: expected log dir to contain file 'stderr', was %s" % log_files)
  log_files = [os.path.join(os.path.join(log_dir, d), "stderr") for d in os.listdir(log_dir)]
  return log_files

def parse_step_times(log_file):
  with open(log_file) as f:
    # Parse step numbers and timestamps
    steps, timestamps = [], []
    for line in f.readlines():
      if "images/sec" not in line or "total" in line:
        continue
      split = line.split()
      steps.append(int(split[4]))
      timestamp = " ".join(split[:2])
      timestamp = datetime.datetime.strptime(timestamp, "I%m%d %H:%M:%S.%f")
      timestamps.append(timestamp)
    # Interpolate missing values
    step_times = []
    for i in range(1, len(steps)):
      step_delta = steps[i] - steps[i-1]
      timestamp_delta = float((timestamps[i] - timestamps[i - 1]).total_seconds())
      step_times += [timestamp_delta / step_delta] * step_delta
    return step_times

# Return the average step time (seconds) and its variance across all nodes running in a job
def get_step_time_average_and_variance(log_dir):
  averages = []
  variances = []
  log_files = validate_log_dir(log_dir)
  for log_file in log_files:
    step_times = parse_step_times(log_file)
    averages.append(np.mean(step_times))
    variances.append(np.var(step_times))
  average = np.mean(averages)
  variance = np.mean(variances)
  if VERBOSE:
    print("Log dir: %s, average: %s, variance: %s" % (log_dir, average, variance))
  return (average, variance)

# Return the step time (seconds) averaged across all nodes running in a job
def get_average_step_time(log_dir):
  (average_step_time, _) = get_step_time_average_and_variance(log_dir)
  return average_step_time

def main():
  args = sys.argv
  if len(args) < 2:
    print("Usage: parse_mpi_logs [log_dir] <[log_dir2], [log_dir3] ...>")
    sys.exit(1)
  step_times = []
  for log_dir in args[1:]:
    step_times.append(get_average_step_time(log_dir))
  average_step_time = sum(step_times) / len(step_times)
  print(average_step_time)

if __name__ == "__main__":
  main()

