#!/usr/bin/env python3

import os
#Note:
# Step 0) Place roster files into pwd
# Step 1) Login to quiz server and go to Administration Panel->Responses
# Step 2) Update the following code to reflect the question number of the question to be reviewed.
# Step 3) Run the following code in console:
"""
var question_number = "2" //MODIFY THIS LINE ONLY!
var cusid_ele = document.getElementsByClassName('reviewlink');
for (var i = 0; i < cusid_ele.length; ++i) {
    var student_html = cusid_ele[i]; 
    console.log(student_html.parentElement.getElementsByTagName("a")[0].innerHTML + "#!#"+ student_html.parentElement.parentElement.getElementsByTagName("td")[4].innerHTML + "#!#" + student_html.href.replace("review.php","comment.php") + "&slot=" + question_number);
}
"""
# Step 4) Right click the console and save as submissions.log, update this directory
# Step 5) Run this python script. The generated files on based per lab section. Open the HTML files in your web browser

def main():
    f = open("submissions.log")
    lines = list(filter(lambda line: "#!#http://" in line,f.readlines()))
    f.close()
    students = [line.strip().split("#!#") for line in lines]
    sections = [filename for filename in os.listdir() if filename.endswith("L.csv")]
    print('Detected lab section files:')
    print(sections)

    for section_filename in sections:
        f = open(section_filename,"r")
        section = f.read()
        f.close()
        f= open("submissions_" + section_filename.replace(" ","_").replace(".csv", ".html"), "w")
        f.write("<!DOCTYPE html>\n<html>\n<body>\n")
        f.write("\n".join(["<a href=\"" + student[-1] + "\"" + ">" + " ".join(student[0:2]) + "</a><br/>" \
                           for student in students if student[1] in section]))

        f.write("</body>\n</html>")
        f.close()

if __name__ == '__main__':        
	main()

