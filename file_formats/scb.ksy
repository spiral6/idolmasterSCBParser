meta:
  id: scb
  endian: be

doc: |
  Idolmaster SCB file. Contains game dialogue, scripts, etc.

seq:
  # - id: initialization_vector
  #   size: 16
  #   doc: |
  #     Initialization vector for AES encyption for SCB file.
  - id: header_cache
    size: 240
    type: header_cache
    doc: | 
      Header cache. Contains file name, etc.
  - id: sections
    size: 32
    type: section
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
      - id: header
        size: 12
      - id: num_files
        type: u4be
      - id: header_cache_padding
        size: 32
      - id: ofs_entry
        type: u4be
      - id: ofs_msg
        type: u4be
      - id: ofs_file
        type: u4be
      - id: header_cache_padding_2
        size: 4
      - id: files
        size: 32
        type: pac_file
        repeat: expr
        repeat-expr: num_files
      
    instances:
      scb_section:
        io: _root._io
        pos: 144 + files[0].ofs_file
        size: 112
        doc: |
          SCB section. Subsection of header cache.
      file_name:
        pos: 176
        type: strz
        encoding: ASCII
        doc: | 
          File name. Inside of header cache.
  
  pac_file:
    seq:
      - id: filesize_padding
        size: 8
      - id: len_file
        type: u4be
      - id: ofs_file
        type: u4be
      - id: fn_index
        type: u4be
      - id: fp_index
        type: u4be
      - id: file_meta_padding
        size-eos: true
    instances:
      file: 
        io: _root._io
        pos: _parent.ofs_file + ofs_file
        size: len_file
  
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
        size: '((dialogue_strings.size * 8) % 16 == 0) ? 0 : (16 - (dialogue_strings.size * 8) % 16)'

  dialogue_string:
    seq:
      - id: len_dialogue_string
        type: u4
      - id: ofs_dialogue_string
        type: u4
    instances:
      body:
        # io: _root._io
        pos: 48 + (_parent.dialogue_strings.size * 8) + _parent.dialogue_strings_block_padding.size + ofs_dialogue_string #+ (_parent.dialogue_strings_block_padding.size - 1)
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