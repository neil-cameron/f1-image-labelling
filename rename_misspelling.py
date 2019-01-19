import os
import glob
from pathlib import Path

root = '/Users/Neil/Library/Mobile Documents/com~apple~CloudDocs/Image Labelling/07 Labelled Images'
orig_name = '**/labeled_images.csv'
full_glob = Path(root, orig_name)

files_to_rename = glob.glob(str(full_glob), recursive=True)
print('Number of matches found is', len(files_to_rename))

for file in files_to_rename:
	orig = Path(file)
	renamed_path = Path(orig.parent, 'labelled_images.csv')
	orig.rename(renamed_path)