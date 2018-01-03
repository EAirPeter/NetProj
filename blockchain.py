from numpy import array_split
from compute import GetMd5AsHex


rootBlock = sum( [b'0000', b'0000',
                  b'00000000000000000000000000000000',
                  b'Implementing a block chain      ',
                  b'00:00:00',
                  b'0000000000000000'] )


class BlockChain :
    def __init__(self):
        self.height: int = 1
        self.chain: list(bytes) = [rootBlock]

    def Update(self, rawData : bytes, overWrite : bool) -> bool :
        assert len(rawData) % 96 == 0
        blockCount : int = len(rawData) // 96
        blocks : list(bytes) = [rawData ]
        dataBottom : int = int(blocks[0][0:4])
        dataTop : int = int(blocks[-1][0:4])
        parentHash: bytes = blocks[0][8:40]

        if dataBottom > self.height:
            return False

        # check if it can be linked to chain
        if GetMd5AsHex(self.chain[dataBottom - 1]) != parentHash:
            return False

        # assert its a valid chain
        for i in range(1, blockCount) :
            assert(GetMd5AsHex(blocks[i-1]) == blocks[i][8:40])

        if overWrite:
            self.chain = self.chain[0:dataBottom]
            self.chain.extend(blocks)
            self.height = dataTop + 1
        else:
            # check the owner of every block to decide which chain to work on
            for i in range(0, dataTop + 1):
                assert(self.chain[i + dataBottom][0:4] == blocks[i][0:4])
                if (self.chain[i + dataBottom] == blocks[i]):
                    continue
                # the block on current working chain is smaller than coming subchain, so keep working on it
                elif (self.chain[i + dataBottom] < blocks[i]):
                    break
                # switch to the coming subchain
                elif (self.chain[i + dataBottom] > blocks[i]):
                    self.chain = self.chain[0:i + dataBottom]
                    self.chain.extend(blocks[i: blockCount + 1])
                    self.height = dataTop + 1

        return True

    def GetHeight(self) -> int :
        return self.height

    def GetRangeRaw(self, beg : int, end : int) -> bytes :
        return sum(self.chain[beg:end])

    def GetTop(self) -> bytes:
        return self.chain[-1]