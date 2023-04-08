# Single Threaded Tokenized Pointer Compression for Text (STTPCT)

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
The pointer is 16 bits, the first bit being a `1`, and the other 15 being an integer between `0` and `32768`.  
Example: `1000000000000110` -> First bit is `1`, the integer inside is `6`
- Generate the metadata for the file. Join all the patterns together, separated by null bytes.
- Concatenate the compressed text to the end of the metadata
- Write everything to file. Boom, compressed