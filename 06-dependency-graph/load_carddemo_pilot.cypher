// CardDemo dependency graph - pilot: job INTCALC / program CBACT04C
// Source: aws-samples/aws-mainframe-modernization-carddemo (commit 59cc6c2), verified line by line by Dr. Eduardo Bautista
// Run as ONE query. It creates 16 nodes and 20 relationships.

CREATE
  (intcalc:Job {id: 'INTCALC', name: 'INTCALC', description: 'Monthly interest calculation job', source: 'jcl/INTCALC.jcl', line: '1', verified: 'Y'}),
  (closefil:Job {id: 'CLOSEFIL', name: 'CLOSEFIL', description: 'Runs before INTCALC (closes CICS files)', source: 'scheduler/CardDemo.controlm', line: '63', verified: 'Y'}),
  (combtran:Job {id: 'COMBTRAN', name: 'COMBTRAN', description: 'Runs after INTCALC (combines transaction files)', source: 'scheduler/CardDemo.controlm', line: '75', verified: 'Y'}),
  (cbact04c:Program {id: 'CBACT04C', name: 'CBACT04C', description: 'Batch COBOL: computes interest and fees per account/category', source: 'cbl/CBACT04C.cbl', line: '1', verified: 'Y'}),
  (cee3abd:SystemRoutine {id: 'CEE3ABD', name: 'CEE3ABD', description: 'IBM Language Environment abend routine (system, not CardDemo code)', source: 'cbl/CBACT04C.cbl', line: '632', verified: 'Y'}),
  (tcatbal:Dataset {id: 'TCATBAL', name: 'AWS.M2.CARDDEMO.TCATBALF.VSAM.KSDS', description: 'Transaction category balances (KSDS)', source: 'jcl/INTCALC.jcl', line: '28', verified: 'Y'}),
  (cardxref:Dataset {id: 'CARDXREF', name: 'AWS.M2.CARDDEMO.CARDXREF.VSAM.KSDS', description: 'Card-to-account cross reference (KSDS)', source: 'jcl/INTCALC.jcl', line: '30', verified: 'Y'}),
  (cardxref_aix:Dataset {id: 'CARDXREF_AIX', name: 'AWS.M2.CARDDEMO.CARDXREF.VSAM.AIX.PATH', description: 'Alternate index path on CARDXREF by account ID', source: 'jcl/INTCALC.jcl', line: '32', verified: 'Y'}),
  (acctdata:Dataset {id: 'ACCTDATA', name: 'AWS.M2.CARDDEMO.ACCTDATA.VSAM.KSDS', description: 'Account master (KSDS)', source: 'jcl/INTCALC.jcl', line: '34', verified: 'Y'}),
  (discgrp:Dataset {id: 'DISCGRP', name: 'AWS.M2.CARDDEMO.DISCGRP.VSAM.KSDS', description: 'Disclosure groups / interest rates (KSDS)', source: 'jcl/INTCALC.jcl', line: '36', verified: 'Y'}),
  (systran:Dataset {id: 'SYSTRAN', name: 'AWS.M2.CARDDEMO.SYSTRAN(+1)', description: 'System-generated interest transactions (new GDG generation)', source: 'jcl/INTCALC.jcl', line: '41', verified: 'Y'}),
  (cvtra01y:Copybook {id: 'CVTRA01Y', name: 'CVTRA01Y', description: 'Layout TRAN-CAT-BAL-RECORD (50 bytes)', source: 'cpy/CVTRA01Y.cpy', line: '1', verified: 'Y'}),
  (cvact03y:Copybook {id: 'CVACT03Y', name: 'CVACT03Y', description: 'Layout CARD-XREF-RECORD (50 bytes)', source: 'cpy/CVACT03Y.cpy', line: '1', verified: 'Y'}),
  (cvtra02y:Copybook {id: 'CVTRA02Y', name: 'CVTRA02Y', description: 'Layout DIS-GROUP-RECORD (50 bytes)', source: 'cpy/CVTRA02Y.cpy', line: '1', verified: 'Y'}),
  (cvact01y:Copybook {id: 'CVACT01Y', name: 'CVACT01Y', description: 'Layout ACCOUNT-RECORD (300 bytes)', source: 'cpy/CVACT01Y.cpy', line: '1', verified: 'Y'}),
  (cvtra05y:Copybook {id: 'CVTRA05Y', name: 'CVTRA05Y', description: 'Layout TRAN-RECORD (350 bytes)', source: 'cpy/CVTRA05Y.cpy', line: '1', verified: 'Y'})

