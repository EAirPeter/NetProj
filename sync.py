from blockchain import BlockChain
from typing import List, Optional, Tuple

import random
import socket
import struct
import time

SockAddr = Tuple[str, int]

class Sync:
    kBufLen : int = 65536
    kNBlock : int = 12
    kZBlock : int = 120

    kRvPll : bytes = b'\x98\x85\xce\x94'
    # [header, 4B] [seqnum, 4B] [beg height, 2B] [end height, 2B]
    kRvPsh : bytes = b'\x98\x85\xce\xc1'
    # [header, 4B] [seqnum, 4B] [max height, 2B] [blocks, 120B each]
    kNmPsh : bytes = b'\x98\x85\xce\xf8'
    # [header, 4B] [seqnum, 4B] [max height, 2B] [blocks, 120B each]

    def __init__(self, bc: BlockChain, localAddr : SockAddr, peersAddr : List[SockAddr], rto : float) -> None:
        self._bc = bc
        self._peers = peersAddr
        self._peers.remove(localAddr)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setblocking(False)
        self._sock.bind(localAddr)
        self._rto = rto
        self._seq = 0

    def DoSync(self) -> None:
        while True:
            res = self._RecvPending()
            if res is None:
                break
            self._Recover(res)
        self._RandomPush()

    def _RecvPending(self) -> Optional[bool]:
        while True:
            (peer, pkt) = self._RecvPkt()
            if peer is None:
                break
            if pkt[0] == Sync.kNmPsh:
                res = self._OnNmPsh(peer, pkt[1], pkt[2], pkt[3])
                if res is not None:
                    return res
            elif pkt[0] == Sync.kRvPll:
                self._OnRvPll(peer, pkt[1], pkt[2], pkt[3])
        return None
    
    def _RandomPush(self) -> None:
        for peer in random.sample(self._peers, 2):
            self._DoNmPsh(peer)

    def _Recover(self, shrink: bool) -> None:
        if shrink:
            self._Shrink()
        while True:
            hbeg = self._bc.GetHeight()
            hend = hbeg + Sync.kNBlock
            pshs: List[Tuple[int, bytes]] = None
            while not pshs:
                pshs = self._PullRound(hbeg, hend)
                pshs = [psh for psh in pshs if psh[0] >= self._bc.GetHeight()]
            hmax = 0
            for psh in pshs:
                hmax = max(hmax, psh[0])
            res = 1
            if lenw[pshs] == 1:
                res = self._bc.Update(pshs[0][1], False)
            elif pshs[0][0] > pshs[1][0]:
                res = self._bc.Update(pshs[0][1], False)
            elif pshs[1][0] > pshs[0][0]:
                res = self._bc.Update(pshs[1][1], False)
            else:
                res = self._bc.Update(pshs[0][1], False)
                if res == 1:
                    res = self._bc.Update(pshs[1][1], False)
                else:
                    self._bc.Update(pshs[1][1], False)
            if res == 1:
                self._Shrink()
            if hmax < self._bc.GetHeight() + 6:
                break

    def _Shrink(self) -> None:
        hmax = self._bc.GetHeight()
        res = 1
        while res == 1:
            hbeg = max(0, hmax - Sync.kNBlock)
            pshs: List[Tuple[int, bytes]] = None
            while not pshs:
                pshs = self._PullRound(hbeg, hmax)
                pshs = [psh for psh in pshs if psh[0] >= self._bc.GetHeight()]
            if len(pshs) == 1:
                res = self._bc.Update(pshs[0][1], True)
            elif pshs[0][0] > pshs[1][0]:
                res = self._bc.Update(pshs[0][1], True)
            elif pshs[1][0] > pshs[0][0]:
                res = self._bc.Update(pshs[1][1], True)
            else:
                res = self._bc.Update(pshs[0][1], True)
                if res == 1:
                    res = self._bc.Update(pshs[1][1], True)
                else:
                    self._bc.Update(pshs[1][1], False)
    
    def _PullRound(self, hbeg: int, hend: int) -> List[Tuple[int, bytes]]:
        seqs = [self._DoRvPll(peer, hbeg, hend) for peer in random.sample(self._peers, 2)]
        pshs: List[Tuple[int, bytes]] = list()
        due = time.time() + self._rto
        while True:
            while True:
                (peer, pkt) = self._RecvPkt()
                if peer is None:
                    break
                if pkt[0] != Sync.kRvPsh:
                    continue
                if pkt[1] not in seqs:
                    continue
                pshs.append((pkt[2], pkt[3]))
                if len(pshs) == 2:
                    return pshs
            time.sleep(0.020)
            if time.time() > due:
                break
        return pshs

    def _OnNmPsh(self, peer: SockAddr, seqnum: int, hmax: int, blocks: bytes) -> Optional[bool]:
        if seqnum != 0:
            return None
        if hmax < self._bc.GetHeight():
            self._DoNmPsh(peer)
            return None
        hcur = self._bc.GetHeight()
        res = self._bc.Update(blocks, False)
        if res == 0:
            return False
        elif res == 1:
            return True
        elif res == 2:
            self._DoNmPsh(peer)
        return None

    def _OnRvPll(self, peer: SockAddr, seqnum: int, hbeg: int, hend: int) -> None:
        hmax = self._bc.GetHeight()
        blocks = self._bc.GetRangeRaw(hbeg, hend)
        self._sock.sendto(struct.pack('<4sLH', Sync.kRvPsh, seqnum, hmax) + blocks, peer)

    def _DoRvPll(self, peer: SockAddr, hbeg: int, hend: int) -> int:
        seqnum = self._seq
        self._seq += 1
        self._sock.sendto(struct.pack('<4sLHH', Sync.kRvPll, seqnum, hbeg, hend), peer)
        return seqnum

    def _DoNmPsh(self, peer: SockAddr) -> None:
        hmax = self._bc.GetHeight()
        hbeg = max(0, hmax - Sync.kNBlock)
        blocks = self._bc.GetRangeRaw(hbeg, hmax)
        self._sock.sendto(struct.pack('<4sLH', Sync.kNmPsh, 0, hmax) + blocks, peer)
    
    def _RecvPkt(self) -> Tuple[Optional[SockAddr], Optional[tuple]]:
        while True:
            try:
                (data, peer) = self._sock.recvfrom(Sync.kBufLen)
            except:
                data = None
            if data is None:
                break
            if len(data) < 8:
                continue
            header = data[:4]
            if header == Sync.kNmPsh or header == Sync.kRvPsh:
                if len(data) < 10 or (len(data) - 10) % Sync.kZBlock != 0:
                    continue
                (seqnum, hmax) = struct.unpack_from('<LH', data, 4)
                blocks = data[10:]
                return (peer, (header, seqnum, hmax, blocks))
            elif header == Sync.kRvPll:
                if len(data) != 12:
                    continue
                (seqnum, hbeg, hend) = struct.unpack_from('<LHH', data, 4)
                return (peer, (header, seqnum, hbeg, hend))
        return (None, None)
