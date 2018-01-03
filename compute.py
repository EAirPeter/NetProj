def GetMd5AsHex(block : bytes) -> bytes :
    md5Val = bytes(32)
    return md5Val


def GetValidNode(height : bytes, id : bytes, parentHash : bytes,
                 data : bytes, timestamp : bytes) -> bytes:
    assert len(height) == 4 and len(id) == 4 and len(parentHash) == 32 \
           and len(data) == 32 and len(timestamp) == 8
    nounce = bytes(16)
    return height + id + parentHash + data + timestamp + nounce