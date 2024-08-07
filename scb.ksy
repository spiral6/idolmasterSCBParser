meta:
  id: scb
  endian: be
seq:
  - id: initialization_vector
    size: 16
    doc: |
      Initialization vector for AES encyption for SCB file.
  - id: header_cache
    size: 240
    type: header_cache
    doc: | 
      Header cache. Contains file name, etc.
  - id: sections
    type: section
    size: 32
    repeat: expr
    repeat-expr: 7
    doc: |
      File sections
  - id: cmd_block
    size: sections[0].len_section
    doc: |
      CMD block struct.
  - id: lbl_block
    size: sections[1].len_section
    doc: |
      LBL block struct.
  - id: msg_block
    size: sections[2].len_section
    type: msg_block
    doc: |
      MSG block struct. 0x90 = 144, SCB block starts at 0x90.
  - id: vcn_block
    size: sections[3].len_section
  - id: lbn_block
    size: sections[4].len_section
  - id: rsc_block
    size: sections[5].len_section
  - id: rsn_block
    size: sections[6].len_section
  - id: scb_padding
    size-eos: true

types:
  header_cache:
    seq:
      - id: header_cache
        size-eos: true
    instances:
      scb_section:
        pos: 128
        size: 112
        doc: |
          SCB section. Subsection of header cache.
      file_name:
        pos: 176
        type: strz
        encoding: ASCII
        doc: | 
          File name. Inside of header cache.
  section:
    seq:
      - id: label
        size: 4
        type: str
        encoding: ASCII
      - id: label_padding
        size: 4
      - id: len_section
        type: u4be
      - id: ofs_section
        type: u4be
      - id: padding
        size-eos: true
    instances:
      block:
        io: _root._io
        pos: 144 + ofs_section
        size: len_section
        
  msg_block:
    seq:
      - id: header
        size: 8
        type: str
        encoding: ASCII
      - id: meta
        size: 24
      - id: dialogue_strings_count
        type: u2
      - id: dialogue_strings_count_padding
        size: 4
      - id: len_dialogue_strings
        type: u2
      - id: len_dialogue_strings_padding
        size: 2
      - id: len_msgs_header
        type: u2
      - id: len_msgs_header_padding
        size: 4
      - id: dialogue_strings_block
        type: dialogue_strings_block

  dialogue_strings_block:
    seq:
      - id: dialogue_strings
        type: dialogue_string
        repeat: expr
        repeat-expr: _parent.dialogue_strings_count
      - id: dialogue_strings_block_padding
        size: 1
        repeat: until
        repeat-until: _ != [0xcd]

  dialogue_string:
    seq:
      - id: len_dialogue_string
        type: u4
      - id: ofs_dialogue_string
        type: u4
    instances:
      body:
        # io: _root._io
        pos: 48 + (_parent.dialogue_strings.size * 8) + (_parent.dialogue_strings_block_padding.size - 1) + ofs_dialogue_string
        size: len_dialogue_string
        type: str
        encoding: utf-16be
        doc: | 
          Dialogue string body. Contains the literal dialogue string. 
          Encoded in UTF-16BE. Position is calculated by adding 48 bytes (the 
          MSG block header), and then the the dialogue string offset to the end 
          of the meta block offset. Meta block contains lengths and offsets 
          for each string, and its size/end of offset is 8 bytes multiplied by 
          number of dialogue strings + padding.

doc: |
  Idolmaster SCB file. Contains game dialogue, scripts, etc.
