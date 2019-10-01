import sys, re

preamble = r"""

/*****************************************************************************
 * benchmarks.c
 *****************************************************************************/

#include <sys/platform.h>
#include "adi_initialize.h"
#include "benchmarks.h"

#include <string.h>
#include <cycle_count.h>
#include <stdio.h>

#include "test.h"

#define STRINGIZE_(TEST) #TEST
#define STRINGIZE(TEST) STRINGIZE_(TEST)

#define TEST_NAME_LENGTH 50

#define RANDOM_DATA_SIZE 10
#define RANDOM_DATA -486482214,-418856181,930282014,-347347496,-138348819,-988261325,815146594,-867907548,408358427,-669950624

#if defined SIM
#define NUMBENCHMARKS 1
#else
#define NUMBENCHMARKS 50000
#endif

void benchmark(void func(void *, size_t), void *data, size_t numBytes);
void ddot_r(int data[], int numWords);
void bubble_sort(int a[], int n);
void no_test(int data[], int numWords);

/** 
 * If you want to use command program arguments, then place them in the following string. 
 */
char __argv_string[] = "";

void no_test(int data[], int numWords)
{
    return;
}

void bubble_sort(int a[], int n) {
   int i = 0, j = 0, tmp;
   for (i = 0; i < n; i++) {   // loop n times - 1 per element
       for (j = 0; j < n - i - 1; j++) { // last i elements are sorted already
            if (a[j] > a[j + 1]) {  // swop if order is broken
               tmp = a[j];
               a[j] = a[j + 1];
               a[j + 1] = tmp;
           }
       }
   }
}

void ddot_r(int data[], int numWords)
       {
		int n = numWords;
		int *dx = (int *)data[0];
		int incx = data[1];
		int *dy = (int *)data[2];
		int incy = data[3];
       int dtemp;
       int i,ix,iy;

       dtemp = 0;

       if (n <= 0)
           return;

       if (incx != 1 || incy != 1)
           {

           /* code for unequal increments or equal increments != 1 */

           ix = 0;
           iy = 0;
           if (incx < 0) ix = (-n+1)*incx;
           if (incy < 0) iy = (-n+1)*incy;
           for (i = 0;i < n; i++)
               {
               dtemp = dtemp + dx[ix]*dy[iy];
               ix = ix + incx;
               iy = iy + incy;
               }
           return;
           }

       /* code for both increments equal to 1 */

       for (i=0;i < n; i++)
           dtemp = dtemp + dx[i]*dy[i];
       return;
}

int main(int argc, char *argv[])
{
int random_data[] = {RANDOM_DATA};
int n = RANDOM_DATA_SIZE;
"""

postamble = r"""

	return 0;
}

//https://gist.github.com/RenatoUtsch/4162799
void benchmark(void func(void *, size_t), void *data, size_t numBytes)
{
	cycle_t start_count;
	cycle_t final_count;
	cycle_t total_count = 0;
	int i;

	for(i = 0; i < NUMBENCHMARKS; ++i)
		{
		START_CYCLE_COUNT(start_count);

		/* Call the function to benchmark. */
		func(data, numBytes);

		STOP_CYCLE_COUNT(final_count,start_count);
		total_count += final_count;
		}
	char test_name[TEST_NAME_LENGTH + 1]; //MAX LENGTH!!!
	strcpy(test_name, TESTNAME);
	printf("%s\n", test_name);
	PRINT_CYCLES("cycles:", total_count);
	printf("test#: %s\n", STRINGIZE(TEST));
	printf("numbenchmarks: %d\n", NUMBENCHMARKS);
}
"""
class Test:
    def __init__(self, name, instrs):
        self.name = name
        self.instrs = instrs

tests = []

name = "bubblesort1"
instrs = '''
        int *a = &random_data;
        int num = 5;
        benchmark(bubble_sort, a, num);
'''
tests.append(Test(name, instrs))

name = "ddot1"
instrs = '''
        int num = 5;
        int *dx = &random_data;
        int incx = 1;
        int *dy = &random_data;
        int incy = 1;
        int data[] = {dx, incx, dy, incy};
        benchmark(ddot_r, &data, num);
'''
tests.append(Test(name, instrs))

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

def generate_benchmarks(output):
        with open (output, 'w') as fout:

                fout.write(preamble)
                fout.write('\n\t#if TEST == 0\n\t\t#define TESTNAME "notest"')
                fout.write('\n\t\tbenchmark(no_test, 0, 0);')

                for i, test in enumerate(tests, start = 1):
                        fout.write('\n\t#elif TEST == %d' % i)
                        fout.write(test.instrs)
                        fout.write('\n\t\t#define TESTNAME "%s"' % test.name[0:49])

                fout.write('\n\t#elif TEST >= %d\n\t\t#define TESTNAME "end"\n\t\tbenchmark(no_test, 0, 0);\n\t#else\n\t\t#define TESTNAME "undefined"\n\t\tbenchmark(no_test, 0, 0);\n\t#endif' %(i+1))
                fout.write(postamble)

