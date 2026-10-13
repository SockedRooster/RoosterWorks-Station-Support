"""Strict reader for the static KSP v5 subset emitted by this project's converter.

Used for structural verification and geometry previews, not as a general MU importer.
"""
from pathlib import Path
import struct

class Reader:
    def __init__(self, path):
        self.data = path if isinstance(path, bytes) else Path(path).read_bytes()
        self.offset = 0
        self.nodes = []
        self.meshes = []
        self.materials = []
        self.textures = []
        assert self.i(2) == (76543, 5), 'Bad MU header'
        self.name = self.string()
        self.node(None)
        assert self.offset == len(self.data), 'Unread trailing MU data'

    def unpack(self, fmt, count=1):
        fmt = '<' + fmt*count
        result = struct.unpack_from(fmt, self.data, self.offset)
        self.offset += struct.calcsize(fmt)
        return result[0] if count == 1 else result

    def i(self, count=1): return self.unpack('i', count)
    def f(self, count=1): return self.unpack('f', count)
    def b(self): return self.unpack('B')
    def string(self):
        length = shift = 0
        while True:
            b = self.b()
            length |= (b & 127) << shift
            if b < 128: break
            shift += 7
            assert shift < 35
        value = self.data[self.offset:self.offset+length].decode('utf-8')
        self.offset += length
        return value

    def node(self, parent):
        start = self.offset
        node = dict(name=self.string(), pos=self.f(3), rot=self.f(4), scale=self.f(3), parent=parent)
        node['start'] = start
        self.nodes.append(node)
        mesh = None
        while self.offset < len(self.data):
            code = self.i()
            if code == 0: self.node(node)
            elif code == 1:
                node['end'] = self.offset
                return
            elif code == 24:
                node['tag'], node['layer'] = self.string(), self.i()
            elif code == 28:
                node['trigger'], node['size'], node['center'] = self.b(), self.f(3), self.f(3)
            elif code == 7:
                assert self.i() == 13
                nv, ns = self.i(2)
                assert ns == 1
                mesh = dict(node=node)
                while True:
                    c = self.i()
                    if c == 22: break
                    if c == 14: mesh['verts'] = [self.f(3) for _ in range(nv)]
                    elif c == 15: mesh['uv'] = [self.f(2) for _ in range(nv)]
                    elif c == 17: mesh['normals'] = [self.f(3) for _ in range(nv)]
                    elif c == 19:
                        ni = self.i()
                        assert ni % 3 == 0
                        mesh['tris'] = [self.i(3) for _ in range(ni//3)]
                    else: raise ValueError(f'Unexpected mesh record {c}')
                self.meshes.append(mesh)
            elif code == 8:
                assert mesh is not None
                mesh['shadow'] = (self.b(), self.b())
                assert self.i() == 1
                mesh['material_offset'] = self.offset
                mesh['material'] = self.i()
            elif code == 10:
                for _ in range(self.i()):
                    material = dict(name=self.string(), shader=self.string(), props={})
                    for _ in range(self.i()):
                        key, kind = self.string(), self.i()
                        if kind == 0: val = self.f(4)
                        elif kind == 4: val = (self.i(), self.f(2), self.f(2))
                        else: raise ValueError(f'Unexpected material property {kind}')
                        material['props'][key] = val
                    self.materials.append(material)
            elif code == 12:
                for _ in range(self.i()): self.textures.append((self.string(), self.i()))
            else: raise ValueError(f'Unexpected record {code} at {self.offset}')

    @staticmethod
    def armored(mesh):
        node = mesh['node']
        while node:
            if node['name'] in ('ArmorPanels','ArmorPanelsGrey'): return True
            node = node['parent']
        return False
