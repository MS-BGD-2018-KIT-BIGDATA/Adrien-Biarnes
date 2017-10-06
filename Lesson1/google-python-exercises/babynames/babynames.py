#!/usr/bin/python
# Copyright 2010 Google Inc.
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

# Google's Python Class
# http://code.google.com/edu/languages/google-python-class/

import sys
import re

"""Baby Names exercise

Define the extract_names() function below and change main()
to call it.

For writing regex, it's nice to include a copy of the target
text for inspiration.

Here's what the html looks like in the baby.html files:
...
<h3 align="center">Popularity in 1990</h3>
....
<tr align="right"><td>1</td><td>Michael</td><td>Jessica</td>
<tr align="right"><td>2</td><td>Christopher</td><td>Ashley</td>
<tr align="right"><td>3</td><td>Matthew</td><td>Brittany</td>
...

Suggested milestones for incremental development:
 -Extract the year and print it
 -Extract the names and rank numbers and just print them
 -Get the names data into a dict and print it
 -Build the [year, 'name rank', ... ] list and print it
 -Fix main() to use the extract_names list
"""

def read_file(filename):
  file = open(filename, "r")
  return file.readlines()

def extract_year(lines):
  year_regex = re.compile(r'Popularity\sin\s(\d\d\d\d)')
  for index, line in enumerate(lines):
    year_match = year_regex.search(line)
    if year_match:
      year_groups = year_match.groups()
      if len(year_groups) == 1:
        return (index, year_groups[0])

def extract_name_ranks(lines):
  name_rank_regex = re.compile(r'<td>(\d+)</td><td>(\w+)</td>\<td>(\w+)</td>')
  name_ranks = []
  for line in lines:
    name_rank_match = name_rank_regex.search(line)
    if name_rank_match:
      name_rank_groups = name_rank_match.groups()
      if len(name_rank_groups) == 3:
        name_ranks.append((name_rank_groups[0], name_rank_groups[1]))
        name_ranks.append((name_rank_groups[0], name_rank_groups[2]))
  name_ranks.sort(key=lambda tup: tup[1])
  return map(lambda kvp : kvp[1] + ' ' + kvp[0], name_ranks)

def extract_names(filename):
  """
  Given a file name for baby.html, returns a list starting with the year string
  followed by the name-rank strings in alphabetical order.
  ['2006', 'Aaliyah 91', Aaron 57', 'Abagail 895', ' ...]
  """
  lines = read_file(filename)
  (index, year) = extract_year(lines)
  name_ranks = extract_name_ranks(lines[index:])

  return [year] + name_ranks


def main():
  # This command-line parsing code is provided.
  # Make a list of command line arguments, omitting the [0] element
  # which is the script itself.
  args = sys.argv[1:]

  if not args:
    print('usage: [--summaryfile] file [file ...]')
    sys.exit(1)

  # Notice the summary flag and remove it from args if it is present.
  summary = False
  if args[0] == '--summaryfile':
    summary = True
    del args[0]

  # +++your code here+++
  # For each filename, get the names, then either print the text output
  # or write it to a summary file
  result = extract_names(args[0])
  print(result)
  
if __name__ == '__main__':
  main()
