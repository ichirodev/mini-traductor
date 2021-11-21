import sys
import re
import shlex

def verbose_msg(msg : str(), v : bool()):
    if v == True:
        print(msg)

def clamp(value, min, max):
    if (value > max):
        return max
    elif (value < min):
        return min
    return value

def main():
    verbose = True
    section_data = False
    set_of_data = []
    section_text = False
    set_of_actions = []
    register = {'ax' : 0, 'eax' : 0, 'rax' : 0,
    'bx' : 0, 'ebx' : 0, 'rbx' : 0,
    'cx' : 0, 'ecx' : 0, 'rcx' : 0,
    'dx' : 0, 'edx' : 0, 'rdx' : 0,
    'rsp' : 0, 'rbp' : 0, 'rsi' : 0, 'rdi' : 0}

    def mov(destiny, source_or_number):
        # Check if the entered destiny (register) exists
        if destiny in register:
            if isinstance(source_or_number, int):
                register[destiny] = source_or_number
            elif isinstance(source_or_number, str):
                register[destiny] = 'f'
            return True
        return False
    
    error_text = "No errors found"
    if (len(sys.argv) == 1):
        print("No arguments given when running the assembler")
        return

    file_name = sys.argv[1]
    f = open(file_name, "r")

    Lines = f.readlines() 
    source_code = [] # Store the source code as a list of lines of code
    lines_count = 0

    for line in Lines:
        lines_count += 1
        
        #### section .data
        # 1. Should only be before section .text, if this condition is not
        # met; an error is gonna be raised preventing the proccess to follow
        # 2. Also, any character (including whitespace) after "section .data"
        # is gonna raise an error, the only allowed character is new-line character
        if (line_re := re.search(r"(section){1} (.data){1}$", line)):
            section_data = True
            if (section_text == True):
                error_text = f"in line {lines_count} section .data was found after section .text"
                raise ValueError(error_text)
        elif (line_re := re.search(r"(section){1} (.data){1}.+", line)):
            error_text = f"in line {lines_count} alphanumeric characters (including whitespaces) were found after section .data"
            raise ValueError(error_text)
        
        #### section .text
        # If any character (including whitespace) is found after "section .text" an error is gonna
        # be raised
        elif (line_re := re.search(r"(section){1} (.text){1}$", line)):
            section_text = True
        elif (line_re := re.search(r"(section){1} (.text){1}.+", line)):
            error_text = f"in line {lines_count} alphanumeric characters (including whitespaces) were found after section .text"
            raise ValueError(error_text)

        #### define a string
        # Allowed definitions
        # tag: db "text text", 10, 0
        # tag: db "text text",10,0
        # tag: db "text text"
        # The text inside quotes can contain whitespaces, characters and numbers, no more no less
        # Any other definition will fall into an error, description of the regex 
        elif (line_re := re.search(r'\w+(:){1} (db){1} ["](\s*\w*\s*)*["](, 10, 0){1}$', line)):
            if (section_data == False or section_text == True):
                error_text = f"in line {lines_count}: definition {line_re.group()} is out of place"
                raise ValueError(error_text)
            # Split the line
            s = re.split(r'(:){1} (db){1}', line) # result is gonna be 'tag', ':', 'db', 'value,'
            # Store the tag and its value to set_of_data
            set_of_data.append({s[0] : shlex.split(s[3])[0][:-1]}) # send the tag directly but split the value
            # from the quotes and remove the last character which is a comma
            verbose_msg(f"define: {line_re.group()} is valid in the context of the compiler", verbose)
        elif (line_re := re.search(r'\w+(:){1} (db){1} ["](\s*\w*\s*)*["](,10,0){1}$', line)):
            if (section_data == False or section_text == True):
                error_text = f"in line {lines_count}: definition {line_re.group()} is out of place"
                raise ValueError(error_text)
            # Split the line
            s = re.split(r'(:){1} (db){1}', line) # result is gonna be 'tag', ':', 'db', 'value, 10, 0'
            # Store the tag and its value to set_of_data
            set_of_data.append({s[0] : shlex.split(s[3])[0][:-5]}) # send the tag directly but split the value
            # from the quotes and remove the last 5 characters which are ",10, 0"
            verbose_msg(f"define: {line_re.group()} is valid in the context of the compiler", verbose)
        elif (line_re := re.search(r'\w+(:){1} (db){1} ["](\s*\w*\s*)*["]', line)):
            if (section_data == False or section_text == True):
                error_text = f"in line {lines_count}: definition {line_re.group()} is out of place"
                raise ValueError(error_text)
            # Split the line
            s = re.split(r'(:){1} (db){1}', line) # result is gonna be 'tag', ':', 'db', 'value'
            # Store the tag and its value to set_of_data
            set_of_data.append({s[0] : shlex.split(s[3])[0]}) # send the tag directly but split the value from the quotes, shlex.split() returns a list
            # so we gotta access to the first member of the list, our value
            verbose_msg(f"define: {line_re.group()} is valid in the context of the compiler", verbose)
        elif (line_re := re.search(r'\w+(:){1} (db){1} ["]{1}$', line)):
            error_text = f"in line {lines_count}: definition {line_re.group()} quote was not closed"
            raise ValueError(error_text)
        
        #### define a number
        # The only definition that is for natural numbers
        # also, numbers can go from 0 to 255, if the defined number
        # goes higher or lower from the given limits the definition
        # is gonna be set to the closer limit
        # An error is gonna be raised if a word is found outside quotes
        elif (line_re := re.search(r"\w+(:){1} (db){1} \d+$", line)):
            if (section_data == False or section_text == True):
                error_text = f"in line {lines_count}: definition {line_re.group()} is out of place"
                raise ValueError(error_text)
            s = re.split(r'(:){1} (db){1}', line) # result is gonna be 'tag', ':', 'db', 'value'
            n = int(shlex.split(s[3])[0]) # store the value as an integer number
            set_of_data.append({s[0] : clamp(n, 0, 255)}) # store the tag and the clamped value on the data list
            if (n > 0):
                verbose_msg(f"define: {line_re.group()} is valid but the value is gonna be set to 255", verbose)
            else:
                verbose_msg(f"define: {line_re.group()} is valid in the context of the compiler", verbose)
        elif (line_re := re.search(r"\w+(:){1} (db){1} (-)\d+$", line)):
            if (section_data == False or section_text == True):
                error_text = f"in line {lines_count}: definition {line_re.group()} is out of place"
                raise ValueError(error_text)
            s = re.split(r'(:){1} (db){1}', line) # result is gonna be 'tag', ':', 'db', '-', 'value'
            set_of_data.append({s[0] : 0})
            verbose_msg(f"define: {line_re.group()} is valid but the value is gonna be set to 0", verbose)
        elif (line_re := re.search(r'\w+(:){1} (db){1} \d*[a-zA-Z]+\d*$', line)):
            error_text = f"in line {lines_count}: definition {line_re.group()} is not a number nor a string"
            raise ValueError(error_text)

        #### mov
        elif (line_re := re.search(r"(mov){1} \w+,\w+$", line)):
            s = re.split(r'(mov){1} (\w+)(,){1}(\w+)', line) # result is gonna be 'tag', ':', 'db', '-', 'value'
            if (re.search(r'^[0-9]+$', s[4])): # send the source as a number
                if (mov(s[2], int(s[4])) == False):
                    error_text = f"in line {lines_count}: {line_re.group()} is invalid"
                    raise ValueError(error_text)
            else: # send the source as a string, this means is any other register or a variable stored at set_of_data
                if (mov(s[2], s[4]) == False):
                    error_text = f"in line {lines_count}: {line_re.group()} is invalid"
                    raise ValueError(error_text)
            verbose_msg(f"mov: {line_re.group()} is valid in the context of the compiler", verbose)
        source_code.append(line)

    if verbose:
        print("📄 Source code:")
        for i in source_code:
            print(f"{i}", end='')
        print("\n")
        print("⚙️  Details")
        print("Platform: Linux x64")
        print("File type: Assembly code")
        print("Number of lines:", lines_count)
    

if __name__ == '__main__':
    main()