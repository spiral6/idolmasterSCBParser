import streamutility
import scb
import json
import struct

def constructMSGBlock(section, old_script: scb.Scb, new_script, translated_dialogue_json: json):
    streamutility.writeStrToLong(new_script, section.label)
    streamutility.writePadding(new_script, 4, streamutility.Padding.zero)
    
    new_script.write(old_script.msg_block.meta)
    
    streamutility.writeHexToShort(new_script, old_script.msg_block.dialogue_strings_count)
    streamutility.writePadding(new_script, 4, streamutility.Padding.zero)

    dialogue_length = 0
    for dialogue in translated_dialogue_json['strings']:
        dialogue = bytes(dialogue, "utf-16-be")
        dialogue_decoded = dialogue.decode("utf-16-be")
        dialogue_length += len(dialogue) + 2 # +2 includes \0

    streamutility.writeHexToShort(new_script, dialogue_length)
    streamutility.writePadding(new_script, 2, streamutility.Padding.zero)

    streamutility.writeHexToShort(new_script, old_script.msg_block.len_msgs_header)
    new_script.write(old_script.msg_block.len_msgs_header_padding)

    offset = 0
    for dialogue in translated_dialogue_json['strings']:        
        dialogue = bytes(dialogue, "utf-16-be")
        streamutility.writeHexToLong(new_script, len(dialogue) + 2) # +2 includes \0
        streamutility.writeHexToLong(new_script, offset)
        offset += len(dialogue) + 2 # +2 includes \0
    
    padding_calc = len(translated_dialogue_json['strings'])
    streamutility.writePadding(new_script, (padding_calc * 8) % 16, streamutility.Padding.pre_MSG_padding)

    for dialogue in translated_dialogue_json['strings']:
        dialogue = bytes(dialogue, 'utf-16-be')
        new_script.write(dialogue)
        new_script.write(bytes('\0', 'utf-16-be'))

    streamutility.writePadding(new_script, dialogue_length % 16, streamutility.Padding.pre_MSG_padding)

    # TODO: return MSG block as byte array, and construct into byte array and not write directly to file.
