# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Scb(KaitaiStruct):
    """Idolmaster SCB file. Contains game dialogue, scripts, etc.
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self._raw_header_cache = self._io.read_bytes(240)
        _io__raw_header_cache = KaitaiStream(BytesIO(self._raw_header_cache))
        self.header_cache = Scb.HeaderCache(_io__raw_header_cache, self, self._root)
        self._raw_sections = []
        self.sections = []
        for i in range(7):
            self._raw_sections.append(self._io.read_bytes(32))
            _io__raw_sections = KaitaiStream(BytesIO(self._raw_sections[i]))
            self.sections.append(Scb.Section(_io__raw_sections, self, self._root))

        self.cmd_block = self._io.read_bytes(self.sections[0].len_section)
        self.lbl_block = self._io.read_bytes(self.sections[1].len_section)
        self._raw_msg_block = self._io.read_bytes(self.sections[2].len_section)
        _io__raw_msg_block = KaitaiStream(BytesIO(self._raw_msg_block))
        self.msg_block = Scb.MsgBlock(_io__raw_msg_block, self, self._root)
        self.vcn_block = self._io.read_bytes(self.sections[3].len_section)
        self.lbn_block = self._io.read_bytes(self.sections[4].len_section)
        self.rsc_block = self._io.read_bytes(self.sections[5].len_section)
        self.rsn_block = self._io.read_bytes(self.sections[6].len_section)
        self.scb_padding = self._io.read_bytes_full()

    class HeaderCache(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = self._io.read_bytes(12)
            self.num_files = self._io.read_u4be()
            self.header_cache_padding = self._io.read_bytes(32)
            self.ofs_entry = self._io.read_u4be()
            self.ofs_msg = self._io.read_u4be()
            self.ofs_file = self._io.read_u4be()
            self.header_cache_padding_2 = self._io.read_bytes(4)
            self._raw_files = []
            self.files = []
            for i in range(self.num_files):
                self._raw_files.append(self._io.read_bytes(32))
                _io__raw_files = KaitaiStream(BytesIO(self._raw_files[i]))
                self.files.append(Scb.PacFile(_io__raw_files, self, self._root))


        @property
        def scb_section(self):
            """SCB section. Subsection of header cache.
            """
            if hasattr(self, '_m_scb_section'):
                return self._m_scb_section

            io = self._root._io
            _pos = io.pos()
            io.seek((144 + self.files[0].ofs_file))
            self._m_scb_section = io.read_bytes(112)
            io.seek(_pos)
            return getattr(self, '_m_scb_section', None)

        @property
        def file_name(self):
            """File name. Inside of header cache.
            """
            if hasattr(self, '_m_file_name'):
                return self._m_file_name

            _pos = self._io.pos()
            self._io.seek(176)
            self._m_file_name = (self._io.read_bytes_term(0, False, True, True)).decode(u"ASCII")
            self._io.seek(_pos)
            return getattr(self, '_m_file_name', None)


    class DialogueString(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.len_dialogue_string = self._io.read_u4be()
            self.ofs_dialogue_string = self._io.read_u4be()

        @property
        def body(self):
            """Dialogue string body. Contains the literal dialogue string. 
            Encoded in UTF-16BE. Position is calculated by adding 48 bytes (the 
            MSG block header), and then the the dialogue string offset to the end 
            of the meta block offset. Meta block contains lengths and offsets 
            for each string, and its size/end of offset is 8 bytes multiplied by 
            number of dialogue strings + padding."""
            if hasattr(self, '_m_body'):
                return self._m_body

            _pos = self._io.pos()
            self._io.seek((((48 + (len(self._parent.dialogue_strings) * 8)) + (len(self._parent.dialogue_strings_block_padding) - 1)) + self.ofs_dialogue_string))
            self._m_body = (self._io.read_bytes(self.len_dialogue_string)).decode(u"utf-16be")
            self._io.seek(_pos)
            return getattr(self, '_m_body', None)


    class Section(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.label = (self._io.read_bytes(4)).decode(u"ASCII")
            self.label_padding = self._io.read_bytes(4)
            self.len_section = self._io.read_u4be()
            self.ofs_section = self._io.read_u4be()
            self.padding = self._io.read_bytes_full()

        @property
        def block(self):
            if hasattr(self, '_m_block'):
                return self._m_block

            io = self._root._io
            _pos = io.pos()
            io.seek((144 + self.ofs_section))
            self._m_block = io.read_bytes(self.len_section)
            io.seek(_pos)
            return getattr(self, '_m_block', None)


    class PacFile(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.filesize_padding = self._io.read_bytes(8)
            self.len_file = self._io.read_u4be()
            self.ofs_file = self._io.read_u4be()
            self.fn_index = self._io.read_u4be()
            self.fp_index = self._io.read_u4be()
            self.file_meta_padding = self._io.read_bytes_full()

        @property
        def file(self):
            if hasattr(self, '_m_file'):
                return self._m_file

            io = self._root._io
            _pos = io.pos()
            io.seek((144 + self.ofs_file))
            self._m_file = io.read_bytes(self.len_file)
            io.seek(_pos)
            return getattr(self, '_m_file', None)


    class MsgBlock(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = (self._io.read_bytes(8)).decode(u"ASCII")
            self.meta = self._io.read_bytes(24)
            self.dialogue_strings_count = self._io.read_u2be()
            self.dialogue_strings_count_padding = self._io.read_bytes(4)
            self.len_dialogue_strings = self._io.read_u2be()
            self.len_dialogue_strings_padding = self._io.read_bytes(2)
            self.len_msgs_header = self._io.read_u2be()
            self.len_msgs_header_padding = self._io.read_bytes(4)
            self.dialogue_strings_block = Scb.DialogueStringsBlock(self._io, self, self._root)


    class DialogueStringsBlock(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dialogue_strings = []
            for i in range(self._parent.dialogue_strings_count):
                self.dialogue_strings.append(Scb.DialogueString(self._io, self, self._root))

            self.dialogue_strings_block_padding = []
            i = 0
            while True:
                _ = self._io.read_bytes(1)
                self.dialogue_strings_block_padding.append(_)
                if _ != b"\xCD":
                    break
                i += 1



