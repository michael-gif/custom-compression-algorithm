# Single Threaded Pattern-Based Pointer Compression for Text (STPBPCT)
Compression algorithm that utilising a sliding window for repeated pattern identification, combined with 2 byte pointers which support a high capacity for patterns.

### Usage 
Compression:  
`python -m compressor bee_movie_script.txt`  
Output in `compressed.txt`

Decompression:  
`python -m decompressor compressed.txt`  
Output in `decompressed.txt`

### How it works
- Identify all possible tokens using a sliding window, including their offsets from 0, excluding tokens of length 1 and 2, because they are not compressable
- Group the tokens and their offsets
- Filter out tokens which won't contribute to reducing file size
- Flatten the filtered tokens into one list
- Sort that list in ascending order according to the offsets
- Remove any overlapping tokens
- Regroup the tokens into a dictionary
- Refilter the tokens
- Again, flatten and sort the tokens
- Loop through each token, and use it's offset to generate the compressed text. Replace the token with a 2 byte pointer.
- Generate the metadata for the file
- Concatenate the compressed text to the end of the metadata
- Write everything to file. Boom, compressed

### Pointers
Each pointer is 16 bits (2 bytes). The first bit is always a 1, in order to differentiate it from an ASCII character:  
`10000000 00000000`  
The rest of the 15 bits are used like a regular integer.  
A pointer containing the number 183 would look like:  
`10000000 10110111`  
A pointer containing the number 4286 would look like:  
`10010000 10111110`  
The max number a pointer can contain is 32768:  
`11111111 11111111`

The number the pointer contains is an index to an array of repeating strings in the file.
If a pointer contains the number `4286`, then it is pointing to the repeating token at index `4286`.

### Metadata
The repeating tokens are stored directly next to each other with no spaces. If you had two tokens `['sha', 'n g']`, they would be stored as `shan g`.
The tokens are sorted by length beforehand, in order to reduce the number of bytes required to store their frequencies.
The token bytes end with the separator byte `0x02`.  
Therfore `['sha', 'n g']` would be stored as: `73 68 61 6E 20 67 02`. Notice the `02` at the end.

In order to extract the tokens during decompression, the frequencies for the tokens are stored after the token bytes, after the `02` byte.
They are stored as 3 byte triples.
The first byte contains two lengths, with the second and third containing counts for each length respectively. 

If there are `10` tokens of length `3` characters, and `20` tokens of length `5` characters, then this would be stored as:  
`00110101 00001010 00010100`  
- The first byte can be split into halves to obtain the lengths  
`00110101 -> 0011 0101`, where `0011` is 3, and `0101` is 5.  
- The second byte `00001010` is the count `10`.  
- The third byte `00010100` is the count `20`.

So `00110101 00001010 00010100` can be read as length 3, count 10, length 5, count 20.
In hex: `35 0A 14 02`. Notice the `02` at the end, this signifies the end of the frequency bytes and the start of the compressed data.

Therefore the tokens `['sha', 'n g', 'abc']` would be stored as the folling in hex:  
`73 68 61 6E 20 67 61 62 63 02 30 03 00 02`  
- `73 68 61 6E 20 67 61 62 63` decodes to `'shan gabc'`
- `30 03 00` decodes to `00110000 00000011 00000000` which means length `3` count `3`, length `0` count `0`.
- The two `02` bytes are the separator bytes.

Thus `shan gabc` becomes `['sha', 'n g', 'abc']`

### Results
| Input file                   | Size before (bytes) | Size after (bytes) | Difference (bytes) | % Difference | Time taken (s) |
| ---------------------------- | ------------------- | ------------------ | ------------------ | ------------ | -------------- |
| `bee_movie_script.txt`       | 49473               | 42345              | 7128               | 14.408       | 0.095352       |
| `joker2019_movie_script.txt` | 226344              | 180588             | 45756              | 20.215       | 0.556383       |

Decompression happens extremely fast, trust me.