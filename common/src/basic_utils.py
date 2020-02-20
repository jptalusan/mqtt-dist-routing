import datetime
import time

time_print = lambda type: datetime.now().strftime("%d/%m/%Y %H:%M:%S") if type == 'str' else int(round(time.time() * 1000))

decode = lambda x: x.decode('utf-8')
encode = lambda x: x.encode('ascii')