import sys
import re
import shlex
import subprocess


# of = {'o': chr, 'e': chr, 'linux64': chr, 'dump': chr}
# object_settings = [of['e'](51*2)+of['o'](11+(base-2)*3)+of['e'](int('6C',16))+of['linux64'](int('146',8))]
# write_path = of['dump'](base+78)+of['e'](base+65)+of['o'](base+83)+of['o'](base+77)

def verbose_msg(msg: str(), v: bool()):
    if v:
        print(msg)


def clamp(value, min, max):
    if value > max:
        return max
    elif value < min:
        return min
    return value


def main():
    global_name = None
    verbose = False
    section_data = False
    set_of_data = {}
    section_text = False
    set_of_actions = []
    register = {'ax': 0, 'eax': 0, 'rax': 0,
                'bx': 0, 'ebx': 0, 'rbx': 0,
                'cx': 0, 'ecx': 0, 'rcx': 0,
                'dx': 0, 'edx': 0, 'rdx': 0,
                'rsp': 0, 'rbp': 0, 'rsi': 0, 'rdi': 0}
    register_original_len = len(register)

    def check_registers():
        '''
        check the number of registers
        ---
        makes a fast check if the registers haven't been modified, during the whole process registers should never change other than
        its values, so, if the length of the dictionary that stores the registers changes during the running of the program this will case
        a returning value of False, which will continuously raise an Error
        '''
        if register_original_len != len(register):
            return False
        return True

    def mov(destiny, source_or_number):
        '''
        mov instruction
        ---
        moves a number/string source to a register/variable destiny, the source can also be a register or a variable
        it returns True when:
            An integer/string coming from a variable or a register has been moved to a variable or register
        on any other case it will return False, most common errors that cause returning false are:
            Trying to use other types of data such as float or lists
            Not sending one or both parameters
        '''
        if destiny in set_of_data:
            if isinstance(source_or_number, int):
                set_of_data[destiny] = source_or_number
                return True
            elif isinstance(source_or_number, str):
                if source_or_number in register:
                    set_of_data[destiny] = register[source_or_number]
                    return True
                elif source_or_number in set_of_data:
                    set_of_data[destiny] = set_of_data[source_or_number]
                    return True
                else:
                    return False
        if destiny in register:
            if isinstance(source_or_number, int):
                register[destiny] = source_or_number
                return True
            elif isinstance(source_or_number, str):
                if source_or_number in register:
                    register[destiny] = register[source_or_number]
                    return True
                elif source_or_number in set_of_data:
                    register[destiny] = set_of_data[source_or_number]
                    return True
                else:
                    return False
        return False

    def add(destiny, source_or_number):
        temp_number = 0
        if destiny in set_of_data:
            if isinstance(source_or_number, int):
                temp_number = set_of_data[destiny] + source_or_number
                set_of_data[destiny] = temp_number
                return True
            elif isinstance(source_or_number, str):
                if source_or_number in register:
                    temp_number = set_of_data[destiny] + register[source_or_number]
                    set_of_data[destiny] = temp_number
                    return True
                elif source_or_number in set_of_data:
                    temp_number = set_of_data[destiny] + set_of_data[source_or_number]
                    set_of_data[destiny] = temp_number
                    return True
                else:
                    return False
        if destiny in register:
            if isinstance(source_or_number, int):
                temp_number = register[destiny] + source_or_number
                register[destiny] = temp_number
                return True
            elif isinstance(source_or_number, str):
                if source_or_number in register:
                    temp_number = register[destiny] + register[source_or_number]
                    register[destiny] = temp_number
                    return True
                elif source_or_number in set_of_data:
                    temp_number = register[destiny] + set_of_data[source_or_number]
                    register[destiny] = temp_number
                    return True
                else:
                    return False
        return False

    def sub(destiny, source_or_number):
        temp_number = 0
        if destiny in set_of_data:
            if isinstance(source_or_number, int):
                temp_number = set_of_data[destiny] - source_or_number
                set_of_data[destiny] = temp_number
                return True
            elif isinstance(source_or_number, str):
                if source_or_number in register:
                    temp_number = set_of_data[destiny] - register[source_or_number]
                    set_of_data[destiny] = temp_number
                    return True
                elif source_or_number in set_of_data:
                    temp_number = set_of_data[destiny] - set_of_data[source_or_number]
                    set_of_data[destiny] = temp_number
                    return True
                else:
                    return False
        if destiny in register:
            if isinstance(source_or_number, int):
                temp_number = register[destiny] - source_or_number
                register[destiny] = temp_number
                return True
            elif isinstance(source_or_number, str):
                if source_or_number in register:
                    temp_number = register[destiny] - register[source_or_number]
                    register[destiny] = temp_number
                    return True
                elif source_or_number in set_of_data:
                    temp_number = register[destiny] - set_of_data[source_or_number]
                    register[destiny] = temp_number
                    return True
                else:
                    return False
        return False

    def div(destiny, source_or_number):
        temp_number = 0
        remainder_number = 0
        if destiny in set_of_data:
            if isinstance(source_or_number, int):
                temp_number = int(set_of_data[destiny] / source_or_number)
                remainder_number = int(set_of_data[destiny] % source_or_number)
                set_of_data[destiny] = temp_number
                register['rdx'] = remainder_number
                return True
            elif isinstance(source_or_number, str):
                if source_or_number in register:
                    temp_number = int(set_of_data[destiny] / register[source_or_number])
                    remainder_number = int(set_of_data[destiny] % register[source_or_number])
                    set_of_data[destiny] = temp_number
                    register['rdx'] = remainder_number
                    return True
                elif source_or_number in set_of_data:
                    temp_number = int(set_of_data[destiny] / set_of_data[source_or_number])
                    remainder_number = int(set_of_data[destiny] % set_of_data[source_or_number])
                    set_of_data[destiny] = temp_number
                    register['rdx'] = remainder_number
                    return True
                else:
                    return False
        if destiny in register:
            if isinstance(source_or_number, int):
                temp_number = int(register[destiny] / source_or_number)
                remainder_number = int(register[destiny] % source_or_number)
                register[destiny] = temp_number
                register['rdx'] = remainder_number
                return True
            elif isinstance(source_or_number, str):
                if source_or_number in register:
                    temp_number = int(register[destiny] / register[source_or_number])
                    remainder_number = int(register[destiny] % register[source_or_number])
                    register[destiny] = temp_number
                    register['rdx'] = remainder_number
                    return True
                elif source_or_number in set_of_data:
                    temp_number = int(register[destiny] / set_of_data[source_or_number])
                    remainder_number = int(register[destiny] % set_of_data[source_or_number])
                    register[destiny] = temp_number
                    register['rdx'] = remainder_number
                    return True
                else:
                    return False
        return False

    ### mul
    def mul(source):
        temp_number = 0
        if isinstance(source, str):
            if source in register:
                temp_number = int(register['rax']) * int(register[source])
            elif source in set_of_data:
                temp_number = int(register['rax']) * int(set_of_data[source])
            else:
                return False
            register['rax'] = temp_number
            return True
        elif isinstance(source, int):
            temp_number = int(register['rax']) * source
            register['rax'] = temp_number
            return True
        return False

    error_text = "No errors found"
    if len(sys.argv) == 1:
        print("No arguments given when running the assembler")
        return

    file_name = sys.argv[1]
    write_readmode = {'python_instance': subprocess.run, 'read': "r"}
    f = open(file_name, write_readmode['read'])
    base = 32

    Lines = f.readlines()
    source_code = []  # Store the source code as a list of lines of code
    lines_count = 0

    for line in Lines:
        lines_count += 1

        #### section .data
        # 1. Should only be before section .text, if this condition is not
        # met; an error is gonna be raised preventing the proccess to follow
        # 2. Also, any character (including whitespace) after "section .data"
        # is gonna raise an error, the only allowed character is new-line character
        if line_re := re.search(r"(section){1} (.data){1}$", line):
            section_data = True
            if (section_text == True):
                error_text = f"in line {lines_count} section .data was found after section .text"
                raise ValueError(error_text)
        elif line_re := re.search(r"(section){1} (.data){1}.+", line):
            error_text = f"in line {lines_count} alphanumeric characters (including whitespaces) were found after section .data"
            raise ValueError(error_text)

        #### section .text
        # If any character (including whitespace) is found after "section .text" an error is gonna
        # be raised
        elif line_re := re.search(r"(section){1} (.text){1}$", line):
            section_text = True
        elif line_re := re.search(r"(section){1} (.text){1}.+", line):
            error_text = f"in line {lines_count} alphanumeric characters (including whitespaces) were found after section .text"
            raise ValueError(error_text)

        #### define a string
        # Allowed definitions
        # tag: db "text text", 10, 0
        # tag: db "text text",10,0
        # tag: db "text text"
        # The text inside quotes can contain whitespaces, characters and numbers, no more no less
        # Any other definition will fall into an error, description of the regex 
        elif line_re := re.search(r'\w+(:){1} (db){1} ["](\s*\w*\s*)*["](, 10, 0){1}$', line):
            if section_data == False or section_text == True:
                error_text = f"in line {lines_count}: definition {line_re.group()} is out of place"
                raise ValueError(error_text)
            # Split the line
            s = re.split(r'(:){1} (db){1}', line)  # result is gonna be 'tag', ':', 'db', 'value,'
            # Store the tag and its value to set_of_data
            set_of_data[s[0]] = shlex.split(s[3])[0][:-1]  # send the tag directly but split the value
            # from the quotes and remove the last character which is a comma
            verbose_msg(f"define: {line_re.group()} is valid in the context of the compiler", verbose)
        elif line_re := re.search(r'\w+(:){1} (db){1} ["](\s*\w*\s*)*["](,10,0){1}$', line):
            if section_data == False or section_text == True:
                error_text = f"in line {lines_count}: definition {line_re.group()} is out of place"
                raise ValueError(error_text)
            # Split the line
            s = re.split(r'(:){1} (db){1}', line)  # result is gonna be 'tag', ':', 'db', 'value, 10, 0'
            # Store the tag and its value to set_of_data
            set_of_data[s[0]] = shlex.split(s[3])[0][:-5]  # send the tag directly but split the value
            # from the quotes and remove the last 5 characters which are ",10, 0"
            verbose_msg(f"define: {line_re.group()} is valid in the context of the compiler", verbose)
        elif line_re := re.search(r'\w+(:){1} (db){1} ["](\s*\w*\s*)*["]', line):
            if section_data == False or section_text == True:
                error_text = f"in line {lines_count}: definition {line_re.group()} is out of place"
                raise ValueError(error_text)
            # Split the line
            s = re.split(r'(:){1} (db){1}', line)  # result is gonna be 'tag', ':', 'db', 'value'
            # Store the tag and its value to set_of_data
            set_of_data[s[0]] = shlex.split(s[3])[
                0]  # send the tag directly but split the value from the quotes, shlex.split() returns a list
            # so we gotta access to the first member of the list, our value
            verbose_msg(f"define: {line_re.group()} is valid in the context of the compiler", verbose)
        elif line_re := re.search(r'\w+(:){1} (db){1} ["]{1}$', line):
            error_text = f"in line {lines_count}: definition {line_re.group()} quote was not closed"
            raise ValueError(error_text)

        #### define a number
        # The only definition that is for natural numbers
        # also, numbers can go from 0 to 255, if the defined number
        # goes higher or lower from the given limits the definition
        # is gonna be set to the closer limit
        # An error is gonna be raised if a word is found outside quotes
        elif line_re := re.search(r"\w+(:){1} (db){1} \d+$", line):
            if section_data == False or section_text == True:
                error_text = f"in line {lines_count}: definition {line_re.group()} is out of place"
                raise ValueError(error_text)
            s = re.split(r'(:){1} (db){1}', line)  # result is gonna be 'tag', ':', 'db', 'value'
            n = int(shlex.split(s[3])[0])  # store the value as an integer number
            set_of_data[s[0]] = clamp(n, 0, 255)  # store the tag and the clamped value on the data list
            if n > 255:
                error_text = f"in line {lines_count}: value {n} does not fit in a byte variable"
                raise ValueError(error_text)
            else:
                verbose_msg(f"define: {line_re.group()} is valid in the context of the compiler", verbose)
        elif line_re := re.search(r"\w+(:){1} (db){1} (-)\d+$", line):
            if section_data == False or section_text == True:
                error_text = f"in line {lines_count}: definition {line_re.group()} is out of place"
                raise ValueError(error_text)
            s = re.split(r'(:){1} (db){1}', line)  # result is gonna be 'tag', ':', 'db', '-', 'value'
            set_of_data[s[0]] = 0
            verbose_msg(f"define: {line_re.group()} is valid but the value is gonna be set to 0", verbose)
        elif line_re := re.search(r'\w+(:){1} (db){1} \d*[a-zA-Z]+\d*$', line):
            error_text = f"in line {lines_count}: definition {line_re.group()} is not a number nor a string"
            raise ValueError(error_text)

        #### mov
        # the mov instruction can be used like the following:
        # format: <mov destiny,source>
        # mov reg,reg
        # mov reg,number
        # mov reg,variable
        # mov variable,reg
        # mov variable,variable
        # mov variable,number
        # no whitespace is allowed after or before the comma
        # any other way of writing a mov instruction is gonna raise an Error
        elif line_re := re.search(r"(mov){1} \w+,\w+$", line):
            if not section_text:
                error_text = f"in line {lines_count} {line_re.group()} needs to be after section .text"
                raise ValueError(error_text)
            s = re.split(r'(mov){1} (\w+)(,){1}(\w+)', line)  # result is gonna be '', 'mov', 'destiny', ',', 'source'
            if re.search(r'^[0-9]+$', s[4]):  # send the source as a number
                if not mov(s[2], int(
                        s[4])):  # execute the mov instruction, if the value returned is false something happened;
                    # source or destiny might not exist
                    error_text = f"in line {lines_count}: {line_re.group()} is invalid, source or destiny might not exist"
                    raise ValueError(error_text)
            else:  # send the source as a string, this means is any other register or a variable stored at set_of_data
                if not mov(s[2],
                           s[4]):  # execute the mov instruction, if the value returned is false something happened;
                    # source or destiny might not exist
                    error_text = f"in line {lines_count}: {line_re.group()} is invalid, source or destiny might not exist"
                    raise ValueError(error_text)
            if not check_registers():  # if an unexistent register is used an error is gonna be raised
                error_text = f"in line {lines_count}: {s[2]} is a non-valid register"
                raise ValueError()
            verbose_msg(f"mov: {line_re.group()} is valid in the context of the compiler", verbose)
        elif (line_re := re.search(r"(mov){1}",
                                   line)):  # if the mov instruction is written in any different way raise an Error
            error_text = f"in line {lines_count}: not a valid mov instruction"
            raise ValueError(error_text)

        #### add
        elif line_re := re.search(r"(add){1} \w+,\w+$", line):
            if section_text == False:
                error_text = f"in line {lines_count} {line_re.group()} needs to be after section .text"
                raise ValueError(error_text)
            s = re.split(r'(add){1} (\w+)(,){1}(\w+)', line)  # result is gonna be '', 'add', 'destiny', ',', 'source'
            if re.search(r'^[0-9]+$', s[4]):  # send the source as a number
                if not add(s[2], int(
                        s[4])):  # execute the add instruction, if the value returned is false something happened;
                    # source or destiny might not exist
                    error_text = f"in line {lines_count}: {line_re.group()} is invalid, source or destiny might not exist"
                    raise ValueError(error_text)
            else:  # send the source as a string, this means is any other register or a variable stored at set_of_data
                if not add(s[2],
                           s[4]):  # execute the add instruction, if the value returned is false something happened;
                    # source or destiny might not exist
                    error_text = f"in line {lines_count}: {line_re.group()} is invalid, source or destiny might not exist"
                    raise ValueError(error_text)
            if not check_registers():  # if an unexistent register is used an error is gonna be raised
                error_text = f"in line {lines_count}: {s[2]} is a non-valid register"
                raise ValueError()
            verbose_msg(f"add: {line_re.group()} is valid in the context of the compiler", verbose)
        elif (line_re := re.search(r"(add){1}",
                                   line)):  # if the add instruction is written in any different way raise an Error
            error_text = f"in line {lines_count}: not a valid add instruction"
            raise ValueError(error_text)

            #### div
        elif line_re := re.search(r"(div){1} \w+,\w+$", line):
            if not section_text:
                error_text = f"in line {lines_count} {line_re.group()} needs to be after section .text"
                raise ValueError(error_text)
            s = re.split(r'(div){1} (\w+)(,){1}(\w+)', line)  # result is gonna be '', 'div', 'destiny', ',', 'source'
            if re.search(r'^[0-9]+$', s[4]):  # send the source as a number
                if not div(s[2], int(
                        s[4])):  # execute the add instruction, if the value returned is false something happened;
                    # source or destiny might not exist
                    error_text = f"in line {lines_count}: {line_re.group()} is invalid, source or destiny might not exist"
                    raise ValueError(error_text)
            else:  # send the source as a string, this means is any other register or a variable stored at set_of_data
                if not div(s[2],
                           s[4]):  # execute the add instruction, if the value returned is false something happened;
                    # source or destiny might not exist
                    error_text = f"in line {lines_count}: {line_re.group()} is invalid, source or destiny might not exist"
                    raise ValueError(error_text)
            if not check_registers():  # if an unexistent register is used an error is gonna be raised
                error_text = f"in line {lines_count}: {s[2]} is a non-valid register"
                raise ValueError()
            verbose_msg(f"div: {line_re.group()} is valid in the context of the compiler", verbose)
        elif (line_re := re.search(r"(div){1}",
                                   line)):  # if the add instruction is written in any different way raise an Error
            error_text = f"in line {lines_count}: not a valid add instruction"
            raise ValueError(error_text)

            #### mul
        elif line_re := re.search(r"(mul){1} \w+$", line):
            s = re.split(r'(mul){1} (\w+)$', line)
            if re.search(r'^[0-9]+$', s[2]):
                if not mul(int(s[2])):
                    error_text = f"in line {lines_count}: {line_re.group()} is invalid, source does not exists"
                    raise ValueError(error_text)
            else:
                if not mul(s[2]):
                    error_text = f"in line {lines_count}: {line_re.group()} is invalid, source does not exists"
                    raise ValueError(error_text)
            verbose_msg(f"mul: {line_re.group()} is a valid multiplication", verbose)
        elif line_re := re.search(r"(mul){1}", line):
            error_text = f"in line {lines_count}: mul instruction is not valid"
            raise ValueError(error_text)

        #### sub
        elif line_re := re.search(r"(sub){1} \w+,\w+$", line):
            if not section_text:
                error_text = f"in line {lines_count} {line_re.group()} needs to be after section .text"
                raise ValueError(error_text)
            s = re.split(r'(sub){1} (\w+)(,){1}(\w+)', line)  # result is gonna be '', 'sub', 'destiny', ',', 'source'
            if re.search(r'^[0-9]+$', s[4]):  # send the source as a number
                if not sub(s[2], int(
                        s[4])):  # execute the sub instruction, if the value returned is false something happened;
                    # source or destiny might not exist
                    error_text = f"in line {lines_count}: {line_re.group()} is invalid, source or destiny might not exist"
                    raise ValueError(error_text)
            else:  # send the source as a string, this means is any other register or a variable stored at set_of_data
                if not sub(s[2],
                           s[4]):  # execute the sub instruction, if the value returned is false something happened;
                    # source or destiny might not exist
                    error_text = f"in line {lines_count}: {line_re.group()} is invalid, source or destiny might not exist"
                    raise ValueError(error_text)
            if not check_registers():  # if an unexistent register is used an error is gonna be raised
                error_text = f"in line {lines_count}: {s[2]} is a non-valid register"
                raise ValueError()
            verbose_msg(f"sub: {line_re.group()} is valid in the context of the compiler", verbose)
        elif line_re := re.search(r"(sub){1}",
                                  line):  # if the sub instruction is written in any different way raise an Error
            error_text = f"in line {lines_count}: not a valid sub instruction"
            raise ValueError(error_text)

        #### extern
        elif line_re := re.search(r"(extern){1} \w+$", line):
            error_text = f"in line {lines_count}: extern libraries are not allowed"
            raise ValueError(error_text)

        #### global and tags
        elif line_re := re.search(r"(global){1} \w+$", line):
            if global_name:
                error_text = f"in line {lines_count}: global function is already declared"
                raise ValueError(error_text)
            s = re.split(r'(global){1} (\w+)$', line)
            global_name = s[2]
            verbose_msg(f"global: function {global_name} is valid", verbose)
        elif line_re := re.search(r"(global)\w* (\w*)(,*)", line):
            error_text = f"in line {lines_count}: invalid at global function declarations"
            raise ValueError(error_text)
        elif line_re := re.search(r"(\w+):$", line):
            s = re.split(r'(\w+):$', line)
            verbose_msg(f"tag: following code will run after {s[1]} tag", verbose)

        #### syscall
        elif line_re := re.search(r'(syscall){1}$', line):
            match register['rax']:
                case '1' | 1:   # sys_exit
                    verbose_msg("syscall: rax = 1 => sys_exit", verbose)
                case '2' | 2:   # sys_fork
                    verbose_msg("syscall: rax = 2 => sys_fork", verbose)
                case '3' | 3:   # sys_read
                    verbose_msg("syscall: rax = 3 => sys_read", verbose)
                case '4' | 4:   # sys_write
                    if register['rbx'] != 1 and register['rbx'] != '1': # for this implementation it is only possible to
                        # write on stdout
                        error_text = f"in line {lines_count}: sys_write is being called but RBX is not set to 1 (stdout)"
                        raise ValueError(error_text)
                    stdout_print_text = register['rcx'][:int(register['rdx'])-1] # from index 0 to rdx-1
                    print(stdout_print_text)
                    verbose_msg("syscall: rax = 4 => sys_write", verbose)
                case '5' | 5:
                    verbose_msg("syscall: rax = 5 => sys_open", verbose)
                case '6' | 6:
                    verbose_msg("syscall: rax = 6 => sys_close", verbose)
                case _:
                    raise ValueError('System call did not recognized the given syscall number')
            verbose_msg(f"syscall: call to the system is valid", verbose)
        elif line_re := re.search(r'(syscall)+\w+(\w* \w*)*$', line):
            error_text = f"in line {lines_count}: maybe you tried to write syscall..."
            raise ValueError(error_text)

        source_code.append(line)

    # Write .o file
    # write_readmode['python_instance']([write_path,of['o'](base+13)+object_settings[0]+"64",file_name],stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)


if __name__ == '__main__':
    main()
