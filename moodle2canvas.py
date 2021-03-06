#!/usr/bin/env python3
import csv
import sys
from time import strftime
from re import match
import numpy as np

class bcolors:
    YELLOW = '\033[93m'
    GREEN = '\033[0;92m'
    RED = '\033[91m'
    ENDC = '\033[0m'

def csv_split(line):
    ret = []
    line_split = line.split(',')
    curr = ''
    quotes = ['"', "'"]
    for _part in line_split:
        part = _part.strip()
        if part != '':
            if part[0] not in quotes and curr == '':
                ret.append(part)
            elif part[0] in quotes:
                curr += part + ", "
            elif part[-1] in quotes:
                ret.append(curr + part)
            else:
                curr += part + ", "

    return ret

def moodle2canvas(moodle_fl="moodle.csv", canvas_fl="grades.csv", lab_sec_fl="my_sections.csv", 
         responses_fl="responses.csv", partner_col_ind=12, check_groups=False, max_moodle_grade=-1,
         style="vpl", grade_cutoff=None, add=False, lp=False):
    '''
    moodle2canvas for partner/group assignements (i.e. labs)
    Args:

    moodle_fl (default="moodle.csv") - str: the input grades file in moodle format found on the quiz server under Results -> Grades. This can be all sections appended together

    canvas_fl (default="grades.csv") - str: the input grades file in canvas format. This shouold contain all grades from all students in that particular section
    
    lab_sec_fl (default="my_sections.csv") - str: a csv containing only YOUR lab sections with tho columns set up as: ID, Email. Note: this assumes that the first line starts with actual data, and not a column headear (very important)

    responses_fl (default=responsess.csv) - str: The csv response file downloaded from Moodle. Can be all sections appended together. Only needed if check_groups is True
    
    partner_col_ind - the column index of the partner question in responses_fl

    max_moodle_grade - the max grade on Moodle. Used to determine a ratio between the max moodle grade and max Canvas grade. if -1, max grades are assumed to be the same between Canvas and Moodle.

    style - string "vpl" or "quiz". If vpl, the spreadsheet is assumed to be in VPL exported format: grades are summed from grade_col_ind to the second to last column, which contains download info.
                        if quiz, the spreadsheet is assumed to be in coderunner/essay format, where the total grade is in column grade_col_ind, and no summation is performed.

    add - bool: if True, add the new grades to the current Canvas grade. Useful for combining multiple project parts into one canvas assignment when kids worked with different partners.

    lp - bool: If True, partners are logged in csv file in the canvas csv directory under "partners.csv"

    Output:

    </path/to/canvas_fl_name>_updated_<date>_with_<Lab/Quiz name>.csv - file: This is the file of <canvas_fl> merged with the new quiz grades from <moodle_fl> in canvas format--ready to upload after fixing the Manual entries
    ''' 

    style = style.lower()
    assert style=='vpl' or style=='quiz', "Unrecognized style: '%s'" % style

    grade_col_ind = 7 if style=='vpl' else 11

    if grade_cutoff is not None:
        if style == 'vpl':
            gc_dict = {}
            for cutoffs in grade_cutoff.split(';'):
                cutoff, ind = cutoffs.split(',')
                cutoff = float(cutoff.strip())
                ind = int(ind.strip())
                gc_dict[ind] = cutoff
            grade_cutoff = gc_dict
        else:
            grade_cutoff = float(grade_cutoff.strip())

    ids_by_username = {} # access ids by username, taken from the lab sections csv
    name_by_username = {} # access name by username, taken from the lab sections csv
    username_by_id = {}
    print(bcolors.GREEN, '\n\nReading students in your section(s) ...', bcolors.ENDC)
    with open(lab_sec_fl) as fin:
        for line in fin:
            line_split = csv_split(line)
            print(line_split)
            ids_by_username[line_split[1].split('@')[0]] = line_split[0] 
            name_by_username[line_split[1].split('@')[0]] = line_split[2] 
            username_by_id[line_split[0]] = line_split[1].split('@')[0]
    # Now that we have all the UDIDs based on udel username, we can accurately tell one student from another, and only process the grades for our lab sections 
    # Moodle accurately provides the udel username, but not student name or UDID
    # Canvas provides the udel username, but not the UDID, so this mapping is necessary    

    

    all_grades={}
    print(bcolors.GREEN, 'Reading Moodle submissions ...', bcolors.ENDC)
    first_line = True
    with open(moodle_fl) as fin:
        for line in fin:
            if first_line:
                first_line = False # skip
            else:
                line_split = line.strip().lower().split(',')
                if style.lower() == "vpl":
                    udel_username = line_split[0] # Get udel username 
                elif style.lower() == "quiz":
                    udel_username = line_split[3]
                else:
                    raise ValueError("Unkown style: " + style.lower())

                if udel_username in ids_by_username.keys():
                    if style.lower() == "vpl":
                        grade_list = []
                        n_parts = len(line_split[grade_col_ind:-1])
                        for i in range(len(line_split[grade_col_ind:-1])): # Skip last col. It's junk with no grades
                            part_grade = line_split[grade_col_ind:-1][i]
                            if part_grade.strip() != '-':# if Part completed.
                                grade_ = float(part_grade.strip())
                                if grade_cutoff is not None and i in grade_cutoff.keys():
                                    grade_ = min(grade_cutoff[i], grade_)
                                grade_list.append(grade_)
                            else:
                                grade_list.append(0)
                        grade = np.array(grade_list)
                    else:
                        grade_ = line_split[grade_col_ind].strip() # Just a string for this style
                        if grade_ == '-':
                            grade = '0'
                        else:
                            grade = grade_ if grade_cutoff is None else str(min(grade_cutoff, float(grade_)))
    
                    if ids_by_username[udel_username] in all_grades.keys(): # check for multiple submissions. Want the max
                        if style == 'quiz':
                            if float(all_grades[ids_by_username[udel_username]]) < float(grade):    
                                all_grades[ids_by_username[udel_username]] = grade
                        else:
                            # Element-wise max for each part of the lab
                            all_grades[ids_by_username[udel_username]] = np.maximum(all_grades[ids_by_username[udel_username]], grade)
                    else:
                        all_grades[ids_by_username[udel_username]] = grade

    if check_groups:
        # TODO Fix this part for new format (with emails or NONE)
        print(bcolors.GREEN, "Cross-checking groups with individual submissions...", bcolors.ENDC)
        groups = [] # nested list of groups
        with open(responses_fl) as fin:
            for line in fin:
                line_split = line.strip().split(',')
                if not line_split[0].strip() == "Surname":
                    group = [line_split[3].strip()] # Username of submitter
                    partners = line_split[partner_col_ind].strip().strip('\"').split(';')
                    for partner in partners:
                        if partner.strip().endswith('@udel.edu'): # Make sure its not random text
                            partner_uname = partner.strip().split('@')[0].lower()
                            if partner_uname in ids_by_username.keys():
                                group.append(partner_uname) # Append multiple partners if there are any
                    groups.append(group)
        groups = np.array(groups) # Do this so we can use logical indexing later

        missing_students_log_fl_name = canvas_fl.split('.')[0] + "_missing_students.log"

        if lp:

            ws = "Submitter, Partner(s)\n"
            for group in groups:
                if group[0] in name_by_username.keys():
                    ws += name_by_username[group[0]] + ','
                    if len(group) == 1:
                        ws += 'None'
                    else:
                        for partner in group[1:]:
                            ws += name_by_username[partner]
                    ws += ",\n"

            with open(canvas_fl.split('.')[0] + "_partners.csv", 'w') as lpf:
                lpf.write(ws)

        log_fl = open(missing_students_log_fl_name, 'w')
        msg = "\n\nthe following students are in your lab sections, but were not found in any group listed in " + responses_fl + ", and they do not have an individual moodle submission. they will receive a zero for now.\nUDID,    Username\n"
        print(bcolors.YELLOW, msg, bcolors.ENDC)
        log_fl.write(msg)
        for uname in ids_by_username.keys():
            is_in_group_i = np.array([uname in group for group in groups])
            has_submitted = ids_by_username[uname] in all_grades.keys()
            if not any(is_in_group_i) and not has_submitted:
                log_fl.write(str(ids_by_username[uname]) + ", " + str(uname) + "\n")
                print(str(ids_by_username[uname]) + ", " + str(uname))
                all_grades[ids_by_username[uname]] = '0.0'
            elif any(is_in_group_i): # Student found, loop through the groups and assign their grades
                # Find max group submission grade
                students_groups = groups[is_in_group_i] # May return multiple groups/single submissions, we want the max for each student (i.e. if they submitted alone after a group member bailed)
                max_group_grade = '0.0' if style=='quiz' else np.zeros((n_parts))
                for group in students_groups:
                    for group_member_uname in group:
                        if group_member_uname in ids_by_username.keys() and ids_by_username[group_member_uname] in all_grades.keys():
                            if style == 'quiz':  
                                if float(all_grades[ids_by_username[group_member_uname]]) > float(max_group_grade):
                                
                                    max_group_grade = all_grades[ids_by_username[group_member_uname]]
                            else:
                                # element-wise max across parts of the lab in case partners
                                # took turns using different accounts
                                max_group_grade = np.maximum(max_group_grade, all_grades[ids_by_username[group_member_uname]])

                all_grades[ids_by_username[uname]] = max_group_grade    
            # Else they submitted individually
    else: # single person activity, dont look for groups
        msg = "\n\nThe following students are in your lab sections, but have no Moodle submission. They will receive a 0 for now.\nUDID,    Username\n"
        missing_students_log_fl_name = canvas_fl.split('.')[0] + "_missing_students.log"
        log_fl = open(missing_students_log_fl_name, 'w')
        print(bcolors.YELLOW, msg, bcolors.ENDC)
        log_fl.write(msg)
        for uname in ids_by_username.keys():
            if ids_by_username[uname] not in all_grades.keys():
                log_fl.write(str(ids_by_username[uname]) + ", " + str(uname) + "\n")
                print(str(ids_by_username[uname]) + ", " + str(uname))
                all_grades[ids_by_username[uname]] = '0.0' if style=='quiz' else np.zeros((n_parts))
    scoreFIN = csv.reader(open(canvas_fl)) 
    line1 = next(scoreFIN)
    poss_cols_to_edit = {}
    poss_cols_to_edit_pretty = []
    idx = 0
    counter = 0
    for col in line1:
        if match("Quiz [0-9]", col) is not None or match("Lab [0-9]", col) is not None \
                or match(".*[p,P]roject .*[0-9]", col) is not None:
            poss_cols_to_edit_pretty.append(col.split(' (')[0])
            poss_cols_to_edit[str(idx)] = counter
            idx += 1
        counter += 1

    correct = False
    col_to_edit = -1
    while not correct:
        print("\nPlease type the number corresponding to the assignment you are uploading grades for\n")
        [print(str(i)+':', poss_cols_to_edit_pretty[i]) for i in range(len(poss_cols_to_edit_pretty))]
        field_idx_to_edit = str(input("\nEntry (number): ")) # This script is only for Quizzes and labs, so only show those cols
        col_to_edit = poss_cols_to_edit.get(field_idx_to_edit)
        if col_to_edit is not None:
            field_to_edit_pretty = poss_cols_to_edit_pretty[int(field_idx_to_edit)]
            print(bcolors.GREEN, "You have chosen to edit " + \
                     field_to_edit_pretty, bcolors.ENDC)
            correct = True
        else:
            print(bcolors.RED, "\nIncorrect entry. Please make sure the number is listed", bcolors.ENDC)


    print(bcolors.GREEN, 'Reading Canvas file ...', bcolors.ENDC) 
    print(bcolors.YELLOW, "\n\nThe following students are in your canvas lecture section, but were not found in " + lab_sec_fl + ". Please ignore if they are a TA or a test student", bcolors.ENDC)
    print("UDID,    Student Name")
    log_fl.write("\n\nThe following students are in your canvas lecture section, but were not found in " + lab_sec_fl + ". Please ignore if they are a TA or a test student.\nUDID,    Student Name")
    new_canvas_csv = [line1] # The matrix to write to the new csv file    
    pts_poss_row = False 
    while not pts_poss_row: # Find the row with the max number of canvas points
        line = next(scoreFIN) # go to next row
        new_canvas_csv.append(line)
        print(line[0])
        if "Points Possible" in line[0].strip():
            pts_poss_row = True
            if max_moodle_grade > -1:
                max_canvas_grade = float(line[col_to_edit].strip()) # Adjust the grade according to the max grade ratio
                mult = max_canvas_grade / max_moodle_grade
            else:
                mult = 1

    for row in scoreFIN:
        udid = row[2].strip() # extract udid from canvas file line
        if udid in all_grades.keys(): # first check if in our lab section,  then check is in this current canvas section (because we have three different canvas pages for three different sections of the same class for some reason)
            if style == 'quiz':
                new_grade = float(all_grades[udid])*mult # Edit the new grade in the correct place
            else:
                new_grade = np.sum(all_grades[udid]) * mult # Edit the new grade in the correct place

            row[col_to_edit] = str(new_grade) if not add else str(float(row[col_to_edit]) + new_grade)

        else:
            print(str(udid) + ", " + row[0].strip())
            log_fl.write(str(udid) + ", " + row[0].strip() + "\n")
        new_canvas_csv.append(row)

    # Now write the new file to $PWD as "<old canvas file name>_update_<date>.csv"
    new_canvas_fl = canvas_fl.split('.')[0] + '_updated_' + \
            '_with_' + field_to_edit_pretty.replace(' ','') + '.csv'
    new_canvas_writer = csv.writer(open(new_canvas_fl, 'w'), delimiter=',')
    for row in new_canvas_csv:
        new_canvas_writer.writerow(row)

    print(bcolors.GREEN, "\nUpdated canvas csv written to: " + new_canvas_fl + "\n\n", bcolors.ENDC)
    print(bcolors.YELLOW, "All missing students written to: " + missing_students_log_fl_name, bcolors.ENDC)
