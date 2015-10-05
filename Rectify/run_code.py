import subprocess32 as sub
import time, random, os


def fun(code, user_code, user_input):

	#Compile User code
	usercode_exec = str(random.randint(100000000, 999999999))
	compilation = sub.Popen('gcc -o ' + usercode_exec + ' -x c -', stdin=sub.PIPE, stderr=sub.PIPE, shell=True)
	error_message = compilation.communicate(input = user_code)[1]

	#Check for compilation error
	if error_message:
		return 1, error_message				#Compilation Error

	#Run user code
	process = sub.Popen('./'+usercode_exec, stdin=sub.PIPE, stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
	user_out, error_message = process.communicate(input = user_input)
	
	
	time.sleep(2)
	if process.poll() is None:					#2 sec timeout period
		process.terminate()
		os.remove(usercode_exec)
		return 2, None							#Timeout Exceeded

	os.remove(usercode_exec)

	# If program exits before timeout, check for errors
	if error_message:
		return 3, error_message					#Runtime Error
	
	#Compile correct code
	#if 'code' not in os.listdir('.'):
	compilation = sub.Popen('gcc -o code -x c -', stdin=sub.PIPE, stderr=sub.PIPE, shell=True)
	error_message = compilation.communicate(input = code)[1]	

	#Run correct code
	server_code = sub.Popen('./code',stdin=sub.PIPE, stdout=sub.PIPE, shell=True)		
	req_out = server_code.communicate(input = user_input)[0]
	os.remove('code')

	if user_out == req_out:
		return 0, None				#Correct Ans
	else:
		return 4, None				#Wrong Ans


if __name__ == '__main__':
	user_input = '1 2 3'
	code = """
	#include <stdio.h>
	int main()
	{
		printf("HEllo World");
		return 0;
	}
	"""
	
	user_code = """
	#include <stdio.h>
	int main()
	{
		while(1);
		printf("HEllo World");
		return 0;
	}
	"""

	fun(code, user_code, user_input)
