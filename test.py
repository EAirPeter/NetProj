from ctypes import *
handle = cdll.LoadLibrary("build/libmd5.so")
ss = "012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789";
print(len(ss))
message = create_string_buffer(ss.encode()[0:119])
print(len(message))
digest = create_string_buffer(32)
handle.md5(digest, message)
print(digest.raw)
print(handle.md5_compute(message, c_ulonglong( 2 ** 64 // 1000000 )))
print(message.raw)
handle.md5(digest, message)
print(digest.raw)
