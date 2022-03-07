import struct
from typing import List, Tuple, BinaryIO


def main(infiles: List[str], outfile: str, n: int) -> None:
    size_x, size_y = None, None
    with open(outfile, 'wb') as ntf:
        for i in range(n):
            print(f'processing file {i+1}/{n}')
            with open(infiles[i], 'rb') as jxf:
                if i == 0:
                    print(f'=> reading and parsing .jxf header')
                    jxf_header = jxf.read(56)
                    ntf_header, size_x, size_y = construct_ntf_header(jxf_header, n)
                    print(f'=> matrix dimensions: {size_x=}, {size_y=}')
                    print('=> writing .ntf header')
                    ntf.write(ntf_header)

                # write one row of data at a time
                jxf.seek(56)
                print(
                    '=> converting big endian .jxf data to little endian,',
                    'writing little endian data to .ntf file'
                )
                for row in range(size_y):
                    data = jxf.read(size_x * 4)
                    ntf.seek(128 + 4 * (row*size_x*n + i*size_x))
                    data = convert_block_to_little_endian(data, size_x)
                    ntf.write(data)


def construct_ntf_data(jxf: BinaryIO, size_x: int, size_y: int) -> bytearray:
    # 32bits = 4 bytes
    jxf.seek(56)
    big_endian_bytes = jxf.read(size_x * size_y * 4)
    data = []
    for i in range(size_x * size_y):
        data += itob(btoi(big_endian_bytes[4*i:4*i+4]))
    return bytearray(data)


def construct_ntf_header(jxf_header: bytes, n: int) -> Tuple[bytes, int, int]:
    # See below link for .jxf file header spec:
    # https://cycling74.com/sdk/max-sdk-8.2.0/chapter_jit_jxf.html#chapter_jit_jxf_api
    assert jxf_header[36:40] == b'FL32', 'matrix is not in float32 format'
    assert btoi(jxf_header[40:44]) == 1, 'matrix does not have planes == 1'
    assert btoi(jxf_header[44:48]) == 2, 'matrix is not 2-dimensional'
    assert btoi(jxf_header[48:52]) == btoi(jxf_header[52:56]), 'matrix rows != cols'

    size_x = btoi(jxf_header[48:52])
    size_y = btoi(jxf_header[52:56])

    # ntf file header
    bytes_arr = [
        *itob(0),           # 0x00  ByteOrder: 1 = little endian
        *itob(1),           # 0x04  VersionNumber: 1 = Reaktor 5+?
        *itob(1),           # 0x08  ArrayFormat: 1 = Float32Bits
        *itob(1),           # 0x0C  ???, default = 1
        *itob(size_x * n),  # 0x10  dx: X size (horizontal)
        *itob(size_y),      # 0x14  dy: Y size (vertical)
        *ftob(0),           # 0x18  Min: Value Property, default = 0.0
        *ftob(1),           # 0x1C  Max: Value Property, default = 1.0
        *ftob(0),           # 0x20  StepSize: Value Property, default = 0.0
        *ftob(0),           # 0x24  Default: Value Property, default = 0.0
        *itob(0),           # 0x28  DisplayFormat
        *itob(0),           # 0x2C  DefaultValueColor
        *itob(0),           # 0x30  MinValueColor
        *itob(0),           # 0x34  MaxValueColor
        *itob(0),           # 0x38  X-Units: 0=Index, 1=[0...1], 2=ms, 3=tempo ticks
        *ftob(48000),       # 0x3C  X-SamplesPerSecond
        *ftob(120),         # 0x40  X-BPM: default = 120.0
        *ftob(1),           # 0x44  X-SamplesPerTick: default = 1.0
        *itob(24),          # 0x48  X-TicksPerBeat: default = 24
        *itob(4),           # 0x4C  X-BeatsPerBar: default = 4
        *ftob(0),           # 0x50  X-Offset: default = 0.0
        *ftob(1),           # 0x54  X-CustomRange: default = 1.0
        *ftob(1),           # 0x58  X-CustomRatio: default = 1.0
        *itob(0),           # 0x5C  Y-Units: 0=Index, 1=[0...1]
        *ftob(48),          # 0x60  Y-SamplesPerSecond, default = 48.0
        *ftob(120),         # 0x64  Y-BPM: default = 120.0
        *ftob(1),           # 0x68  Y-SamplesPerTick: default = 1.0
        *itob(24),          # 0x6C  Y-TicksPerBeat: default = 24
        *itob(4),           # 0x70  Y-BeatsPerBar: default = 4
        *ftob(0),           # 0x74  Y-Offset: default = 0.0
        *ftob(1),           # 0x78  Y-CustomRange: default = 1.0
        *ftob(1),           # 0x7C  Y-CustomRatio: default = 1.0
    ]
    return bytearray(bytes_arr), size_x, size_y


