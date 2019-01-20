import pygame
import os
import sys
import getopt
from PIL import Image
import numpy as np
import pandas as pd
import csv
from itertools import islice
import webbrowser
from pathlib import Path, PureWindowsPath

# Choose operating system
opsys = 'mac' # 'mac' or 'pc'
if opsys == 'mac':
	# csv_root = Path('/Users/Neil/Dropbox/Documents/Apple and Python Scripts/F1 Image Labelling Py')
	csv_root = Path('/Users/Neil/Library/Mobile Documents/com~apple~CloudDocs/Image Labelling')
else:
	csv_root = Path(r'C:\Users\neil.cameron\OneDrive - McLaren Technology Group')

# Set resized image size
img_size = 1000

# Set window size
window_width = 1000
window_height = 790

# Function for parsing the input and output directories
def main(argv):
	input_path = ''
	output_path = ''
	load_file = ''
	try:
		opts, args = getopt.getopt(argv,"hi:o:l:",["ifile=","ofile=","lfile="])
	except getopt.GetoptError:
		print ('imglbl.py -i <input_path> -o <output_path> or imglbl.py -l <load_file>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print ('imglbl.py -i <input_path> -o <output_path> or imglbl.py -l <load_file>')
			sys.exit()
		elif opt in ("-i", "--ifile"):
			input_path = arg
			print ('Input directory path is "', input_path)
		elif opt in ("-o", "--ofile"):
			output_path = arg
			print ('Output directory path "', output_path)
		elif opt in ("-l", "--lfile"):
			load_file = Path(arg)
			print ('Loaded data path is "', load_file)
	return (input_path, output_path, load_file)

# Function for proportionally scaling an image and saving it to a new location 
def scale_image(input_image_path, output_image_path, width=None, height=None):
	original_image = Image.open(input_image_path)
	w, h = original_image.size
	print('The original image size is {wide} wide x {height} '
		  'high'.format(wide=w, height=h))
 
	if width and height:
		max_size = (width, height)
	elif width:
		max_size = (width, h)
	elif height:
		max_size = (w, height)
	else:
		# No width or height specified
		raise RuntimeError('Width or height required!')
 
	original_image.thumbnail(max_size, Image.ANTIALIAS)
	original_image.save(output_image_path)
	
	scaled_image = Image.open(output_image_path)

	width, height = scaled_image.size
	print('The scaled image size is {wide} wide x {height} '
		  'high'.format(wide=width, height=height))

# Function for duplicating a folder structure and calling the scale_image function on each image
def dup_scale(walk_dir, out_dir):
	scaled_images_list = []
	original_images_list = []
	for root, subdirs, files in os.walk(walk_dir):
		structure = os.path.join(out_dir, root[(len(walk_dir)+1):])
		if not os.path.isdir(structure):
			os.mkdir(structure)
		else:
			print('Folder already exits')

		# Copy over the files but resized
		if files:
			for file in files:
				if file.split('.')[1].lower() == 'jpg':
					try:
						input_image_path = os.path.join(root, file)
						scaled_image_path = os.path.join(structure, file)
						scale_image(input_image_path, scaled_image_path, width=img_size)
						scaled_images_list.append(scaled_image_path)
						original_images_list.append(input_image_path)
					except OSError:
						pass
	return(original_images_list, scaled_images_list)

# Function for taking the scaled image paths and converting them for Mac
def repath(path, csv_root):   
    csv_root_lst = list(csv_root.parts)
    path_lst = list(PureWindowsPath(path).parts)
    fr = path_lst.index('07 Labelled Images')
    path_lst = path_lst[fr:]
    remainder = Path(*[item for item in path_lst])
    output_path = Path(csv_root, remainder)
    return output_path

# Function for recreating the original_images_list and scaled_images_list and lbl_list_fr_file from a file
def read_file(load_file, opsys):
	original_images_list = []
	scaled_images_list = []
	lbl_list_fr_file = []
	
	with open(load_file) as file:
		read_file = csv.reader(file, delimiter=',')
		for row in islice(read_file, 1, None):
			original_images_list.append(row[1])
			scaled_images_list.append(str(repath(Path(row[2]), csv_root)))
			# Take the comma separated values for lable and split them into a list
			labels_content = row[3:][0].split(', ')
			lbl_list_fr_file.append(labels_content)
	return(original_images_list, scaled_images_list, lbl_list_fr_file)

# Stuff to do after each key press
def gui_chrome(scaled_images_list, lbl_list, img_index, window_width):
	font = pygame.font.SysFont('Arial', 16)
	black = (0,0,0)
	white = (255,255,255)
	legend_l1 = '[1 - Merc]  [2 - Red Bull]  [3 - Ferrari]  [4 - Force India]  [5 - Williams]  [6 - McLaren]  [7 - Haas]  [8 - Torro Rosso]  [9 - Renault]  [0 - Sauber]'
	#legend_l2 = '[F - Front]   [R - Rear]   [D - Dead Rear]   [S - Side]   [A - Above]   [G - Garage]   [T - Track]'
	legend_l2 = '[F - Front Wing]  [R - Rear Wing]  [C - Chassis]  [S - Front Suspension]  [U - Rear Suspension]  [L - Floor]  [E - Engine]  [M - Maincase]'
	legend_l3 = '[I - Internals]  [B - Front Brake Duct]  [K - Rear Brake Duct]  [H - Ride Height]  [D - Dead Rear]  [A - Above]  [G - Garage]  [T - Track]  [P - Pick]'
	legend_l4 = '[' + str(img_index) + '/' + str((len(scaled_images_list)-1)) + ']'
	
	# Display each image
	screen.fill(black)
	screen.blit(pygame.image.load(scaled_images_list[img_index]), (0, 0))
	
	# Show text options
	screen.blit(font.render(legend_l1, True, white), (10, (window_height-55)))
	screen.blit(font.render(legend_l2, True, white), (10, (window_height-35)))
	screen.blit(font.render(legend_l3, True, white), (10, (window_height-15)))
	screen.blit(font.render(legend_l4, True, white), (10, 10))
	
	# Show any labels applied
	top_lbl = str(lbl_list[img_index])
	screen.blit(font.render(top_lbl, True, white), (10, (window_height-90)))

	pygame.display.flip()

# Get input and output directories and running mode
walk_dir, out_dir, load_file = main(sys.argv[1:])

# Run the duplication and resizing unless we are loading previous work
if load_file:
	print('Loading previous work...')
	original_images_list, scaled_images_list, lbl_list_fr_file = read_file(load_file, opsys)
else:
	original_images_list, scaled_images_list = dup_scale(walk_dir, out_dir)

# Setup GUI
pygame.init()
screen = pygame.display.set_mode((window_width, window_height))
done = False
clock = pygame.time.Clock()
pygame.key.set_repeat(100, 100) # Enable holding down keys

# Stuff to pass into pygame functions
lbl_list = [[] for i in range(len(scaled_images_list))]
if load_file:
	lbl_list = lbl_list_fr_file
	for index, item in enumerate(lbl_list):
		lbl_list[index] = ' '.join(item).split()
img_index = 0
#press_dict = {'Front':pygame.K_f, 'Rear':pygame.K_r, 'Dead':pygame.K_d, 'Side':pygame.K_s, 'Above':pygame.K_a, 'Garage':pygame.K_g, 'Track':pygame.K_t, 'Mercedes':pygame.K_1, 'Red Bull':pygame.K_2, 'Ferrari':pygame.K_3, 'Force India':pygame.K_4, 'Williams':pygame.K_5, 'McLaren':pygame.K_6, 'Haas':pygame.K_7, 'Torro Rosso':pygame.K_8, 'Renault':pygame.K_9, 'Sauber':pygame.K_0}
press_dict = {'Front_Wing':pygame.K_f, 'Rear_Wing':pygame.K_r, 'Chassis':pygame.K_c, 'Front_Suspension':pygame.K_s, 'Rear_Suspension':pygame.K_u, 'Floor':pygame.K_l, 'Engine':pygame.K_e, 'Maincase':pygame.K_m, 'Internals':pygame.K_i, 'Front_Brake_Duct':pygame.K_b, 'Rear_Brake_Duct':pygame.K_k, 'Ride_Height':pygame.K_h, 'Dead_Rear':pygame.K_d, 'Above':pygame.K_a, 'Garage':pygame.K_g, 'Track':pygame.K_t, 'Pick':pygame.K_p, 'Mercedes':pygame.K_1, 'Red_Bull':pygame.K_2, 'Ferrari':pygame.K_3, 'Force_India':pygame.K_4, 'Williams':pygame.K_5, 'McLaren':pygame.K_6, 'Haas':pygame.K_7, 'Torro_Rosso':pygame.K_8, 'Renault':pygame.K_9, 'Sauber':pygame.K_0}

# Run the GUI
pygame.event.clear()
while not done:
	event = pygame.event.wait()
	if event.type == pygame.QUIT:
		done = True
	
	# Initial run
	gui_chrome(scaled_images_list, lbl_list, img_index, window_width)

	pressed = pygame.key.get_pressed()
	
	# Check for image labelling input
	for key in press_dict:
		if pressed[press_dict[key]]:
			if key in lbl_list[img_index]:
				lbl_list[img_index].remove(key)
				gui_chrome(scaled_images_list, lbl_list, img_index, window_width)
			else:
				lbl_list[img_index].append(key)
				gui_chrome(scaled_images_list, lbl_list, img_index, window_width)
	
	# Check for image moving input
	if pressed[pygame.K_LEFT]:
		if img_index == 0:
			img_index = (len(scaled_images_list)-1)
			gui_chrome(scaled_images_list, lbl_list, img_index, window_width)
		else:
			img_index -= 1
			gui_chrome(scaled_images_list, lbl_list, img_index, window_width)
	if pressed[pygame.K_RIGHT]:
		if img_index == (len(scaled_images_list)-1):
			img_index = 0
			gui_chrome(scaled_images_list, lbl_list, img_index, window_width)
		else:
			img_index += 1
			gui_chrome(scaled_images_list, lbl_list, img_index, window_width)
			
	# Command for jumping to image 0
	if pressed[pygame.K_HOME]:
		img_index = 0
		gui_chrome(scaled_images_list, lbl_list, img_index, window_width)
	
	# Command for jumping to the next non-labelled image
	if pressed[pygame.K_END]:
		for index,item in enumerate(lbl_list):
			if not item:
				img_index = index
				break
		gui_chrome(scaled_images_list, lbl_list, img_index, window_width)
		
	# Subrouteen for jumping to a specific image number
	if pressed[pygame.K_SLASH]:
		print('Jump to image...')
		jump_to = ''
		j = 0
		while j < 3:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					digit = (pygame.key.name(event.key))
					if digit.isdigit():
						jump_to += digit
						j += 1
					else:
						print('Not a number')
		print (jump_to)
		if int(jump_to) <= len(scaled_images_list):
			img_index = int(jump_to)
			gui_chrome(scaled_images_list, lbl_list, img_index, window_width)
		else:
			print('Sorry, that index is out of range')
			
	# Open fullscreen
	if pressed[pygame.K_EQUALS]:
		webbrowser.open(original_images_list[img_index])
			
	clock.tick(30)

# Make labels a comma separated string
lbl_list = [', '.join(i) for i in lbl_list]

# Make a dataframe of the paths to the original and scaled images and their labels
image_df = pd.DataFrame(data=original_images_list, columns=['Image Path'])
image_df['Scaled Image Path'] = pd.Series(scaled_images_list)
image_df['Labels'] = pd.Series(lbl_list)

# Output dataframe to csv
if load_file:
	image_df.to_csv(load_file, sep=',')
else:
	image_df.to_csv(os.path.join(out_dir, 'labelled_images.csv'))