# Main (gets run if you run this as a script and not as a library call)
if __name__ == '__main__':
    '''
    Run from the terminal as: 
    $ python moodle2canvas_style.py -mf <moodle file name>
    OR
    $ ./moodle2canvas_style.py -mf <moodle file name>
    if on linux (must have /usr/bin/env)
    '''

    from argparse import ArgumentParser
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest='subparser') 

    # Default vals
    default_moodle_fl = 'moodle.csv'
    default_canvas_fl = 'grades.csv'
    default_lab_sec_fl = 'my_sections.csv'
    default_grade_col_ind = 7
    default_response_fl = 'responses.csv'

    single_parser = subparsers.add_parser('single', help='Use this for single-person assignments (i.e. Quizzes). Use `./moodle2canvas.py single -h` for specific arguments.')
    group_parser = subparsers.add_parser('group', help='Use this for group assignments (i.e. Labs). Use `./moodle2canvas group -h for specific arguments.')

    # Both subparsers share these args
    for subparser in [single_parser, group_parser]:    
        subparser.add_argument('--moodle-fl','-m', dest='moodle_fl', nargs='?', default=default_moodle_fl, help='The input file in moodle format for the results of a quiz if style=="quiz" or the results of exporting multiple VPL labs if stye=="vpl". Default is: ' + default_moodle_fl)

        subparser.add_argument('--canvas-fl','-c', dest='canvas_fl', nargs='?', default=default_canvas_fl, help='The input file of all grades in canvas format. This file will not be overwritten. Default is: ' + default_canvas_fl)

        subparser.add_argument('--lab-sec-fl','-l', dest='lab_sec_fl', nargs='?', default=default_lab_sec_fl, help='The input csv file of all your lab/lecture sections with first three columns of \'ID, Email, Name\' (with no column headers). Other columns are ignored if they exist. Default is: ' + default_lab_sec_fl)

        subparser.add_argument('--response-fl', '-r', dest='response_fl', nargs='?', default=default_response_fl, help='The repsonse file downloaded from Moodle WITH EVERY COLUMN AFTER QUESTION 1 REMOVED. Can have multiple sections appended. Default is: ' + default_response_fl) 
        
        subparser.add_argument('--style', '-s', dest='style', nargs='?', default="vpl", help='"vpl" or "quiz". If vpl, the spreadsheet is assumed to be in VPL exported format: grades are summed from grade_col_ind to the second to last column, which contains download info.if quiz, the spreadsheet is assumed to be in coderunner/essay format, where the total grade is in column grade_col_ind, and no summation is performed. Default is vpl') 

        subparser.add_argument('--max-moodle-grade', '-g', dest='max_moodle_grade', nargs='?', default=-1, help='Max grade on Moodle. If left to default, grade scales on Moodle are assumed to be the same as Canvas', type=float) 

        subparser.add_argument('--grade-cutoff', '-x', dest='grade_cutoff', nargs='?', default=None, help='Max grade (in Moodle scale) for the part(s) specified. Format is "(max grade 1), (offset from first grade column 1); (max grade 2), (offset from first grade column 2)..." if style==vpl or "max grade" if style==quiz') 
        
        subparser.add_argument('--add', '-a', dest='add', nargs='?', default=False, type=bool, help='If true, grades are added to current Canvas grades for each student. Useful for combining multiplt project parts into one canvas assignment when partners may be different for different parts.') 

        subparser.add_argument('--log-partners', '-p', dest='log_partners', nargs='?', default=False, type=bool, help='If true, partners are logged in a csv in the Canvas csv directory under the name partners.csv') 
    
    args = parser.parse_args()
    main_check_groups = False
    if args.subparser == 'group':
        main_check_groups = True    
    moodle2canvas(args.moodle_fl, args.canvas_fl, args.lab_sec_fl, args.response_fl,
         check_groups=main_check_groups, max_moodle_grade=args.max_moodle_grade,
         style=args.style, grade_cutoff=args.grade_cutoff, add=args.add, lp=args.log_partners)


