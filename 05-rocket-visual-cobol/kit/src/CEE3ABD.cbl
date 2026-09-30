       IDENTIFICATION DIVISION.
       PROGRAM-ID. CEE3ABD.
      * Stand-in for the z/OS Language Environment abend service.
       DATA DIVISION.
       LINKAGE SECTION.
       01  ABCODE                  PIC S9(9) BINARY.
       01  TIMING                  PIC S9(9) BINARY.
       PROCEDURE DIVISION USING ABCODE TIMING.
           DISPLAY 'CEE3ABD: USER ABEND ' ABCODE
           STOP RUN RETURNING 16.
