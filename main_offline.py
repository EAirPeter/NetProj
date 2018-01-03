import configparser
from blockchain import BlockChain
from compute import GetValidNode
from compute import GetMd5AsHex
import time

configFilePath = '.\\config.cfg'
dataFilePath = '.\\artical.txt'
logFilePath = '.\\log.txt'

if __name__ == '__main__':
    BC = BlockChain()
    configParser = configparser.RawConfigParser()
    configParser.read(configFilePath)
    difficulty = float(configParser.get('overall-config', 'difficulty'))
    localAddr = configParser.get('local-config', 'ipaddr')
    localPort = int(configParser.get('local-config', 'port'))
    RTO = int(configParser.get('local-config', 'RTO'))

    optNames = configParser.options('peer-config')
    peerAddrPortPairs : list((str, int)) = []

    for optName in optNames:
        addrPort = configParser.get('peer-config', optName)
        ipaddr, port = addrPort.strip().rsplit(':', maxsplit=1)
        port = int(port)
        peerAddrPortPairs.append((ipaddr, port))

    file = open(dataFilePath, 'r')
    words = (file.readline()).split(' ')

    while(len(words) > 0):
        height : bytes = bytes(BC.height).ljust(4, b' ')
        data : bytes = bytes()
        while(len(words) > 0 and len(data) + len(words[0]) < 32):
            data += words.pop(0)
        data = bytes(data.ljust(32))

        parentHash : bytes = GetMd5AsHex(BC.GetTop())

        timestamp = time.asctime()[11:19]
        Node = None
        while(Node is None):
            Node = GetValidNode(height, b' single ', parentHash, data, timestamp)
            timestamp = time.asctime()[11:19]
        BC.Update(Node, False)

    file.close()