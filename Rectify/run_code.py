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

	not_compiled = sub.call(['gcc', '-o', 'user_code', 'user_code.c'])
	if not_compiled:
		return "Compilation Error"
	sub.call(['gcc', '-o', 'code', 'code.c'])

	process = sub.Popen('./user_code < input >user_out', shell=True)

	time.sleep(2)
	if process.poll() is None:
		process.terminate()
		return "Time Limit Exceeded"

	exit_status = process.wait()
	if exit_status:
		return "Runtime Error"
	
	sub.call('./code < input >req_out', shell=True)

	different = sub.call('diff user_out req_out', shell=True)

	if not different:
		return "Success"
	else:
		return "Wrong Answer"