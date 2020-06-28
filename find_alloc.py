#!/usr/bin/env python3

import datetime
import sys 

import numpy as np


MARKER = "ANDREW"

def prettify_bytes(size, decimal_places=2):
  # Stolen from https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
  for unit in ['B','KB','MB','GB','TB']:
    if size < 1000.0:
      break
    size /= 1000.0
  return f"{size:.{decimal_places}f}{unit}"

def parse_timestamp(timestamp):
  return datetime.datetime.strptime(timestamp, "%H:%M:%S.%f")

def parse_memory_over_time_elapsed(data_file):
  """
  Parse memory usage over time elapsed from `data_file`.
  Return a tuple of two lists: (time elapsed in seconds, memory usage in bytes).
  """
  raw_timestamps, memory_used = parse_memory_over_time(data_file)
  first_timestamp = parse_timestamp(raw_timestamps[0])
  time_elapsed = [(parse_timestamp(t) - first_timestamp).total_seconds()\
    for t in raw_timestamps]
  return (time_elapsed, memory_used)

def parse_memory_over_time(data_file):
  """
  Parse memory usage over time from `data_file`, a path to a space separated file
  with four fields: (timestamp, [Allocate|Deallocate], num_bytes, allocation_id).
  Timestamp is expected to be in the format (hour:minute:seconds), e.g.
  15:13:03.741560.

  Return a tuple of two lists: (raw timestamps, memory usage in bytes).
  """
  raw_timestamps = []
  memory_used = []
  with open(data_file) as f:
    for line in f.readlines():
      split = tuple(line.split(" "))
      raw_timestamp = split[0]
      action = split[1].strip()
      if action == MARKER:
        continue
      num_bytes = split[2]
      raw_timestamps.append(raw_timestamp)
      # Parse new memory usage
      current_memory = memory_used[-1] if len(memory_used) > 0 else 0
      delta_bytes = int(num_bytes)
      action = action.lower()
      if action == "deallocate":
        delta_bytes *= -1
      elif action != "allocate":
        raise ValueError("Malformed line: %s" % line)
      memory_used.append(current_memory + delta_bytes)
  return raw_timestamps, memory_used

def parse_markers(data_file):
  """
  Parse the times (relative to first timestamp) at which the MARKER token appears in `data_file`.
  """
  first_timestamp = None
  marker_times = []
  with open(data_file) as f:
    for line in f.readlines():
      split = tuple(line.split(" "))
      timestamp = parse_timestamp(split[0])
      if first_timestamp is None:
        first_timestamp = timestamp
      if split[1].strip() == MARKER:
        marker_times.append((timestamp - first_timestamp).total_seconds())
  return marker_times

def find_alloc(data_file, max_alloc=True, range_start=None, range_end=None):
  '''
  Return a 2-tuple (time_elapsed, memory allocated) that corresponds to
  the point when the cumulative memory allocation is at a maximum or minimum.
  Optional range start and range end are inclusive.
  '''
  raw_timestamps, memory_used = parse_memory_over_time(data_file)
  timestamps = [parse_timestamp(t) for t in raw_timestamps]
  time_elapsed = [(t - timestamps[0]).total_seconds() for t in timestamps]
  if range_start is not None:
    indices = np.where(np.array(time_elapsed) >= range_start)[0]
    if len(indices) == 0:
      return (None, None)
    start_index = indices[0]
    time_elapsed = time_elapsed[start_index:]
    memory_used = memory_used[start_index:]
  if range_end is not None:
    indices = np.where(np.array(time_elapsed) <= range_end)[0]
    if len(indices) == 0:
      return (None, None)
    end_index = indices[-1]
    time_elapsed = time_elapsed[:end_index+1]
    memory_used = memory_used[:end_index+1]
  arg_function = np.argmax if max_alloc else np.argmin
  result_index = arg_function(np.array(memory_used))
  return (time_elapsed[result_index], memory_used[result_index])

def print_usage_and_exit():
  print("Usage: find_alloc.py [data.txt] <['max' or 'min']> <[after this timestamp]> <[before this timestamp]>")
  sys.exit(1)

def main():
  args = sys.argv
  if len(args) < 2 or len(args) > 5:
    print_usage_and_exit()
  # Parse arguments
  max_or_min = args[2].lower() if len(args) > 2 else "max"
  if max_or_min not in ["max", "min"]:
    print("Invalid mode: '%s', must be one of 'max' or 'min'" % max_or_min)
    print_usage_and_exit()
  max_alloc = max_or_min == "max"
  range_start = float(args[3]) if len(args) > 3 else None
  range_end = float(args[4]) if len(args) > 4 else None
  # Find max/min allocation
  time_elapsed, alloc = find_alloc(args[1], max_alloc, range_start, range_end)
  if time_elapsed is not None and alloc is not None:
    print("%s alloc: %s at %.3fs" % (max_or_min.capitalize(), prettify_bytes(alloc), time_elapsed))
  else:
    print("No allocations found within given range")

if __name__ == "__main__":
  main()

