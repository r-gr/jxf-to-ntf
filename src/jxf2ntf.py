import struct


def ftob(f: float):
    #return int.to_bytes(int.from_bytes(struct.pack('<f', f), byteorder='little'))
    return struct.pack('<f', f)


def itob(i: int):
    return [*i.to_bytes(4, byteorder='little')]


def btoi(b: bytes):
    return int.from_bytes(b, byteorder='big')


def main(infile, outfile):
    # 32bits = 4 bytes
    with open(infile, 'rb') as f:
        header = f.read(48)
        assert header[36:40] == b'FL32'
        assert btoi(header[40:44]) == 1
        assert btoi(header[44:48]) == 2
        dims = btoi(header[44:48])
        dims = f.read(dims * 4)
        assert btoi(dims[0:4]) == btoi(dims[4:8])
        with open(outfile, 'wb') as g:
            # ntf file header
            size_x = btoi(dims[0:4])
            size_y = btoi(dims[4:8])
            bytes_arr = [
                *itob(0),       # ByteOrder: 1 = little endian
                *itob(1),       # VersionNumber: 1 = Reaktor 5+?
                *itob(1),       # ArrayFormat: 1 = Float32Bits
                *itob(1),       # ???
                *itob(size_x),  # 0x10 dx
                *itob(size_y),
                *ftob(0),       # Min = 0.0
                *ftob(1),       # Max = 1.0
                *ftob(0),       # 0x20 StepSize = 0.0
                *ftob(0),       # Default = 0
                *itob(0),
                *itob(0),
                *itob(0),       # 0x30 MinValueColor
                *itob(0),
                *itob(0),
                *ftob(48000),
                *ftob(120),     # 0x40 X-BPM
                *ftob(1),
                *itob(24),
                *itob(4),
                *ftob(0),       # 0x50 X-Offset
                *ftob(1),
                *ftob(1),
                *itob(0),
                *ftob(48),      # 0x60 Y-SamplesPerSecond
                *ftob(120),
                *ftob(1),
                *itob(24),
                *itob(4),       # 0x70 Y-BeatsPerBar
                *ftob(0),
                *ftob(1),
                *ftob(1),
            ]
            g.write(bytearray(bytes_arr))

            big_endian_bytes = f.read(size_x * size_y * 4)
            data = []
            for i in range(0, size_x * size_y):
                data.append(btoi(big_endian_bytes[4*i:4*i+4]))
            # data = [data[i:i+512] for i in range(0, len(data))]
            # data = [[data[j][i] for j in range(size_y)] for i in range(size_x)]
            # final_data = []
            # for row in data:
            #     for val in row:
            #         final_data += itob(val)
            # final_bytes = bytearray(final_data)
            # g.write(final_bytes)
            final_data = []
            for val in data:
                final_data += itob(val)
            g.write(bytearray(final_data))

if __name__ == '__main__':
    import sys
    infile = sys.argv[1]
    outfile = f'{infile.rpartition(".")[0]}.ntf'
    main(infile, outfile)


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
