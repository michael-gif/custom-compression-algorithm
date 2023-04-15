import sys

with open(sys.argv[1], 'rb') as f:
    compressed_bytes = f.read()

metadata_end = compressed_bytes.index(b'\x02')
token_metadata = compressed_bytes[:metadata_end]
print('Extracted token metadata')
remaining = compressed_bytes[metadata_end + 1:]

temp = remaining.index(b'\x02')
counts_and_lengths = remaining[:temp]
print('Extracted frequency metadata')
remaining = remaining[temp + 1:]

temp = 0
tokens = []
for i in range(0, len(counts_and_lengths), 3):
    lengths_byte, count_bytes = counts_and_lengths[i], counts_and_lengths[i + 1: i + 3]
    length_1 = (lengths_byte >> 4) & 15  # high half
    length_2 = lengths_byte & 15  # low half
    count_1 = int(count_bytes[0])
    count_2 = int(count_bytes[1])

    index = 0
    for j in range(count_1):
        tokens.append(token_metadata[temp + index: temp + index + length_1])
        index += length_1

    temp += length_1 * count_1
    index = 0
    for j in range(count_2):
        tokens.append(token_metadata[temp + index: temp + index + length_2])
        index += length_2

    temp += length_2 * count_2
print('Reconstructed tokens')

print('Uncompressing bytes...')
decompressed = b''
i = 0
while i < len(remaining):
    byte = remaining[i]
    if byte & 128 == 128:
        pointer_bytes = remaining[i: i + 2]
        encoded_pointer = int.from_bytes(pointer_bytes, 'big')
        decoded_pointer = encoded_pointer ^ 0x8000
        decompressed += tokens[decoded_pointer]
        i += 2
        continue
    else:
        decompressed += byte.to_bytes(1, 'big')
        i += 1
print('Uncompressed bytes')

print('Writing to file')
with open('decompressed.txt', 'wb') as f:
    f.write(decompressed)
