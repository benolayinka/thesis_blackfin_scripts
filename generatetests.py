import sys, re

preamble = """

/*****************************************************************************
 * bf706ez.c
 *****************************************************************************/

#include <sys/platform.h>
#include "adi_initialize.h"
#include "bf706ez.h"
#include "test.h"

#include <string.h>
#include <cycle_count.h>
#include <stdio.h>

#define STRINGIZE_(TEST) #TEST
#define STRINGIZE(TEST) STRINGIZE_(TEST)

#define TEST_NAME_LENGTH 50

#if defined SIM
asm ("#define SIM 1");
#endif

asm ("#define COMMA ,");
asm ("#if defined SIM");
asm ("#define SECONE 1");
asm ("#define SECTWO 1");
asm ("#define SECZERO 1");
asm ("#else");
asm ("#define SECONE 50000000");
asm ("#define SECTWO 25000000");
asm ("#define SECZERO 0xFFFFFFFF");
asm ("#endif");

asm ("#define lp100(instr) P4=SECONE; LOOP LC0 = P4; instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr LOOP_END;");
asm ("#define lp200(instr) P4=SECTWO; LOOP LC0 = P4; instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr instr LOOP_END;");

/** 
 * If you want to use command program arguments, then place them in the following string. 
 */
char __argv_string[] = "";

int add (volatile int * a, volatile int * b){
			return *a+*b;
	}

int main(int argc, char *argv[]) {
	/**
	 * Initialize managed drivers and/or services that have been added to
	 * the project.
	 * @return zero on success
	 */
	// adi_initComponents(); //ben this doesnt seem to make a difference. register init?
	/* Begin adding your custom code here */

	cycle_t start_count;
	cycle_t final_count;
	START_CYCLE_COUNT(start_count);
"""

postamble = """
	STOP_CYCLE_COUNT(final_count,start_count);

	char test_name[TEST_NAME_LENGTH + 1]; //MAX LENGTH!!!
	strcpy(test_name, TESTNAME);
	printf("%s ", test_name);
	PRINT_CYCLES("cycles:", final_count);
	printf("test#: %s\\n", STRINGIZE(TEST));

	return 0;
}

"""

def comment_remover(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return "" # note: a space and not an empty string
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)

def splitlines_blank_remover(text):
	lines = text.split('\n')
	lines = [line for line in lines if line.strip()]
	return lines

def increment_reg_remover(text):
	pattern = re.compile(r'\[\W*([a-zA-Z]+[0-9]+).*?[+-].*?\]')
	for line in text:
		if re.search(pattern, line):
			print('removing increment register test at ' + line)
		else:
			yield line

def comma_replacer(text):
	for line in text:
		if ',' in line:
			print('replacing comma test at ' + line)
			yield line.replace(',', ' COMMA ')
		else:
			yield line

def get_reg(text):
	pattern = re.compile(r'\[\W*([a-zA-Z]+[0-9]+).*?\]')
	return re.findall(pattern, text)

def generate_tests(input, output):
    with open (input) as fin:
            with open (output, 'w') as fout:

                    fout.write(preamble)
                    fout.write('\n\t#if TEST == 0\n\t\t#define TESTNAME "notest"')

                    text = comment_remover(fin.read())
                    text = splitlines_blank_remover(text)
                    text = comma_replacer(text)

                    for i, line in enumerate(increment_reg_remover(text), start = 1):
                            fout.write('\n\t#elif TEST == %d' % i)
                            if '[' in line:
                                            for reg in get_reg(line):
                                                    fout.write('\n\t\tasm("')
                                                    fout.write(reg)
                                                    fout.write('=SP;");')
                            fout.write('\n\t\tasm ("lp200(')
                            fout.write(line)
                            fout.write(')");')
                            fout.write('\n\t\t#define TESTNAME "%s"' % line[0:49])

                    fout.write('\n\t#elif TEST >= %d\n\t\t#define TESTNAME "end"\n\t#else\n\t\t#define TESTNAME "undefined"\n\t#endif' %(i+1))
                    fout.write(postamble)