CREATE
  (closefil)-[:PRECEDES {detail: 'Control-M: INTCALC waits for CLOSEFIL', source: 'scheduler/CardDemo.controlm', line: '70', verified: 'Y'}]->(intcalc),
  (intcalc)-[:PRECEDES {detail: 'Control-M: COMBTRAN waits for INTCALC', source: 'scheduler/CardDemo.controlm', line: '76', verified: 'Y'}]->(combtran),
  (intcalc)-[:EXECUTES {ddname: 'STEP15', detail: 'PARM=\'2022071800\' (run date)', source: 'jcl/INTCALC.jcl', line: '22', verified: 'Y'}]->(cbact04c),
  (cbact04c)-[:READS {ddname: 'TCATBALF', detail: 'OPEN INPUT; sequential READ (drives the run)', source: 'cbl/CBACT04C.cbl', line: '236, 326', verified: 'Y'}]->(tcatbal),
  (cbact04c)-[:READS {ddname: 'XREFFILE', detail: 'OPEN INPUT; random READ', source: 'cbl/CBACT04C.cbl', line: '254, 394', verified: 'Y'}]->(cardxref),
  (cbact04c)-[:READS {ddname: 'XREFFIL1', detail: 'READ ... KEY IS FD-XREF-ACCT-ID (alternate key) needs the AIX path DD', source: 'cbl/CBACT04C.cbl', line: '38, 395', verified: 'Y'}]->(cardxref_aix),
  (cbact04c)-[:READS {ddname: 'DISCGRP', detail: 'OPEN INPUT; random READ. Business rule: if the group is not found (status \'23\'), reads again with key \'DEFAULT\' (line 444).', source: 'cbl/CBACT04C.cbl', line: '272, 416, 444', verified: 'Y'}]->(discgrp),
  (cbact04c)-[:UPDATES {ddname: 'ACCTFILE', detail: 'OPEN I-O; READ then REWRITE (balance updated)', source: 'cbl/CBACT04C.cbl', line: '291, 356, 373', verified: 'Y'}]->(acctdata),
  (cbact04c)-[:WRITES {ddname: 'TRANSACT', detail: 'OPEN OUTPUT; WRITE interest transactions; LRECL=350', source: 'cbl/CBACT04C.cbl', line: '309, 500', verified: 'Y'}]->(systran),
  (cbact04c)-[:CALLS {detail: 'Called only on error to force an abend (ABCODE 999)', source: 'cbl/CBACT04C.cbl', line: '632', verified: 'Y'}]->(cee3abd),
  (cbact04c)-[:INCLUDES {detail: 'COPY statement', source: 'cbl/CBACT04C.cbl', line: '97', verified: 'Y'}]->(cvtra01y),
  (cbact04c)-[:INCLUDES {detail: 'COPY statement', source: 'cbl/CBACT04C.cbl', line: '102', verified: 'Y'}]->(cvact03y),
  (cbact04c)-[:INCLUDES {detail: 'COPY statement', source: 'cbl/CBACT04C.cbl', line: '107', verified: 'Y'}]->(cvtra02y),
  (cbact04c)-[:INCLUDES {detail: 'COPY statement', source: 'cbl/CBACT04C.cbl', line: '112', verified: 'Y'}]->(cvact01y),
  (cbact04c)-[:INCLUDES {detail: 'COPY statement', source: 'cbl/CBACT04C.cbl', line: '117', verified: 'Y'}]->(cvtra05y),
  (cvtra01y)-[:DESCRIBES {detail: 'READ ... INTO TRAN-CAT-BAL-RECORD', source: 'cbl/CBACT04C.cbl', line: '326', verified: 'Y'}]->(tcatbal),
  (cvact03y)-[:DESCRIBES {detail: 'READ ... INTO CARD-XREF-RECORD', source: 'cbl/CBACT04C.cbl', line: '394', verified: 'Y'}]->(cardxref),
  (cvtra02y)-[:DESCRIBES {detail: 'READ ... INTO DIS-GROUP-RECORD', source: 'cbl/CBACT04C.cbl', line: '416', verified: 'Y'}]->(discgrp),
  (cvact01y)-[:DESCRIBES {detail: 'READ ... INTO ACCOUNT-RECORD', source: 'cbl/CBACT04C.cbl', line: '373', verified: 'Y'}]->(acctdata),
  (cvtra05y)-[:DESCRIBES {detail: 'WRITE ... FROM TRAN-RECORD', source: 'cbl/CBACT04C.cbl', line: '500', verified: 'Y'}]->(systran)
