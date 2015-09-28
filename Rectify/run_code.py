import subprocess as sub
import time


def fun(code, user_code, input):
	"""
		'input' is user input, 'code' is correct code, and 'user_code' is code submitted by the user
	"""
	
	##code, user_code, input can also be files in which case fileIO is not required
	input_file = open('input', 'w')
	input_file.write(input)
	input_file.close()

	code_file = open('user_code.c', 'w')
	code_file.write(user_code)
	code_file.close()

	code_file = open('code.c', 'w')
	code_file.write(code)
	code_file.close()
	##

	#Compile User code
	compilation_process = sub.Popen('gcc -o user_code user_code.c 2>error', shell=True)
	exit_status = process.wait()

	#Check for compilation error
	if exit_status:
		error_file = open('error')
		error_message = error_file.read()
		error_file.close()
		return "Compilation Error", error_message

	sub.call(['gcc', '-o', 'code', 'code.c'])		#Compile correct code

	#Run user code
	process = sub.Popen('./user_code < input 1>user_out 2>error', shell=True)

	time.sleep(2)
	if process.poll() is None:					#2 sec timeout period
		process.terminate()
		return "Time Limit Exceeded"

	# If program exits before timeout, check for errors
	exit_status = process.wait()
	if exit_status:
		error_file = open('error')
		error_message = error_file.read()
		error_file.close()
		return "Runtime Error",error_message
	
	sub.call('./code < input >req_out', shell=True)		#Run correct code

	different = sub.call('diff user_out req_out', shell=True)

	if not different:
		return "Success"
	else:
		return "Wrong Answer"