#!/usr/bin/env python3

import datetime
import os
import sys

import numpy as np


def parse_timestamp(timestamp):
  return datetime.datetime.strptime(timestamp, "%H:%M:%S.%f")

def print_unreleased_allocation_ids(data_file, until_this_timestamp):
  until_this_timestamp = parse_timestamp(until_this_timestamp)
  unreleased_allocation_ids_with_num_bytes = []
  with open(data_file) as f:
    for line in f.readlines():
      timestamp, allocate_or_deallocate, num_bytes, allocation_id = tuple(line.strip().split(" "))
      timestamp = parse_timestamp(timestamp)
      if timestamp > until_this_timestamp:
        break
      # Keep or remove this allocation ID
      allocate_or_deallocate = allocate_or_deallocate.lower() 
      if allocate_or_deallocate == "allocate":
        unreleased_allocation_ids_with_num_bytes.append((allocation_id, num_bytes))
      elif allocate_or_deallocate == "deallocate":
        unreleased_allocation_ids_with_num_bytes.remove((allocation_id, num_bytes))
      else:
        raise ValueError("Malformed line: %s" % line)
  for allocation_id, num_bytes in unreleased_allocation_ids_with_num_bytes:
    print(allocation_id, num_bytes)

def main():
  args = sys.argv
  if len(args) != 3:
    print("Usage: unreleased_alloc_ids.py [data.txt] [until_this_timestamp]")
    print("  e.g. ./unreleased_alloc_ids.py data.txt 14:09:03.208021")
    sys.exit(1)
  print_unreleased_allocation_ids(args[1], args[2])

if __name__ == "__main__":
  main()

