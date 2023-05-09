# Python Program illustrating
# working of argmax()

import numpy as np

arr = np.random.rand(3, 10, 10)
max_val = np.argmax(arr, axis= 0)

print(max_val.shape)
