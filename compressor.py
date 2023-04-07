import sys

with open(sys.argv[1]) as f:
    input_text = f.read()

# generate all tokens and offsets
tokens = []
for i in range(3, 5):
    window_size = i
    for j in range(len(input_text) - window_size):
        tokens.append((input_text[j:j + window_size], j))
print(f'Generated tokens: {len(tokens)} tkns')

# group all the tokens into a dictionary
grouped_tokens = {}
for token in tokens:
    if token[0] not in grouped_tokens:
        grouped_tokens[token[0]] = [token[1]]
    else:
        grouped_tokens[token[0]].append(token[1])
print(f'Grouped tokens: {len(grouped_tokens)} tkns')

# sort by descending, filtering out tokens with only two occurences
print('Sorting tokens')
sorted_tokens = dict(sorted(grouped_tokens.items(), key=lambda item: len(item[1]), reverse=True))
filtered_tokens = {k: v for k, v in sorted_tokens.items() if len(v) > 2}
print(f'Filtered tokens: {len(filtered_tokens)} tkns')

# adjust offsets for each token, removing tokens which are too far apart
print('Reducing offset sizes')
adjusted_tokens = {}
for token, offsets in filtered_tokens.items():
    new_offsets = []
    for i in range(len(offsets)):
        if i:
            diff = offsets[i] - offsets[i - 1]
            if diff < 256:
                new_offsets.append(diff)
        else:
            new_offsets.append(offsets[i])
    adjusted_tokens[token] = new_offsets

# refilter out tokens with only two occurrences
filtered_tokens = {k: v for k, v in adjusted_tokens.items() if len(v) > 2}
print(f'Refiltered tokens: {len(filtered_tokens)} tkns')


def overlaps(token1, off1: int, token2, offsets2):
    total_offset = 0
    for off2 in offsets2:
        total_offset += off2
        if off2 + total_offset <= off1 <= off2 + total_offset + len(token2):
            return True
        if off2 + total_offset <= off1 + len(token1) <= off2 + total_offset + len(token2):
            return True
    return False


# remove overlapping tokens
unique_tokens = {}
for token, offsets in filtered_tokens.items():
    unique_offsets = []
    total_offset = 0
    for off in offsets:
        total_offset += off
        is_offset_unique = True
        for u_token, u_offsets in unique_tokens.items():
            if overlaps(token, off + total_offset, u_token, u_offsets):
                is_offset_unique = False
                break
        if not is_offset_unique:
            break
        if is_offset_unique:
            unique_offsets.append(off)
    unique_tokens[token] = unique_offsets
print(f'Removed redundant tokens: {len(unique_tokens)} tkns')

filtered_tokens = {k: v for k, v in unique_tokens.items() if len(v) > 2}
print(f'Refiltered tokens: {len(filtered_tokens)} tkns')

with open('tokens.txt', 'w') as f:
    for key, value in filtered_tokens.items():
        f.write(f'{key}: {value}\n')

print('Compressing input text')
bytes_text = input_text.encode()
for token, offsets in filtered_tokens.items():
    total_offset = 0
    for offset in offsets:
        total_offset += offset
        bytes_text = bytes_text[:total_offset] + b'\x00' * len(token) + bytes_text[total_offset + len(token):]

compressed_text = bytes_text.translate(None, b'\x00')

print('Generating metadata')
metadata = b''
for token, offsets in filtered_tokens.items():
    token_data = token.encode()
    for offset in offsets:
        token_data += offset.to_bytes((offset.bit_length() // 8) + 1, 'big')
    token_data += b'\x00'
    metadata += token_data

print('Writing to file')
with open('compressed.txt', 'wb') as f:
    f.write(metadata + compressed_text)

size_before = len(input_text)
size_after = len(metadata) + len(compressed_text)
print(f'Size before: {size_before} bytes')
print(f'Size after: {size_after} bytes')
print(f'Saving: {size_before - size_after} bytes')
print(f'Compressed file by {round(100 - ((size_after / size_before) * 100), 3)}%')