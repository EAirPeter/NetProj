import hashlib
import random
def GetMd5AsHex(block : bytes) -> bytes:
    m = hashlib.md5()
    m.update(block)
    return bytes(m.hexdigest(), 'utf-8')


def GetValidNode(content : bytes, height : bytes, id : bytes,
                 timestamp: bytes, parentHash : bytes, difficulty: float) -> bytes:
    assert len(content) == 32 and len(height) == 8 and len(id) == 4 \
           and len(timestamp) == 20 and len(parentHash) == 32
    beg = random.randint(10000000000000000000,100000000000000000000)
    for i in range(beg, beg + 10000000000000000000000):
        nounce = b'  ' + bytes(str(i).rjust(20,' '), 'utf-8') + b'  '
        tryBlock = content + height + id + timestamp + nounce + parentHash
        if GetMd5AsHex(tryBlock) < b'0000'.ljust(32, b'f'):
            return tryBlock
    return None