ROCKET VISUAL COBOL KIT - CBACT04C (AWS CardDemo interest calculation)
Dr. Eduardo Bautista - portfolio project, Sessions 2-4

FOLDERS
  src\        CBACT04C.cbl  - ORIGINAL CardDemo program (unchanged, Apache 2.0)
              CVACT01Y.cpy CVACT03Y.cpy CVTRA01Y.cpy CVTRA02Y.cpy CVTRA05Y.cpy
                            - its five copybooks (unchanged)
              RUNJOB.cbl    - test driver: plays the INTCALC JCL job
                              (STEP 1 load, STEP 2 CBACT04C with PARM, STEP 3-4 unload)
              LOADVSAM.cbl  - builds the indexed files (stand-in for IDCAMS REPRO)
              CEE3ABD.cbl   - stand-in for the z/OS abend service
              UNLDACCT.cbl  - writes the updated accounts to acctdata-out.txt
              UNLDTRAN.cbl  - writes the new transactions to systran.txt
                              (binary zeros shown as '~', see finding D4)
  data\       tcatin.txt  xrefin.txt  acctin.txt  discin.txt  - input test data
              tcatin-PURPOSE.txt - why each test record exists
  expected\   results of the same job under GnuCOBOL (Step 4 of the portfolio):
              gnucobol-sysout.txt, gnucobol-acctdata-out.txt, gnucobol-systran.txt
  reference\  INTCALC.jcl - the original JCL, for comparison

WHAT THE JOB CREATES (in the run folder)
  TCATBALF.dat XREFFILE.dat ACCTFILE.dat DISCGRP.dat - indexed files (+ index companions)
  TRANSACT.dat                         - interest transactions (binary, 350 bytes)
  acctdata-out.txt, systran.txt        - readable results to compare with expected\

KEY SETTINGS IN VISUAL COBOL (Session 2)
  Dialect: Enterprise COBOL for z/OS   (directive DIALECT"ENTCOBOL")
  Extra directives: SIGN"EBCDIC"       (reads mainframe-style signs such as { and J)
                    ASSIGN"EXTERNAL"   (ASSIGN names are DD names, as on z/OS)
  Entry point / main program: RUNJOB
  Run working directory: the folder holding the data files
  "DD statements" (Run Configuration > Environment tab), because with the
  Enterprise COBOL dialect ASSIGN names are DD names, as in JCL:
    dd_TCATIN   = tcatin.txt          dd_TCATBALF = TCATBALF.dat
    dd_XREFIN   = xrefin.txt          dd_XREFFILE = XREFFILE.dat
    dd_ACCTIN   = acctin.txt          dd_ACCTFILE = ACCTFILE.dat
    dd_DISCIN   = discin.txt          dd_DISCGRP  = DISCGRP.dat
    dd_ACCTOUT  = acctdata-out.txt    dd_TRANSACT = TRANSACT.dat
    dd_TRANOUT  = systran.txt

CHECK OF SUCCESS (Session 3)
  Console: TCATBALF loaded 11, XREFFILE 50, ACCTFILE 50, DISCGRP 51,
           Accounts unloaded 50, Transactions unloaded 9
  acctdata-out.txt identical to expected\gnucobol-acctdata-out.txt
  systran.txt identical to expected\gnucobol-systran.txt except the two
  timestamps near the end of each line (they record when the job ran)
