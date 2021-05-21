FILE = "Full_Project_Reportback_1Ver.html"

with open(FILE, 'r') as html_file:
    content = html_file.read()

# Get rid off prompts and source code
content = content.replace("div.input_area {","div.input_area {\n\tdisplay: none;")
content = content.replace(".prompt {",".prompt {\n\tdisplay: none;")

out_file = "Full_Project_Reportback_1Ver_nocode.html"
f = open(out_file, 'w')
f.write(content)
f.close()