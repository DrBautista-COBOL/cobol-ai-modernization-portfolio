       IDENTIFICATION DIVISION.
       PROGRAM-ID. RUNJOB.
      *---------------------------------------------------------------
      * Test driver - plays the role of the INTCALC JCL job:
      *   STEP 1  LOADVSAM  builds the indexed files (like IDCAMS REPRO)
      *   STEP 2  CBACT04C  the ORIGINAL program, unchanged, with
      *                     PARM='2022071800' as on the EXEC card
      *   STEP 3  UNLDACCT  unloads the updated account file to text
      *   STEP 4  UNLDTRAN  unloads the new transactions to text
      *---------------------------------------------------------------
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  EXTERNAL-PARMS.
           05  PARM-LENGTH         PIC S9(04) COMP VALUE 10.
           05  PARM-DATE           PIC X(10) VALUE '2022071800'.
       PROCEDURE DIVISION.
           DISPLAY '*** STEP 1: LOADVSAM ***'
           CALL 'LOADVSAM'
           DISPLAY '*** STEP 2: CBACT04C PARM=2022071800 ***'
           CALL 'CBACT04C' USING EXTERNAL-PARMS
           DISPLAY '*** STEP 3: UNLDACCT ***'
           CALL 'UNLDACCT'
           DISPLAY '*** STEP 4: UNLDTRAN ***'
           CALL 'UNLDTRAN'
           DISPLAY '*** JOB ENDED ***'
           STOP RUN.
