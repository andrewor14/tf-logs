#!/usr/bin/env python

import datetime
import math
import json
import os
import sys

import numpy as np


# ========================= #
#  COMMON HELPER FUNCTIONS  #
# ========================= #

VERBOSE = False

# Validate the specified log dir and return the log files.
# The structure should be log_dir/1/rank.x, where x+1 is the number of nodes used in the job.
# If we're interested in the horovod trace, then only check that the trace exists and return it.
def validate_log_dir(log_dir, horovod_trace=False):
  temp_dir = os.listdir(log_dir)
  if horovod_trace:
    if "horovod_timeline.json" not in temp_dir:
      raise ValueError("ERROR: horovod_timeline.json not found under %s" % log_dir)
    return os.path.join(log_dir, "horovod_timeline.json")
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


# ============================== #
#  ALLREDUCE COMMUNICATION TIME  #
# ============================== #

LAST_N_COMMUNICATION_TIMES = 10
MIN_COMMUNICATION_COUNT = 2

# Parse the allreduce communication times (seconds) from the given trace
# Tag refers to an identifier (a string) for the name of the process ("tensor")
# Communicating a model consists of multiple rounds of allreduce (for multiple layers)
# Thus, we simply sum up the communication times across different tensors matching the tag
def parse_allreduce_times(horovod_trace, tag):
  json_str = None
  with open(horovod_trace) as f:
    json_str = f.read()
  # A lot of these traces end with a comma for some reason,
  # which json dislikes, so we manually fix it here
  if json_str.endswith(",\n"):
    json_str = json_str[:-2] + "]\n"
  events = json.loads(json_str)
  # Find the pids (kind of like "tensor ID") that we care about
  pids = []
  for e in events:
    if "name" in e and e["name"] == "process_name" and tag.lower() in e["args"]["name"].lower():
      pids.append(e["pid"])
  # Parse the communication times from the begin and end events of interest
  communication_times = {} # pid -> communication times (seconds)
  for pid in pids:
    begin_timestamp = None
    communication_times[pid] = []
    for e in events:
      if e["pid"] == pid:
        if begin_timestamp is None:
          if e["ph"] == "B" and e["name"] == "ALLREDUCE":
            begin_timestamp = e["ts"]
        else:
          if e["ph"] == "E" and "args" in e and "shape" in e["args"]:
            communication_time_us = e["ts"] - begin_timestamp
            communication_times[pid].append(float(communication_time_us) / 1000 / 1000)
            begin_timestamp = None
  # Sum up the communication times across different tensors.
  # Because of tensor fusion, some tensors may not be communicated many rounds.
  # We will filter these out in our computation.
  summed_communication_times = []
  for pid, times in communication_times.items():
    if len(times) < MIN_COMMUNICATION_COUNT:
      continue
    if len(summed_communication_times) == 0:
      summed_communication_times = times
    elif len(summed_communication_times) == len(times):
      summed_communication_times = np.add(summed_communication_times, times).tolist()
    else:
      raise ValueError("Inconsistent lengths of communication times: %s" % communication_times)
  # Return only last N communication times to skip warmup
  summed_communication_times = summed_communication_times[
    len(summed_communication_times) - LAST_N_COMMUNICATION_TIMES:]
  return summed_communication_times

# Return the average allreduce time (seconds) and its variance across all nodes running in a job
def get_allreduce_time_average_and_variance(log_dir, tag):
  horovod_trace = validate_log_dir(log_dir)
  allreduce_times = parse_allreduce_times(horovod_trace, tag)
  average = np.mean(allreduce_times)
  variance = np.var(allreduce_times)
  if VERBOSE:
    print("Log dir: %s, average: %s, variance: %s" % (log_dir, average, variance))
  return (average, variance)

# Return the allreduce time (seconds) averaged across all nodes running in a job
def get_average_allreduce_time(log_dir):
  (average_allreduce_time, _) = get_allreduce_time_average_and_variance(log_dir)
  return average_allreduce_time


# =========== #
#  STEP TIME  #
# =========== #

# Parse step times from the given log file, interpolating missing values if necessary
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

