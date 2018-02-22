#!/usr/bin/env python3
import csv
import sys
from time import strftime
from re import match

def moodle2canvas_single(moodle_fl="moodle.csv", canvas_fl="grades.csv", lab_sec_fl="my_sections.csv", grade_col_ind=11):
	'''
	moodle2canvas for single-person assignements (i.e. Quiz)
	Args:

	moodle_fl (default="moodle.csv") - str: the input grades file in moodle format found on the quiz server under Results -> Grades. These should be restuls from one quiz

	canvas_fl (default="grades.csv") - str: the input grades file in canvas format. This shouold contain all grades from all students in that particular section
	
	lab_sec_fl (default="my_sections.csv") - str: a csv containing only YOUR lab sections with tho columns set up as: ID, Email. Note: this assumes that the first line starts with actual data, and not a column headear (very important)

	grade_col_ind (default=11) - int: the column index of 'Grade/10.00'. Please change this value if it appears differently on your moodle csv

	Output:

	</path/to/canvas_fl_name>_updated_<date>_with_<Lab/Quiz name>.csv - file: This is the file of <canvas_fl> merged with the new quiz grades from <moodle_fl> in canvas format--ready to upload after fixing the Manual entries
	''' 
	ids_by_username = {} # access ids by username, taken from the lab sections csv
	print('\n\nReading students in your lab section ...')
	with open(lab_sec_fl) as fin:
		for line in fin:
			line_split = line.split(',')
			ids_by_username[line_split[1].split('@')[0]] = line_split[0] 
	
	# Now that we have all the UDIDs based on udel username, we can accurately tell one student from another, and only process the grades for our lab sections 
	# Moodle accurately provides the udel username, but not student name or UDID
	# Canvas provides the udel username, but not the UDID, so this mapping is necessary	

	all_grades={}
	print('Reading Moodle submissions ...')
	max_moodle_grade = -1
	with open(moodle_fl) as fin:
		for line in fin:
			if 'Grade' in line: # first line. Get max moodle grade
				max_moodle_grade = float(line.strip().lower().split(',')[grade_col_ind].split('/')[1])	
			else:
				line_split=line.strip().lower().split(',')
				udel_username = line_split[3]
				grade = line_split[grade_col_ind]
				if grade == '-':
					grade = '0.0'
				if udel_username in ids_by_username.keys():
					all_grades[ids_by_username[udel_username]] = grade
	if max_moodle_grade < 0:
		raise ValueError("Max Moodle Grade not found! Ensure that \"Grade/<max grade>\" is in the column header of column " + grade_col_ind + ". If the column index is wrong, please pass the correct one to this function") 

	print("\n\nThe following students are in your lab sections, but have no Moodle submission. They will receive a 0 for now.")
	print("UDID,    Username")
	for uname in ids_by_username.keys():
		if ids_by_username[uname] not in all_grades.keys():
			print(str(ids_by_username[uname]) + ", " + str(uname))
			all_grades[ids_by_username[uname]] = '0.0'
	
	scoreFIN = csv.reader(open(canvas_fl)) 
	line1 = next(scoreFIN)
	poss_cols_to_edit = []
	for col in line1:
		if match("Quiz [0-9]", col)!=None or match("Lab [0-9]", col)!=None:
			poss_cols_to_edit.append(col)

	correct = False
	col_to_edit = -1
	while not correct:
		field_to_edit = str(input("\nPlease type the field you wish to edit (exactly).\nChoices are: " + str(poss_cols_to_edit[:]) + "\nEntry: ")) # This script is only for Quizzes and labs, so only show those cols
		try:
			col_to_edit = line1.index(field_to_edit)
			print("You have chosen to edit " + field_to_edit)
			correct = True
		except:
			print("\nIncorrect entry. Please make sure there are no typos. You can always copy and paste")


	print('Reading Canvas file ...') 
	print("\n\nThe following students are in your canvas lecture section, but were not found in " + lab_sec_fl + ". Please ignore if they are a TA or a test student")
	print("UDID,    Student Name")
	new_canvas_csv = [line1] # The matrix to write to the new csv file	
	mult = 1.0
	pts_poss_row = True
	for row in scoreFIN:
		if pts_poss_row: # Get the max canvas grade so we can make a multiplier for the diff
			max_canvas_grade = float(row[col_to_edit].strip())
			mult = max_canvas_grade / max_moodle_grade
			pts_poss_row = False
		else:
			udid = row[2].strip() # extract udid from canvas file line
			if udid in all_grades.keys(): # first check if in our lab section,  then check is in this current canvas section (because we have three different canvas pages for three different sections of the same class for some reason)
				row[col_to_edit] = str(float(all_grades[udid])*mult) # Edit the new grade in the correct place
			else:
				print(str(udid) + ", " + row[0].strip())
		new_canvas_csv.append(row)

	# Now write the new file to $PWD as "<old canvas file name>_update_<date>.csv"
	new_canvas_fl = canvas_fl.split('.')[0] + '_updated_' + strftime("%d-%m-%Y_%I%M%S") + '_with_' + field_to_edit.split('(')[0] + '.csv'
	new_canvas_writer = csv.writer(open(new_canvas_fl, 'w'), delimiter=',')
	for row in new_canvas_csv:
		new_canvas_writer.writerow(row)

	print("\nUpdated canvas csv written to: " + new_canvas_fl + "\n\n")


