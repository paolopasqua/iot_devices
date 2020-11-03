# from pymodbus.client.sync import ModbusTcpClient

# client = ModbusTcpClient(host='127.0.0.1', port=5000)
# result = client.read_coils(0,1)
# print(result)
# client.close()

# print(__name__)
# print(__file__)
# # print(__path__)
# print(__package__)
# print(__spec__)
# print(__doc__)
import os
import sys
import time
import threading

# try:
from IPython import embed
# except ImportError:
#     import code

#     def embed():
#         vars = globals()
#         vars.update(locals())
#         shell = code.InteractiveConsole(vars)
#         shell.interact()

def run():
    time.sleep(5)
    os.system("exit")
threading.Thread(target=run).start()

embed()