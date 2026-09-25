       IDENTIFICATION DIVISION.
       PROGRAM-ID. RUNINT.
      * Test driver: stands in for the JCL EXEC card.
      * Passes PARM='2022071800' to CBACT04C exactly as z/OS would.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  EXTERNAL-PARMS.
           05  PARM-LENGTH         PIC S9(04) COMP VALUE 10.
           05  PARM-DATE           PIC X(10) VALUE '2022071800'.
       PROCEDURE DIVISION.
           CALL 'CBACT04C' USING EXTERNAL-PARMS
           STOP RUN.
