       IDENTIFICATION DIVISION.
       PROGRAM-ID. UNLDTRAN.
      *---------------------------------------------------------------
      * Copies the interest transactions written by CBACT04C
      * (fixed 350-byte records) to a text file, one per line.
      * Binary zeros (LOW-VALUES) are shown as '~' so they are
      * visible in Notepad (see finding D4 in the portfolio).
      *---------------------------------------------------------------
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT TRAN-IN  ASSIGN TO TRANSACT
                  ORGANIZATION SEQUENTIAL.
           SELECT TRAN-OUT ASSIGN TO TRANOUT
                  ORGANIZATION LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD  TRAN-IN.
       01  TI-REC                  PIC X(350).
       FD  TRAN-OUT.
       01  TO-REC                  PIC X(350).
       WORKING-STORAGE SECTION.
       01  WS-EOF                  PIC X VALUE 'N'.
       01  WS-CNT                  PIC 9(5) VALUE 0.
       PROCEDURE DIVISION.
           OPEN INPUT TRAN-IN OUTPUT TRAN-OUT
           PERFORM UNTIL WS-EOF = 'Y'
              READ TRAN-IN AT END MOVE 'Y' TO WS-EOF
                NOT AT END
                   MOVE TI-REC TO TO-REC
                   INSPECT TO-REC REPLACING ALL LOW-VALUE BY '~'
                   WRITE TO-REC
                   ADD 1 TO WS-CNT
              END-READ
           END-PERFORM
           DISPLAY 'Transactions unloaded: ' WS-CNT
           CLOSE TRAN-IN TRAN-OUT
           GOBACK.
