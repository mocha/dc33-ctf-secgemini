       IDENTIFICATION DIVISION.
       PROGRAM-ID. SYS-PROCESS-86.

       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       SOURCE-COMPUTER. ANY.
       OBJECT-COMPUTER. ANY.

       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 DATA-SET-A.
           05 FILLER PIC S9(4) COMP VALUE 1041.
           05 FILLER PIC S9(4) COMP VALUE 1061.
           05 FILLER PIC S9(4) COMP VALUE 1067.
           05 FILLER PIC S9(4) COMP VALUE 1030.
           05 FILLER PIC S9(4) COMP VALUE 1538.
           05 FILLER PIC S9(4) COMP VALUE 2403.
           05 FILLER PIC S9(4) COMP VALUE 1059.
           05 FILLER PIC S9(4) COMP VALUE 1924.
           05 FILLER PIC S9(4) COMP VALUE 1059.
           05 FILLER PIC S9(4) COMP VALUE 1000.
           05 FILLER PIC S9(4) COMP VALUE 1924.
           05 FILLER PIC S9(4) COMP VALUE 1538.
           05 FILLER PIC S9(4) COMP VALUE 1555.
           05 FILLER PIC S9(4) COMP VALUE 1324.
           05 FILLER PIC S9(4) COMP VALUE 1150.
           05 FILLER PIC S9(4) COMP VALUE 1924.
           05 FILLER PIC S9(4) COMP VALUE 1000.
           05 FILLER PIC S9(4) COMP VALUE 1394.
           05 FILLER PIC S9(4) COMP VALUE 1234.
           05 FILLER PIC S9(4) COMP VALUE 1000.
           05 FILLER PIC S9(4) COMP VALUE 1361.
           05 FILLER PIC S9(4) COMP VALUE 1059.
           05 FILLER PIC S9(4) COMP VALUE 1059.
           05 FILLER PIC S9(4) COMP VALUE 1263.
           05 FILLER PIC S9(4) COMP VALUE 1000.
           05 FILLER PIC S9(4) COMP VALUE 1555.
           05 FILLER PIC S9(4) COMP VALUE 1132.
           05 FILLER PIC S9(4) COMP VALUE 1361.
           05 FILLER PIC S9(4) COMP VALUE 1000.
           05 FILLER PIC S9(4) COMP VALUE 1217.
           05 FILLER PIC S9(4) COMP VALUE 1555.
           05 FILLER PIC S9(4) COMP VALUE 1324.
           05 FILLER PIC S9(4) COMP VALUE 1150.
           05 FILLER PIC S9(4) COMP VALUE 1000.
           05 FILLER PIC S9(4) COMP VALUE 1333.
           05 FILLER PIC S9(4) COMP VALUE 1132.
           05 FILLER PIC S9(4) COMP VALUE 1000.
           05 FILLER PIC S9(4) COMP VALUE 1538.
           05 FILLER PIC S9(4) COMP VALUE 1333.
           05 FILLER PIC S9(4) COMP VALUE 1134.
           05 FILLER PIC S9(4) COMP VALUE 1059.
           05 FILLER PIC S9(4) COMP VALUE 1319.

       01 DATA-ARRAY-A REDEFINES DATA-SET-A.
           05 DATA-POINT PIC S9(4) COMP OCCURS 42 TIMES.

       01 VAR-I                 PIC 9(4) COMP.
       01 VAR-N                 PIC 9(4) COMP.
       01 VAR-RSLT              PIC 9(4) COMP.
       01 VAR-T1                PIC 9(4) COMP.
       01 VAR-T2                PIC 9(4) COMP.
       01 VAR-T4                PIC 9(4) COMP.
       01 VAR-Q                 PIC 9(9) COMP.
       01 VAR-REM               PIC 9(4) COMP.

       01 OUTPUT-BUFFER.
           05 OUTPUT-CHAR PIC X OCCURS 42 TIMES.

       PROCEDURE DIVISION.
       P-000-MAIN.
           DISPLAY "===================================================".
           DISPLAY "   SYSTEM PROCESS INITIATED (UNOPTIMIZED)".
           DISPLAY "===================================================".
           DISPLAY "Starting calculation... This may take a long time.".
           DISPLAY " ".

           PERFORM P-100-ITERATE VARYING VAR-I FROM 1 BY 1
               UNTIL VAR-I > 42.

           PERFORM P-900-OUTPUT.

           STOP RUN.

       P-100-ITERATE.
           MOVE DATA-POINT(VAR-I) TO VAR-N.
           PERFORM P-200-COMPUTE.
           UNSTRING FUNCTION CHAR(VAR-RSLT + 1) INTO OUTPUT-CHAR(VAR-I).

       P-200-COMPUTE.
           IF VAR-N < 4
               EVALUATE VAR-N
                   WHEN 0 MOVE 10 TO VAR-RSLT
                   WHEN 1 MOVE 20 TO VAR-RSLT
                   WHEN 2 MOVE 30 TO VAR-RSLT
                   WHEN 3 MOVE 40 TO VAR-RSLT
               END-EVALUATE
           ELSE
               SUBTRACT 1 FROM VAR-N GIVING VAR-T1.
               PERFORM SUB-COMPUTE-RTN
                   USING VAR-T1
                   GIVING VAR-T1.

               SUBTRACT 2 FROM VAR-N GIVING VAR-T2.
               PERFORM SUB-COMPUTE-RTN
                   USING VAR-T2
                   GIVING VAR-T2.
               MULTIPLY 2 BY VAR-T2.

               SUBTRACT 4 FROM VAR-N GIVING VAR-T4.
               PERFORM SUB-COMPUTE-RTN
                   USING VAR-T4
                   GIVING VAR-T4.

               COMPUTE VAR-RSLT = VAR-T1 + VAR-T2 + VAR-T4 + 5.

               DIVIDE VAR-RSLT BY 256 GIVING VAR-Q
                   REMAINDER VAR-REM.
               MOVE VAR-REM TO VAR-RSLT
           END-IF.

       SUB-COMPUTE-RTN.
           ENTRY "SUB-COMPUTE-RTN"
               USING BY VALUE IN-VAL AS NUMERIC
               GIVING OUT-VAL AS NUMERIC.

           MOVE IN-VAL TO VAR-N.
           PERFORM P-200-COMPUTE.
           MOVE VAR-RSLT TO OUT-VAL.
           EXIT PROGRAM.

       P-900-OUTPUT.
           DISPLAY " ".
           DISPLAY "========================================".
           DISPLAY "Processing complete.".
           DISPLAY "Final result: " WITH NO ADVANCING.
           DISPLAY OUTPUT-BUFFER.
           DISPLAY "========================================".

       END PROGRAM SYS-PROCESS-86.
