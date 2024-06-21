import random
import time

def function_a(data):
	start_time = time.time()
	# Simulate work with sleep
	time.sleep(random.randint(1, 5))
	end_time = time.time()
	data['function_a'] = {'start_time': start_time, 'end_time': end_time}