def moodle2canvas_groups(moodle_fl="moodle.csv", canvas_fl="grades.csv", lab_sec_fl="my_sections.csv", grade_col_ind=11, groups_fl="groups.csv"):
	'''
	moodle2canvas for partner/group assignements (i.e. labs)
	Args:

	moodle_fl (default="moodle.csv") - str: the input grades file in moodle format found on the quiz server under Results -> Grades. These should be restuls from one quiz

	canvas_fl (default="grades.csv") - str: the input grades file in canvas format. This shouold contain all grades from all students in that particular section
	
	lab_sec_fl (default="my_sections.csv") - str: a csv containing only YOUR lab sections with tho columns set up as: ID, Email. Note: this assumes that the first line starts with actual data, and not a column headear (very important)

	grade_col_ind (default=11) - int: the column index of 'Grade/10.00'. Please change this value if it appears differently on your moodle csv

	groups_fl (default=groups.csv) - str: a csv defining each group for the week. Each row should be a group, defined by a comma-separated list of each student's UD username

	Output:

	</path/to/canvas_fl_name>_updated_<date>_with_<Lab/Quiz name>.csv - file: This is the file of <canvas_fl> merged with the new quiz grades from <moodle_fl> in canvas format--ready to upload after fixing the Manual entries
	''' 
	ids_by_username = {} # access ids by username, taken from the lab sections csv
	print('\n\nReading students in your lab section ...')
	with open(lab_sec_fl) as fin:
		for line in fin:
			line_split = line.split(',')
			ids_by_username[line_split[1].split('@')[0]] = line_split[0] 
	
	# Now that we have all the UDIDs based on udel username, we can accurately tell one student from another, and only process the grades for our lab sections 
	# Moodle accurately provides the udel username, but not student name or UDID
	# Canvas provides the udel username, but not the UDID, so this mapping is necessary	

	

	all_grades={}
	print('Reading Moodle submissions ...')
	max_moodle_grade = -1
	with open(moodle_fl) as fin:
		for line in fin:
			if 'Grade' in line: # first line. Get max moodle grade
				max_moodle_grade = float(line.strip().lower().split(',')[grade_col_ind].split('/')[1])	
			else:
				line_split=line.strip().lower().split(',')
				udel_username = line_split[3]
				grade = line_split[grade_col_ind]
				if grade == '-':
					grade = '0.0'
				if udel_username in ids_by_username.keys():
					all_grades[ids_by_username[udel_username]] = grade
	if max_moodle_grade < 0:
		raise ValueError("Max Moodle Grade not found! Ensure that \"Grade/<max grade>\" is in the column header of column " + grade_col_ind + ". If the column index is wrong, please pass the correct one to this function") 

	print("Cross-checking groups with individual submissions...")
	groups = [] # nested list of groups
	with open(groups_fl) as fin:
		for line in fin:
			groups.append([s.strip() for s in line.strip().split(',')])

	print("\n\nThe following students are in your lab sections, but were not found in any group listed in " + groups_fl + ", and they do not have an individual Moodle submission. Please ensure that " + groups_fl + " is correct. They will receive a zero for now.")
	print("UDID,    Username")
	for uname in ids_by_username.keys():
		is_in_group_i = [uname in group for group in groups]
		has_submitted = ids_by_username[uname] in all_grades.keys()
		if not any(is_in_group_i) and not has_submitted:
			print(str(ids_by_username[uname]) + ", " + str(uname))
			all_grades[ids_by_username[uname]] = '0.0'
		elif any(is_in_group_i): # Student found, loop through the groups and assign their grades
			# Find max group submission grade
			group = groups[is_in_group_i.index(True)]
			max_group_grade = '0.0'
			for group_member_uname in group:
				if group_member_uname in ids_by_username.keys() and ids_by_username[group_member_uname] in all_grades.keys():
					if float(all_grades[ids_by_username[group_member_uname]]) > float(max_group_grade):
						max_group_grade = all_grades[ids_by_username[group_member_uname]]
			all_grades[ids_by_username[uname]] = max_group_grade	
		# Else they submitted individually
	
	scoreFIN = csv.reader(open(canvas_fl)) 
	line1 = next(scoreFIN)
	poss_cols_to_edit = []
	for col in line1:
		if match("Quiz [0-9]", col)!=None or match("Lab [0-9]", col)!=None:
			poss_cols_to_edit.append(col)

	correct = False
	col_to_edit = -1
	while not correct:
		field_to_edit = str(input("\nPlease type the field you wish to edit (exactly).\nChoices are: " + str(poss_cols_to_edit[:]) + "\nEntry: ")) # This script is only for Quizzes and labs, so only show those cols
		try:
			col_to_edit = line1.index(field_to_edit)
			print("You have chosen to edit " + field_to_edit)
			correct = True
		except:
			print("\nIncorrect entry. Please make sure there are no typos. You can always copy and paste")


	print('Reading Canvas file ...') 
	print("\n\nThe following students are in your canvas lecture section, but were not found in " + lab_sec_fl + ". Please ignore if they are a TA or a test student")
	print("UDID,    Student Name")
	new_canvas_csv = [line1] # The matrix to write to the new csv file	
	mult = 1.0
	pts_poss_row = True
	for row in scoreFIN:
		if pts_poss_row: # Get the max canvas grade so we can make a multiplier for the diff
			max_canvas_grade = float(row[col_to_edit].strip())
			mult = max_canvas_grade / max_moodle_grade
			pts_poss_row = False
		else:
			udid = row[2].strip() # extract udid from canvas file line
			if udid in all_grades.keys(): # first check if in our lab section,  then check is in this current canvas section (because we have three different canvas pages for three different sections of the same class for some reason)
				row[col_to_edit] = str(float(all_grades[udid])*mult) # Edit the new grade in the correct place
			else:
				print(str(udid) + ", " + row[0].strip())
		new_canvas_csv.append(row)

	# Now write the new file to $PWD as "<old canvas file name>_update_<date>.csv"
	new_canvas_fl = canvas_fl.split('.')[0] + '_updated_' + strftime("%d-%m-%Y_%I%M%S") + '_with_' + field_to_edit.split('(')[0] + '.csv'
	new_canvas_writer = csv.writer(open(new_canvas_fl, 'w'), delimiter=',')
	for row in new_canvas_csv:
		new_canvas_writer.writerow(row)

	print("\nUpdated canvas csv written to: " + new_canvas_fl + "\n\n")

