meta:
  id: ntf_reaktor6
  file-extension: ntf
  endian: le
doc: |
  NTF is the Native Table Format for Reaktor.
seq:
  - id: header
    type: header
  - id: data
    size-eos: true
types:
  header:
    seq:
      - id: byte_order
        contents: [0, 0, 0, 0]
      - id: version_number
        contents: [1, 0, 0, 0]
      - id: array_format
        contents: [1, 0, 0, 0]
      - id: unknown_const
        contents: [1, 0, 0, 0]
      - id: x_size
        type: u4
      - id: y_size
        type: u4
      - id: min
        type: f4
      - id: max
        type: f4
      - id: step_size
        type: f4
      - id: default
        type: f4
      - id: display_format
        type: u4
      - id: default_value_color
        type: u4
      - id: min_value_color
        type: u4
      - id: max_value_color
        type: u4
      - id: x_units
        type: u4
      - id: x_samples_per_second
        type: f4
      - id: x_bpm
        type: f4
      - id: x_samples_per_tick
        type: f4
      - id: x_ticks_per_beat
        type: u4
      - id: x_beats_per_bar
        type: u4
      - id: x_offset
        type: f4
      - id: x_custom_range
        type: f4
      - id: x_custom_ratio
        type: f4
      - id: y_units
        type: u4
      - id: y_samples_per_second
        type: f4
      - id: y_bpm
        type: f4
      - id: y_samples_per_tick
        type: f4
      - id: y_ticks_per_beat
        type: u4
      - id: y_beats_per_bar
        type: u4
      - id: y_offset
        type: f4
      - id: y_custom_range
        type: f4
      - id: y_custom_ratio
        type: f4