"""This cli entrypoint is for running distributed multiruns."""

import sys
import os
from do3se.project import Project
from pprint import pprint
import json

if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) != 1:
        raise ValueError(
            'Must only include project file location as argument.')

    project_file_loc = args[0]
    output_file_location = project_file_loc.split('.do3se')[0] + '.json'
    project = Project(project_file_loc)
    print(output_file_location)
    with open(output_file_location, 'w') as outfile:
        json.dump(dict(project.data), outfile)
