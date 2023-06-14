import pickle
import numpy as np
import time


start = time.time()
while True:
    
    fin = time.time()
    if ((fin-start>=0.1)):
        try:
            with open('vector.pickle','rb') as file:
                data = pickle.load(file)
            print(data)
        except:
            pass
        start = fin
            
