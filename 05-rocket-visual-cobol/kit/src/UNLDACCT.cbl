       IDENTIFICATION DIVISION.
       PROGRAM-ID. UNLDACCT.
      *---------------------------------------------------------------
      * Unloads the updated account file to text for comparison.
      *---------------------------------------------------------------
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT ACCT-IN  ASSIGN TO ACCTFILE
                  ORGANIZATION INDEXED ACCESS SEQUENTIAL
                  RECORD KEY AC-ID.
           SELECT ACCT-OUT ASSIGN TO ACCTOUT
                  ORGANIZATION LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD  ACCT-IN.
       01  AC-REC.
           05  AC-ID               PIC X(11).
           05  FILLER              PIC X(289).
       FD  ACCT-OUT.
       01  AO-REC                  PIC X(300).
       WORKING-STORAGE SECTION.
       01  WS-EOF                  PIC X VALUE 'N'.
       01  WS-CNT                  PIC 9(5) VALUE 0.
       PROCEDURE DIVISION.
           OPEN INPUT ACCT-IN OUTPUT ACCT-OUT
           PERFORM UNTIL WS-EOF = 'Y'
              READ ACCT-IN AT END MOVE 'Y' TO WS-EOF
                NOT AT END
                   WRITE AO-REC FROM AC-REC
                   ADD 1 TO WS-CNT
              END-READ
           END-PERFORM
           DISPLAY 'Accounts unloaded: ' WS-CNT
           CLOSE ACCT-IN ACCT-OUT
           GOBACK.
