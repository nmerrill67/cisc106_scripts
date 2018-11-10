#!/usr/bin/env python3
import sys, os
    

def vpl_submissions2spreadsheet(input_dir, output_fl, lab_fl_name, lab_sec_fl , partner_col_ind):
    
    ids_by_username = {} # access ids by username, taken from the lab sections csv
    username_by_last_name = {}
    email_by_id = {}
    with open(lab_sec_fl) as fin:
        for line in fin:
            line_split = line.split(',')
            ids_by_username[line_split[1].split('@')[0]] = line_split[0] 
            email_by_id[line_split[0]] = line_split[1]
            # For multiple part last names take the first part only
            username_by_last_name[line_split[2].split()[0].split('-')[0].strip('"').lower()] = line_split[1].split('@')[0]   

    flstr = "Surname, First Name, ID number, Username, Institution, Department, Email address, State, Started on, Completed, Time taken, Grade, Response 1\n"

    for dir_ in os.listdir(input_dir):
        path = os.path.join(input_dir, dir_)
        name = dir_.split()
        last = name[0].split('-')[0]
        first = name[-2]
        if last.lower() in username_by_last_name.keys():
            ss_line = last + ", " + first + ", , " + username_by_last_name[last.lower()] + ", , , , , , , , ,"
            newest = ""
            for sub_dir in os.listdir(path): # Get newest submission dir
                if not sub_dir.endswith('.ceg'):
                    newest = max(newest, sub_dir) # The dirs are dates. This works just fine
            if newest != "": # Else they have no submissions at all
                full_path = os.path.join(path, newest, lab_fl_name)
                with open(full_path) as fp:
                    lines = fp.read().split('\n')[:-1]
                partner = '-'
                last_name = None
                for line in lines:
                    if 'Partner Name:' in line:
                        name = line.split(':')[1].strip()
                        if name != '':
                            split = name.split()
                            if len(split) > 1:
                                last_name = split[-1]                        

                    elif 'Partner UDID:' in line:
                        partner_ = line.split(':')[1].strip() 
                        if len(partner_) == 9 and partner_ in email_by_id.keys(): # Check its valid      
                            partner = email_by_id[partner_]
                            break
                        else: # Try to get it from the name if the kids can't follow directions
                            if last_name is not None:
                                uname = username_by_last_name.get(last_name.lower())
                                if uname is not None:
                                    partner = uname + "@udel.edu"
                ss_line += partner + "\n"
                flstr += ss_line
                
        else:
            print("Student", name[:-1], "not found in section") 
    with open(output_fl, 'w') as fp:
        fp.write(flstr)

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()

    # Default vals
    default_partner_col_ind = 12
    default_lab_sec_fl = 'my_sections.csv'

    parser.add_argument('input_dir')
    parser.add_argument('output_fl')
    parser.add_argument('lab_fl_name', help="Name of the lab file. Example: lab2c.py")

    parser.add_argument('--lab-sec-fl', '-l', dest='lab_sec_fl', nargs='?', default=default_lab_sec_fl, help='The input csv file of all your lab sections with only two columns of \'ID, Email\' (with no column headers). Default is: ' + default_lab_sec_fl)

    parser.add_argument('--partner-col-ind','-i', dest='partner_col_ind', nargs='?', default=default_partner_col_ind, help="The column index of the partner response in the outputted spreadsheet", type=int)

    args = parser.parse_args()
    vpl_submissions2spreadsheet(args.input_dir, args.output_fl, args.lab_fl_name, args.lab_sec_fl , args.partner_col_ind)
    

