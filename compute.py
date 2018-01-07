import hashlib
import random
from ctypes import *
handle = cdll.LoadLibrary("build/libmd5.so")


def GetMd5AsHex(block: bytes) -> bytes:
    digest = create_string_buffer(32)
    handle.md5(digest, block)
    return digest.raw


def GetValidNode(content: bytes, height: bytes, id: bytes,
                 timestamp: bytes, parentHash: bytes, difficulty: float) -> bytes:
    assert len(content) == 32 and len(height) == 8 and len(id) == 4 \
        and len(timestamp) == 20 and len(parentHash) == 32
    nounce = b' ' * 24
    assert len(nounce) == 24
    tryBlock = content + height + id + timestamp + parentHash + nounce
    assert(len(tryBlock) == 120)
    buffer = create_string_buffer(tryBlock)
    if handle.md5_compute(buffer, c_ulonglong(int(2**45 * difficulty))) == 1:
        b = buffer.raw[0:120]
        print("fake " + b.decode())
        return b
    else:
        return None

# ss = "012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789";
# print(len(ss))
# message = create_string_buffer(ss.encode())
# print(digest.raw)
# print(handle.md5_compute(message, c_ulonglong( 2 ** 64 // 1000000 )))
# print(message.raw)
# handle.md5(digest, message)
# print(digest.raw)
