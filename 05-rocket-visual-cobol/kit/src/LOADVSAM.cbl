       IDENTIFICATION DIVISION.
       PROGRAM-ID. LOADVSAM.
      *---------------------------------------------------------------
      * Builds the indexed files (stand-ins for the VSAM KSDS
      * clusters) from the text files, like IDCAMS REPRO in the
      * CardDemo JCL. Keys match the SELECTs in CBACT04C.
      *---------------------------------------------------------------
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT TCAT-IN  ASSIGN TO TCATIN
                  ORGANIZATION LINE SEQUENTIAL.
           SELECT XREF-IN  ASSIGN TO XREFIN
                  ORGANIZATION LINE SEQUENTIAL.
           SELECT ACCT-IN  ASSIGN TO ACCTIN
                  ORGANIZATION LINE SEQUENTIAL.
           SELECT DISC-IN  ASSIGN TO DISCIN
                  ORGANIZATION LINE SEQUENTIAL.
           SELECT TCAT-OUT ASSIGN TO TCATBALF
                  ORGANIZATION INDEXED ACCESS SEQUENTIAL
                  RECORD KEY TC-KEY.
           SELECT XREF-OUT ASSIGN TO XREFFILE
                  ORGANIZATION INDEXED ACCESS SEQUENTIAL
                  RECORD KEY XR-CARD
                  ALTERNATE RECORD KEY XR-ACCT.
           SELECT ACCT-OUT ASSIGN TO ACCTFILE
                  ORGANIZATION INDEXED ACCESS SEQUENTIAL
                  RECORD KEY AC-ID.
           SELECT DISC-OUT ASSIGN TO DISCGRP
                  ORGANIZATION INDEXED ACCESS SEQUENTIAL
                  RECORD KEY DG-KEY.
       DATA DIVISION.
       FILE SECTION.
       FD  TCAT-IN.
       01  TCAT-IN-REC             PIC X(50).
       FD  XREF-IN.
       01  XREF-IN-REC             PIC X(50).
       FD  ACCT-IN.
       01  ACCT-IN-REC             PIC X(300).
       FD  DISC-IN.
       01  DISC-IN-REC             PIC X(50).
       FD  TCAT-OUT.
       01  TC-REC.
           05  TC-KEY              PIC X(17).
           05  FILLER              PIC X(33).
       FD  XREF-OUT.
       01  XR-REC.
           05  XR-CARD             PIC X(16).
           05  FILLER              PIC X(09).
           05  XR-ACCT             PIC X(11).
           05  FILLER              PIC X(14).
       FD  ACCT-OUT.
       01  AC-REC.
           05  AC-ID               PIC X(11).
           05  FILLER              PIC X(289).
       FD  DISC-OUT.
       01  DG-REC.
           05  DG-KEY              PIC X(16).
           05  FILLER              PIC X(34).
       WORKING-STORAGE SECTION.
       01  WS-EOF                  PIC X.
       01  WS-CNT                  PIC 9(5).
       PROCEDURE DIVISION.
           OPEN INPUT TCAT-IN OUTPUT TCAT-OUT
           MOVE 'N' TO WS-EOF MOVE 0 TO WS-CNT
           PERFORM UNTIL WS-EOF = 'Y'
              READ TCAT-IN AT END MOVE 'Y' TO WS-EOF
                NOT AT END
                   WRITE TC-REC FROM TCAT-IN-REC
                   ADD 1 TO WS-CNT
              END-READ
           END-PERFORM
           DISPLAY 'TCATBALF loaded: ' WS-CNT
           CLOSE TCAT-IN TCAT-OUT
           OPEN INPUT XREF-IN OUTPUT XREF-OUT
           MOVE 'N' TO WS-EOF MOVE 0 TO WS-CNT
           PERFORM UNTIL WS-EOF = 'Y'
              READ XREF-IN AT END MOVE 'Y' TO WS-EOF
                NOT AT END
                   WRITE XR-REC FROM XREF-IN-REC
                   ADD 1 TO WS-CNT
              END-READ
           END-PERFORM
           DISPLAY 'XREFFILE loaded: ' WS-CNT
           CLOSE XREF-IN XREF-OUT
           OPEN INPUT ACCT-IN OUTPUT ACCT-OUT
           MOVE 'N' TO WS-EOF MOVE 0 TO WS-CNT
           PERFORM UNTIL WS-EOF = 'Y'
              READ ACCT-IN AT END MOVE 'Y' TO WS-EOF
                NOT AT END
                   WRITE AC-REC FROM ACCT-IN-REC
                   ADD 1 TO WS-CNT
              END-READ
           END-PERFORM
           DISPLAY 'ACCTFILE loaded: ' WS-CNT
           CLOSE ACCT-IN ACCT-OUT
           OPEN INPUT DISC-IN OUTPUT DISC-OUT
           MOVE 'N' TO WS-EOF MOVE 0 TO WS-CNT
           PERFORM UNTIL WS-EOF = 'Y'
              READ DISC-IN AT END MOVE 'Y' TO WS-EOF
                NOT AT END
                   WRITE DG-REC FROM DISC-IN-REC
                   ADD 1 TO WS-CNT
              END-READ
           END-PERFORM
           DISPLAY 'DISCGRP  loaded: ' WS-CNT
           CLOSE DISC-IN DISC-OUT
           GOBACK.
