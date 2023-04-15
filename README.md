# Single Threaded Pattern-Based Pointer Compression for Text (STPBPCT)
STPBPCT is a compression algorithm that uses a sliding window to identify repeated patterns and 2 byte pointers to represent them.

## Usage
To compress a file called `bee_movie_script.txt` run:
`python -m compressor bee_movie_script.txt`

The output will be saved in a file called `compressed.txt`.

To decompress the file, run:
`python -m decompressor compressed.txt`

The output will be saved in a file called `decompressed.txt`.

## How it works
1. Identify all possible tokens using a sliding window, excluding tokens of length 1 and 2, as they cannot be compressed.
2. Group the tokens and their offsets.
3. Filter out tokens that won't reduce the file size.
4. Flatten the filtered tokens into one list.
5. Sort the list in ascending order according to the offsets.
6. Remove any overlapping tokens.
7. Regroup the tokens into a dictionary.
8. Refilter the tokens.
9. Flatten and sort the tokens again.
10. Loop through each token, using its offset to generate compressed text. Replace the token with a 2 byte pointer.
11. Generate metadata for the file.
12. Concatenate the compressed text to the end of the metadata.
13. Write everything to file.

## Pointers
Each pointer is 16 bits (2 bytes), with the first bit always set to 1 to distinguish it from an ASCII character. The remaining 15 bits are used as a regular integer.
For example, a pointer with the value 183 would be represented as `10000000 10110111`, while a pointer with the value 4286 would be represented as `10010000 10111110`.
The maximum value that a pointer can hold is 32768, which is represented as `11111111 11111111`.

Each pointer points to an index in an array of repeating strings in the compressed file.
For instance, a pointer with the value 4286 points to the repeating token at index 4286.

## Metadata
The repeating tokens are stored directly next to each other without spaces. For example, if we have two tokens `['sha', 'n g']`, they would be stored as `'shan g'`.
The tokens are sorted by length beforehand to reduce the number of bytes required to store their frequencies.

The token bytes end with the separator byte `0x02`.
For example, `['sha', 'n g']` would be stored as `73 68 61 6E 20 67 02`.
Notice the `02` byte at the end.

To extract the tokens during decompression, their frequencies are stored after the token bytes, following the `02` byte.
The frequencies are stored as 3-byte triples, where the first byte contains two lengths, and the second and third bytes contain counts for each length, respectively.

For example, if we have 10 tokens of length 3 and 20 tokens of length 5, the frequencies would be stored as `00110101 00001010 00010100`.
The first byte can be split into halves to obtain the lengths, where `0011` is 3 and `0101` is 5.
The second byte `00001010` represents the count 10, and the third byte `00010100` represents the count 20.

Thus, `00110101 00001010 00010100` can be read as "length 3, count 10, length 5, count 20".
In hex, this is represented as `35 0A 14 02`.
The `02` byte signifies the end of the frequency bytes and the start of the compressed data.

Therefore, the tokens `['sha', 'n g', 'abc']` would be stored as `73 68 61 6E 20 67 61 62 63 02 30 03 00 02` in hex.
The first section of hex represents the token bytes, which decode to `shan gabc`.
The second section represents the frequency bytes, which decode to `00110000 00000011 00000000`, meaning length 3 count 3, length 0 count 0.
The two `02` bytes represent the separator bytes.
Using the token bytes `'shan gabc'` and the obtained frequencies `l:3 c:3, l:0 c:0`, one can obtain the tokens `['sha', 'n g', 'abc']`, which will be used during decompression.

## Results
The following table shows the results of compressing two input files using the STPBPCT algorithm:

| Input file                   | Size before (bytes) | Size after (bytes) | Difference (bytes) | % Difference | Time taken (s) |
| ---------------------------- | ------------------- | ------------------ | ------------------ | ------------ | -------------- |
| `bee_movie_script.txt`       | 49473               | 42345              | 7128               | 14.408       | 0.095352       |
| `joker2019_movie_script.txt` | 226344              | 180588             | 45756              | 20.215       | 0.556383       |