def convert_block_to_little_endian(
    big_endian_bytes: bytes,
    size_in_bytes: int,
) -> bytearray:
    data = bytearray(big_endian_bytes)
    for i in range(size_in_bytes):
        big = data[4*i : 4*(i+1)]
        little = btoi(big).to_bytes(4, byteorder='little')
        data[4*i : 4*(i+1)] = little
    return data


def ftob(f: float) -> struct:
    return struct.pack('<f', f)


def itob(i: int) -> List[bytes]:
    return [*i.to_bytes(4, byteorder='little')]


def btoi(b: bytes) -> int:
    return int.from_bytes(b, byteorder='big')


if __name__ == '__main__':
    import sys
    infiles = sys.argv[1:]
    n = len(infiles)
    if n == 0:
        print(f"Usage: {__file__} <jxf_file1> ...")
        sys.exit(-1)
    elif n == 1:
        outfile = f'{infiles[0].rpartition(".")[0]}.ntf'
    else:
        outfile = f'{infiles[0].rpartition(".")[0].rpartition("_")[0]}.ntf'
    main(infiles, outfile, n)


"""
https://web.archive.org/web/20160407101527/http://www.semaforte.com/reaktor/files/NTF-Layout.htm

//----------------------------- NTF - file format ------------------------

// int   :  32-bit signed Integer
// float :  32-bit IEEE Floating Point


Adr   Type   Parameter          Comment
====  =====  =================  ==========================================

0x00  int    ByteOrder          // INTEL (little endian) = 0, MOTOROLA = 1
      int    VersionNumber      // Reaktor 6 = 1
      int    ArrayFormat        // Undefined = 0, Float32Bits = 1
      int    <unknown>          // always 1?
0x10  int    dx                 // X size (horizontal)
      int    dy                 // Y size (vertical)
      float  Min                // Value Properties
      float  Max                // Value Properties
0x20  float  StepSize           // Value Properties, generally 0
      float  Default            // Value Properties, generally 0
      int    DisplayFormat      // 0 = Numeric, 1 = Midi Note, 2 = %
      int    DefaultValueColor  // generally 0
0x30  int    MinValueColor      // generally 0
      int    MaxValueColor      // generally 0
      int    X-Units            // 0 = Index, 1 = [0...1], 2 = milliseconds, 3 = tempo ticks
      float  X-SamplesPerSecond // e.g. 48000.0
0x40  float  X-BPM              // e.g. 120.0
      float  X-SamplesPerTick   // generally 1.0
      int    X-TicksPerBeat     // generally 24
      int    X-BeatsPerBar      // generally 4
0x50  float  X-Offset           // generally 0.0
      float  X-CustomRange      // generally 1.0
      float  X-CustomRatio      // generally 1.0
      int    Y-Units            // 0 = Index, 1 = [0...1]
0x60  float  Y-SamplesPerSecond // generally 48.0
      float  Y-BPM              // generally 120.0
      float  Y-SamplesPerTick   // generally 1.0
      int    Y-TicksPerBeat     // generally 24
0x70  int    Y-BeatsPerBar      // generally 4
      float  Y-Offset           // generally 0.0
      float  Y-CustomRange      // generally 1.0
      float  Y-CustomRatio      // generally 1.0

// Start of table data strored as Float-32's. Data is saved by row.
// So...First row = (y0, x0), (y0,x1), (y0,x2)...(y1, x0), (y1,x1), (y1,x2)…etc
//   for (int y = 0; y < dy; y++)    // vertical
//   {
//     for (int x = 0; x < dx; x++)  // horizontal
//     {
//       Value[y][x]
//     }
//   }
0x80  float  Value[0][0]
      float  Value[0][1]
      float  Value[0][2]
             ...
      float  Value[0][dx-1]

      float  Value[1][0]
0x90  float  Value[1][1]
      float  Value[1][2]
             ...
      float  Value[1][dx-1]

      float  Value[2][0]
0xA0  float  Value[2][1]
      float  Value[2][2]
             ...
      float  Value[2][dx-1]

             ...

      float  Value[dy-1][0]
      float  Value[dy-1][1]
      float  Value[dy-1][2]
             ...
      float  Value[dy-1][dx-1]

// for questions please contact -> julian.ringel@native-instruments.de
"""
