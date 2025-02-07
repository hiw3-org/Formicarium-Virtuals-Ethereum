G00 X0 Y0
G01 X0 Y20
G01 X25 Y20
G01 X25 Y0
G01 X0 Y0
M30
M400      ; Wait for moves to complete
M104 S0   ; Turn off the hotend
M140 S0   ; Turn off the heated bed
M84       ; Disable motors
M73 P100 R0;

