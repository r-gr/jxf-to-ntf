meta:
  id: jxf
  file-extension: jxf
  endian: be
doc: |
  JXF is the Jitter matrix format for Max.
seq:
  - id: header
    type: header
  - id: data
    size-eos: true
types:
  header:
    seq:
      - id: group_id
        contents: 'FORM'
      - id: file_size
        type: u4
      - id: iff_type
        contents: 'JIT!'
      - id: format_chunk_id
        contents: 'FVER'
      - id: format_chunk_size
        contents: [0x00, 0x00, 0x00, 0x0c]
      - id: version
        contents: [0x3c, 0x93, 0xdc, 0x80]
      - id: matrix_chunk_id
        contents: 'MTRX'
      - id: matrix_chunk_size
        type: u4
      - id: matrix_offset
        type: u4
      - id: matrix_type
        contents: 'FL32'
      - id: plane_count
        type: u4
      - id: dim_count
        type: u4
      - id: dimensions
        type: u4
        repeat: expr
        repeat-expr: dim_count