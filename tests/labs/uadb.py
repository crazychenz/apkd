#!/usr/bin/env python3

import asyncio
import struct
from types import SimpleNamespace
import pdb

JDWP_HOST = 'localhost'
JDWP_PORT = 8700

class VirtualMachine_AllClasses():
    def __init__(self, session):
        self.session = session
        self.cmd_set = 1
        self.cmd_id = 3
    
    async def run(self):
        
        pkt = self.session.packet_id
        self.session.packet_id += 1
    
        await self._send_packet(packet_id=pkt, command_set=self.cmd_set, command=self.cmd_id)
        data = await self._read_reply()

        count = struct.unpack('>I', data[:4])[0]
        offset = 4
        classes = []
        for _ in range(count):
            ref_type_tag = data[offset]
            offset += 1
            type_id = struct.unpack('>Q', data[offset:offset+8])[0]
            offset += 8
            sig_len = struct.unpack('>I', data[offset:offset+4])[0]
            offset += 4
            signature = data[offset:offset+sig_len].decode('utf-8')
            offset += sig_len
            status = struct.unpack('>I', data[offset:offset+4])[0]
            offset += 4
            classes.append({
                'refTypeTag': ref_type_tag,
                'typeID': type_id,
                'signature': signature,
                'status': status,
            })

        return classes

class JdwpSession():
    HANDSHAKE = b'JDWP-Handshake'

    def __init__(self, host: str = 'localhost', port: int = 8700):
        self.host = host
        self.port = port
        self.packet_id = 1

        self.VirtualMachine = SimpleNamespace()
        self.VirtualMachine.AllClasses = VirtualMachine_AllClasses(self)


    async def init(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

        self.writer.write(JdwpSession.HANDSHAKE)
        await self.writer.drain()
        resp = await self.reader.readexactly(len(JdwpSession.HANDSHAKE))
        if resp != JdwpSession.HANDSHAKE:
            raise RuntimeError("JDWP Handshake Failed.")
        print("JDWP Handshake Successful.")


    async def _send_packet(self, packet_id, command_set, command, data=b''):

        length = 11 + len(data)
        flags = 0x00
        packet = struct.pack('>IIBBB', length, packet_id, flags, command_set, command)
        self.writer.write(packet)
        await self.writer.drain()
        return packet_id + 1


    async def _read_reply(self):
        header = await self.reader.readexactly(11)
        length, packet_id, flags, error_code = struct.unpack('>IIBH', header)
        data_length = length - 11
        data = await self.reader.readexactly(data_length)
        if error_code != 0:
            raise RuntimeError(f"JDWP Error Code: {error_code}")
        return data, packet_id, error_code


class Adb_Forward():

    def __init__(self, adb: 'Adb', local: str, remote: str):
        self.adb = adb
        self.local = local
        self.remote = remote

    async def run() -> None:
        
        self.adb.init()
        
        forward_cmd = f"host:forward:tcp:{local};jdwp:{remote}"
        await self.adb._send_command(forward_cmd)

        resp = await self.adb.reader.readexactly(4)
        if resp != b"OKAY":
            raise RuntimeError(f"Forward command failed: {resp}")

        self.adb._fini()


class Adb_Shell():

    def __init__(self, adb: 'Adb', cmd: str):
        self.adb = adb
        self.cmd

    async def run() -> str:
        
        self.adb.init()
    
        shell_cmd = f"shell:{self.cmd}"
        await self.adb._send_command(shell_cmd)

        await self.adb._check_resp_ok()
        
        output = []
        while True:
            chunk = await self.adb.reader.read(4096)
            if not chunk:
                break
            output.append(chunk.decode(errors='replace'))

        self.adb._fini()
        return ''.join(output)
    

class Adb():

    def __init__(self, host: str = 'localhost', port: int = 5037, serial: str = 'localhost:5554'):
        self.host = host
        self.port = port
        self.serial = serial

        self.Forward = Adb_Forward(self)
        self.Shell = Adb_Shell(self)

    async def init(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

        if serial:
            transport_cmd = f"host:transport:{serial}"
            self.writer.write(frame_command(transport_cmd))
            await self.writer.drain()

            resp = await self.reader.readexactly(4)
            if resp != b"OKAY":
                raise RuntimeError(f"Failed to select device {serial}: {resp}")

    @staticmethod
    def _frame_command(cmd: str) -> bytes:
        length = len(cmd)
        return f"{length:04X}".encode() + cmd.encode()

    def _send_command(self, cmd):
        self.writer.write(Adb._frame_command(cmd))
        await self.writer.drain()

    def _check_resp_ok(self):
        resp = await self.reader.readexactly(4)
        if resp != b"OKAY":
            raise RuntimeError(f"Command failed: {resp}")
    
    def _fini(self):
        self.writer.close()
        await self.writer.wait_closed()


'''
async def adb_forward_command(local: str, remote: str, serial: str = None) -> None:
    reader, writer = await asyncio.open_connection(ADB_HOST, ADB_PORT)

    if serial:
        transport_cmd = f"host:transport:{serial}"
        writer.write(frame_command(transport_cmd))
        await writer.drain()

        resp = await reader.readexactly(4)
        if resp != b"OKAY":
            raise RuntimeError(f"Failed to select device {serial}: {resp}")
    
    forward_cmd = f"host:forward:tcp:{local};jdwp:{remote}"
    writer.write(frame_command(forward_cmd))
    await writer.drain()

    resp = await reader.readexactly(4)
    if resp != b"OKAY":
        raise RuntimeError(f"Forward command failed: {resp}")

    writer.closed()
    await writer.wait_closed()


async def adb_shell_command(command: str, serial: str = None) -> str:
    reader, writer = await asyncio.open_connection(ADB_HOST, ADB_PORT):

    if serial:
        transport_cmd = f"host:transport:{serial}"
        writer.write(frame_command(transport_cmd))
        await writer.drain()

        resp = await reader.readexactly(4)
        if resp != b"OKAY":
            raise RuntimeError(f"Failed to select device {serial}: {resp}")
    
    shell_cmd = f"shell:{command}"
    writer.write(frame_command(shell_cmd))
    await writer.drain()

    resp = await reader.readexactly(4)
    if resp != b"OKAY":
        raise RuntimeError(f"Shell command failed: {resp}")
    
    output = []
    while True:
        chunk = await reader.read(4096)
        if not chunk:
            break
        output.append(chunk.decode(errors='replace'))

    writer.close()
    await writer.wait_closed()
    return ''.join(output)


async def main():

    output = await adb_shell_command("ps -A", serial=DEVICE_SERIAL)
    pid = -1
    for line in output.split('\n'):
        if line.find('sh.kau.playground') < 0:
            continue
        pid = line.split()[1]
    if pid == -1:
        print("Failed to find target pid.")
        exit(-1)

    print(f"Target pid: {pid}")

    await adb_forward_command(local="8700", remote=pid, serial=DEVICE_SERIAL)

    reader, writer = await asyncio.open_connection(JDWP_HOST, JDWP_PORT)

    try:
        await jdwp_handshake(reader, writer)
        classes = await jdwp_list_classes(reader, writer)
        print("Loaded classes:")
        for c in classes:
            if c['signature'].find('sh/kau') == -1:
                continue
            print(c)
    finally:
        writer.close()
        await writer.wait_closed()
'''



async def main2():
    
    adb = Adb(host='localhost', port=8700, serial='localhost:5554')
    adb.Shell()
    await Adb.Shell().run()
    await Adb.Forward().run()

    jdwp = JdwpSession().init()
    await jdwp.VirtualMachine.AllClasses().run()

