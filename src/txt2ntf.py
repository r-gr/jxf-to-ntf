import struct


def ftob(f: float):
    #return int.to_bytes(int.from_bytes(struct.pack('<f', f), byteorder='little'))
    return struct.pack('<f', f)


def itob(i: int):
    return (*i.to_bytes(4, byteorder='little'),)


def main(n, size, infile, outfile):
    # 32bits = 4 bytes
    with open(outfile, 'wb') as f:
        # ntf file header
        # size_x = [*size_x.to_bytes(4, byteorder='little')]
        size_y = size * n
        size_x = size
        # size_y = [*size_y.to_bytes(4, byteorder='little')]
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
        # import pdb; pdb.set_trace()
        f.write(bytearray(bytes_arr))
        for i in range(n):
            with open(f'{infile}_{i:02}.txt', 'r') as g:
                for l in g:
                    from itertools import chain
                    floats = [float(x) for x in l.strip().split('\t')]
                    floats_as_bytes = [ftob(val) for val in floats]
                    for val in floats_as_bytes:
                        f.write(val)

if __name__ == '__main__':
    import sys
    n = int(sys.argv[1])
    size = int(sys.argv[2])
    infile = sys.argv[3]
    outfile = f'{infile}.ntf'
    main(n, size, infile, outfile)


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