# Main (gets run if you run this as a script and not as a library call)
if __name__ == '__main__':
	'''
	Run from the terminal as: 
	$ python moodle2canvas_style.py -mf <moodle file name>
	OR
	$ ./moodle2canvas_style.py -mf <moodle file name>
	if on linux (must have /usr/bin/env 
	'''

	from argparse import ArgumentParser
	parser = ArgumentParser()
	subparsers = parser.add_subparsers(dest='subparser') 

	# Default vals
	default_moodle_fl = 'moodle.csv'
	default_canvas_fl = 'grades.csv'
	default_lab_sec_fl = 'my_sections.csv'
	default_grade_col_ind = 11
	default_groups_fl = 'groups.csv'

	single_parser = subparsers.add_parser('single', help='Use this for single-person assignments (i.e. Quizzes). Use `./moodle2canvas.py single -h` for specific arguments.')
	group_parser = subparsers.add_parser('group', help='Use this for group assignments (i.e. Labs). Use `./moodle2canvas group -h for specific arguments.')

	# Both subparsers share these args
	for subparser in [single_parser, group_parser]:	
		subparser.add_argument('--moodle-fl','-m', dest='moodle_fl', nargs='?', default=default_moodle_fl, help='The input file in moodle format for the results of a quiz. Default is: ' + default_moodle_fl)
		subparser.add_argument('--canvas-fl','-c', dest='canvas_fl', nargs='?', default=default_canvas_fl, help='The input file of all grades in canvas format. This file will not be overwritten. Default is: ' + default_canvas_fl)

		subparser.add_argument('--lab-sec-fl','-l', dest='lab_sec_fl', nargs='?', default=default_lab_sec_fl, help='The input csv file of all your lab sections with only two columns of \'ID, Email\' (with no column headers). Default is: ' + default_lab_sec_fl)

		subparser.add_argument('--grade-col-ind','-i', dest='grade_col_ind', nargs='?', default=default_grade_col_ind, help="The column index of 'Grade/<max grade>'. Please change this value if it appears differently on your moodle csv. Default is: " + str(default_grade_col_ind), type=int)

	# group parser needs the groups csv file
	group_parser.add_argument('--groups-fl', '-g', dest='groups_fl', nargs='?', default=default_groups_fl, help='Groups csv file defining groups for this week. Each row should be a group defined by a comma-separated list of the student UD usernames (not email). Default is: ' + default_groups_fl) 

	args = parser.parse_args()
	if args.subparser == 'group':
		moodle2canvas_groups(args.moodle_fl, args.canvas_fl, args.lab_sec_fl, args.grade_col_ind, args.groups_fl)
	else:	
		moodle2canvas_single(args.moodle_fl, args.canvas_fl, args.lab_sec_fl, args.grade_col_ind)


