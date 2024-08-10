from file_formats import scb
from file_formats import scb0

import streamutility
import json
import io
import pathlib

def constructMSGBlock(scb0_file: pathlib.Path, translated_dialogue_json: json) -> io.BytesIO:
    MSGBlock = io.BytesIO()

    file = scb0_file.name

    old_script = scb0.Scb0.from_file(file)
    section = old_script.sections[2]

    streamutility.writeStrToLong(MSGBlock, section.label)
    streamutility.writePadding(MSGBlock, 4, streamutility.Padding.zero)
    
    MSGBlock.write(old_script.msg_block.meta)
    
    streamutility.writeHexToShort(MSGBlock, old_script.msg_block.dialogue_strings_count)
    streamutility.writePadding(MSGBlock, 4, streamutility.Padding.zero)

    dialogue_length = 0
    for dialogue in translated_dialogue_json['strings']:
        dialogue = bytes(dialogue, "utf-16-be")
        dialogue_decoded = dialogue.decode("utf-16-be")
        dialogue_length += len(dialogue) + 2 # +2 includes \0

    streamutility.writeHexToShort(MSGBlock, dialogue_length)
    streamutility.writePadding(MSGBlock, 2, streamutility.Padding.zero)

    streamutility.writeHexToShort(MSGBlock, old_script.msg_block.len_msgs_header)
    MSGBlock.write(old_script.msg_block.len_msgs_header_padding)

    offset = 0
    for dialogue in translated_dialogue_json['strings']:        
        dialogue = bytes(dialogue, "utf-16-be")
        streamutility.writeHexToLong(MSGBlock, len(dialogue) + 2) # +2 includes \0
        streamutility.writeHexToLong(MSGBlock, offset)
        offset += len(dialogue) + 2 # +2 includes \0
    
    padding_calc = len(translated_dialogue_json['strings'])
    streamutility.writePadding(MSGBlock, (padding_calc * 8) % 16, streamutility.Padding.pre_MSG_padding)

    for dialogue in translated_dialogue_json['strings']:
        dialogue = bytes(dialogue, 'utf-16-be')
        MSGBlock.write(dialogue)
        MSGBlock.write(bytes('\0', 'utf-16-be'))

    padding_calc = 16 - (dialogue_length % 16)
    if padding_calc == 16: 
        padding_calc = 0

    streamutility.writePadding(MSGBlock, padding_calc, streamutility.Padding.pre_MSG_padding)

    return MSGBlock