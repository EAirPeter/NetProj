from compute import GetMd5AsHex

# block structure:
# 0-31 content
# 32-39 height
# 40-43 owner id
# 44-63 timestamp
# 64-95 parentHash 
# 96-120 nounce
#  0123 4567 89ab cdef 0123 4567 89ab cdef 0123 4567 89ab cdef 0123 4567 89ab cdef 0123 4567 89ab cdef 0123 4567 89ab cdef 0123 4567 89ab cdef 0123 4567
# +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
# |                 content               | height  | id |        timestamp       |         parent hash val as hex        |            nounce           |
# +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
# for example:
# Implementing a block chain      000000000000Jan  5 00:00:00 19700000000000000000000000000000000000000000000000000000
rootBlock = b''.join([b'Implementing a block chain      ',
                      b'00000000',
                      b'0000',
                      b'Jan  5 00:00:00 1970',
                      b'00000000000000000000000000000000',
                      b'000000000000000000000000'])


def GetBlockHeight(block):
    return block[32:40]


def GetParentHash(block):
    return block[64:96]


def GetBlockOwner(block):
    return block[40:44]


class BlockChain :
    def __init__(self):
        self.height: int = 1
        self.chain: list(bytes) = [rootBlock]

    # return value: 0 : current working chain far too short than incoming chain
    #               1 : first block of incoming subchain failed to match any father block,
    #                   therefore there is no way to link this subchain to working chain
    #               3 : updated successfully
    # only can be returned when overWrite is False
    #               2 : forked, and the corresponding incoming chain needs to be updated
    #                           (while currenting working one not)
    def Update(self, rawData : bytes, overWrite : bool) -> int :
        assert len(rawData) % 120 == 0
        blockCount : int = len(rawData) // 120
        blocks : list(bytes) = [rawData[i * 120 : i * 120 + 120] for i in range(0, blockCount)]
        dataBottom : int = int(GetBlockHeight(blocks[0]))
        dataTop : int = int(GetBlockHeight(blocks[-1]))

        if dataBottom > self.height:
            return 0

        if dataBottom == 0:
            dataBottom = dataBottom + 1
            blocks = blocks[1:]
            blockCount = blockCount - 1

        # check if it can be linked to chain
        if GetMd5AsHex(self.chain[dataBottom - 1]) != GetParentHash(blocks[0]):
            return 1

        # assert it is a valid chain
        for i in range(1, blockCount) :
            assert(GetMd5AsHex(blocks[i-1]) == GetParentHash(blocks[i]))

        if overWrite or dataBottom == self.height or dataTop >= self.height:
            self.chain = self.chain[0:dataBottom]
            self.chain.extend(blocks)
            self.height = dataTop + 1
            return 3
        else:
            # check the owner of every block to decide which chain to work on
            for i in range(0, blockCount):
                assert(GetBlockHeight(self.chain[i + dataBottom])
                     == GetBlockHeight(blocks[i]))
                if GetBlockOwner(self.chain[i + dataBottom]) \
                == GetBlockOwner(blocks[i]):
                    continue
                # the block on current working chain is smaller than coming subchain, so keep working on it
                elif GetBlockOwner(self.chain[i + dataBottom]) \
                   < GetBlockOwner(blocks[i]):
                    return 2
                # switch to the corresponding chain of incoming subchain
                elif GetBlockOwner(self.chain[i + dataBottom]) \
                   > GetBlockOwner(blocks[i]):
                    self.chain = self.chain[0:i + dataBottom]
                    self.chain.extend(blocks[i: blockCount + 1])
                    self.height = dataTop + 1
                    return 3
            return 3

    def GetHeight(self) -> int :
        return self.height

    def GetRangeRaw(self, beg : int, end : int) -> bytes :
        return b''.join(self.chain[beg:end])

    def GetTop(self) -> bytes:
        return self.chain[-1]
