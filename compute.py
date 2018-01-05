def GetMd5AsHex(block : bytes) -> bytes :
    md5Val = b'hashval placeholder'.ljust(32)
    return md5Val


def GetValidNode(content : bytes, height : bytes, id : bytes,
                 timestamp: bytes, parentHash : bytes) -> bytes:
    assert len(content) == 32 and len(height) == 8 and len(id) == 4 \
           and len(timestamp) == 20 and len(parentHash) == 32
    nounce = b'placeholder'.ljust(24)
    return content + height + id + timestamp + nounce + parentHash