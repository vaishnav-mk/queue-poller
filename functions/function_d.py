import random
import time

def function_d(data):
	start_time = time.time()
	# Simulate work with sleep
	time.sleep(random.randint(1, 5))
	end_time = time.time()
	data['function_d'] = {'start_time': start_time, 'end_time': end_time}
