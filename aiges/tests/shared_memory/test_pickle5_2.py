from multiprocessing import Process, Pipe

import time
import numpy as np

class Test:
    def __init__(self,name,age):
        self.name = name
        self.age = age

def sender(send_conn):
    # Our big python data object
    big_array = np.arange(5 * 10**7)
    tst = Test("cccc","ddd")
    send_conn.send(tst)
    send_conn.close()

def receiver(recv_conn):
    obj = recv_conn.recv()
    recv_conn.close()

    return obj


if __name__ == '__main__':

    recv_conn, send_conn = Pipe(duplex=False)

    start_time = time.time()

    p = Process(target=sender, args=(send_conn,))
    p.start()

    obj = receiver(recv_conn)

    p.join()

    print("--- Total %s seconds ---" % (time.time() - start_time))

    print(obj) # [       0        1        2 ... 49999997 49999998 49999999]