#!/usr/bin/env python3 

"""changelog 
This script outputs a changelog markdown to stdout.
"""

import subprocess
import re
import argparse
from packaging.version import Version

parser = argparse.ArgumentParser()
parser.add_argument('--end-tag', type=str, help='Optional end tag')
args = parser.parse_args()

# Get all the tags for the project
git_tag_result = subprocess.run(
    ["git", "tag"], capture_output=True, text=True
)

# Make a tag list
tags = git_tag_result.stdout.split("\n")

# Remove v from tags
for i in range(len(tags)):
    tags[i] = tags[i].replace('v','')

# Remove empty strings from tags
tags[:] = [x for x in tags if x]

# Sort tags by semver number
tags.sort(key = lambda x: [int(y) for y in x.split('.')])

# Remove all tags newer than end tag
if args.end_tag:
    tags = [tag for tag in tags if Version(tag) <= Version(args.end_tag.lstrip('v'))]

# Add v back into tags
for i in range(len(tags)):
    tags[i] = 'v'+tags[i]

# Iterate through all the tags in the tag list and get a list of commits
count = 0
changelogs = {}
for tag in tags:
    if tag:
        if count == 0:
            # If this is the first tag, get a list of the commits up to when the tag was created.
            git_log_result = subprocess.getoutput(
                f'git log --pretty=oneline {tag} | grep -v Merge | cut -d " " -f 2-'
            )
        else:
            # For subsequents tags, get a list of the commits since the previous tag.
            git_log_result = subprocess.getoutput(
                f'git log --pretty=oneline {tag}...{prev_tag} | grep -v Merge | cut -d " " -f 2-'
            )
        
        # Convert the commit list to a set and then back to a list to remove any duplicate commits.
        git_logs = list(set(git_log_result.split('\n')))
        
        # Sort git_logs so they are in the same order each time 
        git_logs.sort()
        
        # Add links to pull requests
        for i in range(len(git_logs)):
            if re.search(r'\(\#\d*\)',git_logs[i]):
                test = re.search(r'\(\#\d*\)',git_logs[i])
                num = test.group()
                num = num[2:]
                num = num[:-1]
                sub = ' https://github.com/itential/itential.deployer/pull/' + num
                git_logs[i] = re.sub('\(\#\d*\)',sub,git_logs[i])

        # Add the commits to the changelogs dictionary using the tag as the key and the 
        # commit list as the value
        changelogs[tag] = git_logs

        # Save the tag as the previous tag and increment the counter
        prev_tag = tag
        count = count + 1

# Create the changelog markdown output
print('# Changelog\n')
for release,changes in reversed(changelogs.items()):
    # Get the tag date in the date format we want
    release_date = subprocess.getoutput(
        f'git log -1 --format=%ad --date=format:"%B %d, %Y" {release}'
    )

    # Print the tag (release) and the date it was created
    print(f'## {release} ({release_date})\n')
    
    # Print an unordered list of the commits (changes)
    for change in changes:
        print(f'* {change}')
    print()

    for i in range(len(tags)):
        if i > 0:
            if release == tags[i]:
                full = 'https://github.com/itential/itential.deployer/compare/' + tags[i-1] + '...' + release
                print('Full Changelog:', full, '\n\n')