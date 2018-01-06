import time
import configparser
from blockchain import BlockChain
from compute import GetValidNode
from compute import GetMd5AsHex


configFilePath = '.\\config.cfg'
contentFilePath = '.\\artical.txt'
logFilePath = '.\\log.txt'


def GetEffectiveData(words):
    EffectiveData = []
    while len(words) > 0:
        contentOfBlock = bytes(words.pop(0), 'utf-8')
        # put words into contentOfBlock while keeping its length less than 32
        while len(words) > 0 and len(contentOfBlock) + len(words[0]) + 1 < 31:
            contentOfBlock += b' ' + bytes(words.pop(0), 'utf-8')
        # padding to 32
        EffectiveData.append(contentOfBlock.ljust(32))

    return EffectiveData


if __name__ == '__main__':
    BC = BlockChain()
    configParser = configparser.RawConfigParser()
    configParser.read(configFilePath)
    difficulty = float(configParser.get('overall-config', 'difficulty'))
    localAddr = configParser.get('local-config', 'ipaddr')
    localPort = int(configParser.get('local-config', 'port'))
    localId = bytes(configParser.get('local-config', 'id'), 'utf-8')
    RTO = int(configParser.get('local-config', 'RTO'))

    optNames = configParser.options('peer-config')
    peerAddrPortPairs = []

    for optName in optNames:
        addrPort = configParser.get('peer-config', optName)
        ipaddr, port = addrPort.strip().rsplit(':', maxsplit=1)
        port = int(port)
        peerAddrPortPairs.append((ipaddr, port))

    file = open(contentFilePath, 'r', encoding='utf-8')
    words = file.readline().split(' ')
    effectiveData = GetEffectiveData(words)
    file.close()

    while BC.height < len(effectiveData):
        height = bytes(str(BC.height), 'utf-8').ljust(8, b' ')
        content = effectiveData[BC.height]

        parentHash = GetMd5AsHex(BC.GetTop())

        timestamp = bytes(time.asctime()[4:24], 'utf-8')
        Node = None
        while Node is None:
            Node = GetValidNode(content, height, localId, timestamp, parentHash)
            timestamp = time.asctime()[4:24]
        BC.Update(Node, True)

    # print chain
    for i in range(BC.height):
        print(str(BC.chain[i])[2:-1])


