import configparser
from blockchain import BlockChain
import sync
from compute import GetValidNode

configFilePath = '.\config.cfg'

if __name__ == '__main__':
    BC = BlockChain()
    configParser = configparser.RawConfigParser()
    configParser.read(configFilePath)
    difficulty = float(configParser.get('overall-config', 'difficulty'))
    localAddr = configParser.get('local-config', 'ipaddr')
    localPort = int(configParser.get('local-config', 'port'))
    RTO = int(configParser.get('local-config', 'RTO'))

    peerAddrPortItems = configParser.get('peer-config')
    peerAddrPorts : list((str, int)) = []

    for key, addrPort in peerAddrPortItems:
        ipaddr, port= addrPort.strip().rsplit(':', maxsplit=1)
        port = int(port)
        peerAddrPorts.append(ipaddr, port)

