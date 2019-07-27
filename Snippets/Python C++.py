import ctypes, _ctypes

source = \ # from_cpp.cpp
'''
#include <math.h>

extern "C" int py_pow(int x, int y) {
    return pow(x, y);
}
'''

# mingw64
with open('from_cpp.cpp', 'w') as f:
    f.write(source)

# g++ -c from_cpp.cpp
# g++ -shared -o from_cpp.dll from_cpp.o
# del from_cpp.cpp from_cpp.o

if __name__ == '__main__':
    lib = ctypes.CDLL('from_cpp.dll')
    val = lib.py_pow(5, 4)
    print('from cpp: {}'.format(val))
    _ctypes.FreeLibrary(lib._handle)

    # from cpp: 625
