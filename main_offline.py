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
    localId : bytes = bytes(configParser.get('local-config', 'id'), 'utf-8')
    RTO = int(configParser.get('local-config', 'RTO'))

    optNames = configParser.options('peer-config')
    peerAddrPortPairs : list((str, int)) = []

    for optName in optNames:
        addrPort = configParser.get('peer-config', optName)
        ipaddr, port = addrPort.strip().rsplit(':', maxsplit=1)
        port = int(port)
        peerAddrPortPairs.append((ipaddr, port))

    file = open(contentFilePath, 'r', encoding='utf-8')
    words = file.readline()
    words = words.split(' ')
    effectiveData = GetEffectiveData(words)
    file.close()

    while BC.height < len(effectiveData):
        height : bytes = bytes(str(BC.height), 'utf-8').ljust(4, b' ')
        content : bytes = effectiveData[BC.height]

        parentHash : bytes = GetMd5AsHex(BC.GetTop())

        timestamp = bytes(time.asctime()[11:19], 'utf-8')
        Node = None
        while Node is None:
            Node = GetValidNode(height, localId, parentHash, content, timestamp)
            timestamp = time.asctime()[11:19]
        print("Node to be updated:{}".format(Node))
        BC.Update(Node, True)

    # print chain
    # print("{content}{height}{id}{parentHash}{timestamp}{nounce}"
    #       .format(height='height', id='id'.ljust(4),
    #               parentHash='parentHash'.ljust(32), content='content'.ljust(32),
    #               timestamp='timestamp', nounce='nounce'.ljust(16)))

    for i in range(BC.height):
        print(str(BC.chain[i])[2:-1])

        # height = str(int(BC.chain[i][0:4])).ljust(6)
        # id = str(BC.chain[i][4:8])[2:-1]
        # parentHash = str(BC.chain[i][8:40])[2:-1]
        # content = str(BC.chain[i][40:72])[2:-1]
        # timestamp = str(BC.chain[i][72:80])[2:-1]
        # nounce = str(BC.chain[i][80:96])[2:-1]
        # print("{content}{height}{id}{parentHash}{timestamp}{nounce}"
        #       .format(height=height, id=id,
        #               parentHash=parentHash, content=content,
        #               timestamp=timestamp.ljust(9), nounce=nounce))

