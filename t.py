import struct

def decode_varint(data, offset):
    value = 0
    shift = 0
    while True:
        b = data[offset]
        value |= (b & 0x7F) << shift
        shift += 7
        offset += 1
        if not (b & 0x80):
            break
    return value, offset

# 从 hex.txt 文件中读取十六进制字符串
with open('hex.txt', 'r', encoding='utf-8') as f:
    hex_str = f.read().strip()
data = bytes.fromhex(hex_str.replace(' ', ''))

# 第一步：跳过第一个字段的结构
pos = 0
key1 = data[pos]
pos += 1
len1, pos = decode_varint(data, pos)
pos += len1

# 第二步：定位好友数据
key2 = data[pos]
assert key2 == 0x12, f"Tag 0x12 not found, got {hex(key2)}"
len2, pos = decode_varint(data, pos + 1)
content_start = pos
content_end = pos + len2

gids = []
pos = content_start
while pos < content_end:
    if data[pos] != 0x0A:
        break
    pos += 1
    entry_len, pos = decode_varint(data, pos)
    entry_end = pos + entry_len
    
    # 解析条目内的字段
    while pos < entry_end:
        tag, pos = decode_varint(data, pos)
        wire_type = tag & 0x07
        field_num = tag >> 3
        
        if field_num == 1 and wire_type == 0:  # 兼容以前的数据：Tag 1, varint
            gid, pos = decode_varint(data, pos)
            gids.append(gid)
        elif field_num == 4 and wire_type == 2:  # 新的数据：Tag 4, 字符串
            strlen, pos = decode_varint(data, pos)
            gid_str = data[pos:pos+strlen].decode('utf-8')
            gids.append(int(gid_str) if gid_str.isdigit() else gid_str)
            pos += strlen
        else:
            # 跳过未知的字段
            if wire_type == 0:
                _, pos = decode_varint(data, pos)
            elif wire_type == 1:
                pos += 8
            elif wire_type == 2:
                strlen, pos = decode_varint(data, pos)
                pos += strlen
            elif wire_type == 5:
                pos += 4
            else:
                break
                
    pos = entry_end

print(gids)  # 输出所有gid