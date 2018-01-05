import configparser
import time
import sync
from blockchain import BlockChain
from compute import GetValidNode
from compute import GetMd5AsHex

configFilePath = '.\\config.cfg'
contentFilePath = '.\\artical.txt'
logFilePath = '.\\log.txt'


def GetEffectiveData(words: list(str)):
    EffectiveData : list(bytes) = []
    while len(words) > 0:
        contentOfBlock = bytes(words.pop(0), 'utf-8')
        # put words into contentOfBlock while keeping its length less than 32
        while len(words) > 0 and len(contentOfBlock) + len(words[0]) + 1 < 32:
            contentOfBlock += b' ' + bytes(words.pop(0), 'utf-8')
        # padding to 32
        EffectiveData.append(contentOfBlock.ljust(32))

    return EffectiveData


if __name__ == '__main__':
    BC = BlockChain()
    configParser = configparser.RawConfigParser()
    configParser.read(configFilePath)
    difficulty = float(configParser.get('overall-config', 'difficulty'))
    localAddr : str = configParser.get('local-config', 'ipAddr')
    localPort : int = int(configParser.get('local-config', 'port'))
    localId : bytes = bytes(configParser.get('local-config', 'id'), 'utf-8')
    RTO = int(configParser.get('local-config', 'RTO'))

    optNames = configParser.options('peer-config')
    peerAddrPortPairs : list((str, int)) = []

    for optName in optNames:
        addrPort = configParser.get('peer-config', optName)
        ipaddr, port = addrPort.strip().rsplit(':', maxsplit=1)
        port = int(port)
        peerAddrPortPairs.append((ipaddr, port))

    file = open(contentFilePath, 'r')
    words = (file.readline()).split(' ')
    print(type(words))
    file.close()
    effectiveData = GetEffectiveData(words)

    syncer = sync.Sync()
    localAddrPort = (localAddr, localPort)
    syncer.SyncInit(BC, localAddrPort, peerAddrPortPairs, RTO)

    while BC.height < len(effectiveData):
        # work out the component in the block we are going to dig in this round
        height : bytes = bytes(str(BC.height), 'utf-8').ljust(4, b' ')
        content : bytes = effectiveData[BC.height]

        parentHash : bytes = GetMd5AsHex(BC.GetTop())
        timestamp : bytes = bytes(time.asctime()[11:19], 'utf-8')
        Node = GetValidNode(height, localId, parentHash, content, timestamp)

        if Node is not None:
            BC.Update(Node, False)
        syncer.SyncPeer()

    # print chain
    print("{height} | {id} | {parentHash} | {content} | {timestamp} | {nounce}"
          .format(height='height', id='id'.ljust(4),
                  parentHash='parentHash'.ljust(32), content='content'.ljust(32),
                  timestamp='timestamp', nounce='nounce'.ljust(16)))
    for i in range(BC.height):
        height = int(BC.chain[i][0:4])
        id = BC.chain[i][4:8]
        parentHash = BC.chain[i][8:40]
        content = BC.chain[i][40:72]
        timestamp = BC.chain[i][72:80]
        nounce = BC.chain[i][80:96]
        print("{height} | {id} | {parentHash} | {content} | {timestamp} | {nounce}"
              .format(height=height.ljust(6), id=id,
                      parentHash=parentHash, content=content,
                      timestamp=timestamp.ljust(9), nounce=nounce))