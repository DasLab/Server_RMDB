/* ------------------------------------------------------------------------
   RNAMOT.C
   --------

   See rnamot.doc for program information.

   Author: 1.1 - Daniel Gautheret
	   2.0 - Alain Laferriere */

/* ------------------------------- Includes ------------------------------- */

#include "rnamot.h"

/* Compilation switch for developper environment. When active, lets the
   user specify a "debug" switch at run time (-x). Must be commented for
   distributed version. */
#define DEVELOPPER

/* Compilation switch that creates an Amiga version (with time) */
/*
#define AMIGA
*/

/* --------------------------- Global variables --------------------------- */

boolean writebars = FALSE;        /* Don't write bars */
boolean normal = TRUE;            /* Scan normal sequences */
boolean reverse = FALSE;          /* Don't scan reverse sequences */
boolean silent = TRUE;            /* Be silent and don't display results */
boolean usemotifpriority = FALSE; /* Use priority list in the motif file */
boolean noalternative = FALSE;    /* Generate alternative solutions file */
boolean debugmode = FALSE;        /* Debug mode */
boolean fastsearch = TRUE;        /* Fast search mode */
boolean formatted = FALSE;        /* Output formatted in 80 columns */

int mode;                         /* Rnamot's mode (SEARCH | ALIGNMENT) */

int fileformat = NONE;            /* Sequence file format (FASTA | GENBANK) */

int seqnamepos = 0;               /* Position of seq. file name in args */
int desnamepos = 0;               /* Position of des. file name in args */
int solnamepos = 0;               /* Position of output file name in args */

char seqname [61];                /* Sequence file name */
char desname [61];                /* Descriptor file name */
char solname [61];                /* Optimal solution file name */
char altname [61];                /* Alternatives solutions file name */

typMotif motif;                   /* The motif we try to find */
typSequence sequence;             /* A sequence in treatment */
typSolution solution;             /* The solution we find */

long bufferlength = BUFFERLENGTH; /* Initial buffer length dimension */

/* Usage information */
#ifdef DEVELOPPER
char usage[] =
{"Usage: RNAMOT -s [-b] [-c] [-n]\n \
                [-s seqname] [-d desname] [-o outname] [-e] [-f] [-p] [-t] [-x]\n \
      or\n\n \
      RNAMOT -a [-b]\n \
                [-s seqname] [-d desname] [-o outname] [-e] [-f] [-p] [-t] [-x]\n\n"};
#else
char usage [] =
{"Usage: RNAMOT -s [-b] [-c] [-n]\n \
                [-s seqname] [-d desname] [-o outname] [-e] [-f] [-p] [-t]\n \
      or\n\n \
      RNAMOT -a [-b]\n \
                [-s seqname] [-d desname] [-o outname] [-e] [-f] [-p] [-t]\n\n"};
#endif

/* Options information */
#ifdef DEVELOPPER
char options[] =
{"Options:\n \
  <-s | -a>       : Mode of use (SEARCH or ALIGNMENT)\n \
  [-s sequence]   : Name of the sequence(s) file\n \
  [-d descriptor] : Name of the descriptor file\n \
  [-o output]     : Name of output files (defaults: \"sol\" and \"alt\")\n \
  [-e]            : Exhaustive search mode (see documentation)\n \
  [-f]            : Output results in 80 columns format\n \
  [-p]            : Use search priority order in the descriptor file\n \
                    (don't try to generate an optimal order)\n \
  [-t]            : Activate interactive information display\n \
  [-x]            : Activate debug mode\n\n \
  SEARCH MODE EXTRA PARAMETERS:\n\n \
  [-b]            : Search both normal and complementary sequence(s)\n \
  [-c]            : Search complementary sequence(s) only\n \
  [-n]            : Don't generate alternative solutions\n\n \
  ALIGNMENT MODE EXTRA PARAMETERS:\n\n \
  [-b]            : Write separator bars in solution file\n\n \
  The order of appearance of the optional switches has no importance.\n\n"};
#else
char options[] =
{"Options:\n \
  <-s | -a>       : Mode of use (SEARCH or ALIGNMENT)\n \
  [-s sequence]   : Name of the sequence(s) file\n \
  [-d descriptor] : Name of the descriptor file\n \
  [-o output]     : Name of output files (defaults: \"sol\" and \"alt\")\n \
  [-e]            : Exhaustive search mode (see documentation)\n \
  [-f]            : Output results in 80 columns format\n \
  [-p]            : Use search priority order in the descriptor file\n \
                    (don't try to generate an optimal order)\n \
  [-t]            : Activate interactive information display\n\n \
  SEARCH MODE EXTRA PARAMETERS:\n\n \
  [-b]            : Search both normal and complementary sequence(s)\n \
  [-c]            : Search complementary sequence(s) only\n \
  [-n]            : Don't generate alternative solutions\n\n \
  ALIGNMENT MODE EXTRA PARAMETERS:\n\n \
  [-b]            : Write separator bars in solution file\n\n \
  The order of appearance of the optional switches has no importance.\n\n"};
#endif

/* Author information */
char author[] =
{"Authors: v1.1 Daniel Gautheret 1991 (gauthere@beagle.colorado.edu)\n \
        v2.1 Alain Laferriere 1993 (laferrie@iro.umontreal.ca)\n"};

/* ----------------------------- Main program ----------------------------- */

/* The program parameters are:

  Usage: RNAMOT -s [-b | -c] [-n]
                   [-s seqname] [-d desname] [-o outname] [-e] [-f] [-p] [-t] [-x]
         or

         RNAMOT -a [-b]
                   [-s seqname] [-d desname] [-o outname] [-e] [-f] [-p] [-t] [-x]

  Note that [-x] option is only available in the developper's version.

*/

void main (int argc, char *argv[])
{
  int finished = FALSE;

  #ifdef AMIGA
  long datedeb [3], datecour [3], datefin1 [3], daterev [3], datefin2 [3];
  float tempsdeb, tempscour, tempsfin1, tempsrev, tempsfin2;
  #endif

  /* Parse the arguments */
  if (! ParseArgs (argc, argv))
  {
    fprintf (stderr, "%s", usage);
    fprintf (stderr, "%s", options);
    fprintf (stderr, "%s", author);
    exit (0);
  }

  #ifdef AMIGA
  DateStamp (datedeb);
  tempsdeb = datedeb [1] * 6000.0 + datedeb [2] * 2.0;
  #endif

  /* Initialize the motif structure */
  if (! InitializeMotif (desname, &motif))
    exit (1);

  /* Initialise the sequence structure */
  if (! InitializeSequence (seqname, &sequence))
  {
    FreeMotif (&motif);
    exit (1);
  }

  /* Initialize the solution structure */
  if (! InitializeSolution (solname, altname, &solution))
  {
    FreeMotif (&motif);
    FreeSequence (&sequence);
    exit (1);
  }

  /* Read the motif file */
  if (! ReadMotif (&motif))
    Goodbye (4);

  /* Trace motif */
  if (debugmode)
    TraceMotif (&motif);

  /* Analyse the sequence file's type */
  if (! (fileformat = SequenceFormat (&sequence)))
    Goodbye (5);

  /* Can we talk? Display information header */
  if (! silent)
  {
    if (mode == SEARCH)
      printf ("   seq  comp  length   sols   alts  total sols total alts done\n"
              "   ---  ----  ------   ----   ----  ---------- ---------- ----\n");
    else
      printf ("   seq  length   match  done\n"
              "   ---  ------   -----  ----\n");
  }

  /* Let's go to work... */
  if (mode == SEARCH)
  {
    /* Analyse sequences */
    while (! finished)
    {
      switch (ReadSequence (&sequence))
      {
        case EOF:
          finished = TRUE;
          break;

        case BUG:
          Goodbye (1);
          break;

        case OK:

          /* Do we want to scan normal sequences? */
          if (normal)
          {
            #ifdef AMIGA
            DateStamp (datecour);
            tempscour = datecour [1] * 6000.0 + datecour [2] * 2.0;
            #endif

            /* Mark the sequence */
            if (fastsearch)
              MarkSequence (&motif, &sequence);

            /* Analyse that sequence */
            Analyze (&motif, &sequence, &solution);

            #ifdef AMIGA
            DateStamp (datefin1);
            tempsfin1 = datefin1 [1] * 6000.0 + datefin1 [2] * 2.0;
            #endif
          }

          /* Do we want to scan complementary sequence? */
          if (reverse)
          {
            /* Complement the sequence */
            ComplementSequence (&sequence);

            /* Mark the sequence */
            if (fastsearch)
              MarkSequence (&motif, &sequence);

            #ifdef AMIGA
            DateStamp (daterev);
            tempsrev = daterev [1] * 6000.0 + daterev [2] * 2.0;
            #endif

            /* Analyse that sequence */
            Analyze (&motif, &sequence, &solution);

            #ifdef AMIGA
            DateStamp (datefin2);
            tempsfin2 = datefin2 [1] * 6000.0 + datefin2 [2] * 2.0;
            #endif
	  }

          break;
      }
    }

    /* Write global information */
    if (solution.fsol)
      fprintf (solution.fsol, "\nTotal: %d sequences, %d nucleotides scanned, "
               "%d matches, %d actual\n",
               sequence.nbsequences, sequence.totnucleotides,
               sequence.totmatches, solution.totsols);

    /* Can we talk? Display global results on screen. */
    if (! silent)
    {
      printf ("\n\nTotal: %d sequences, %d nucleotides scanned, %d matches, "
              "%d actual\n", sequence.nbsequences, sequence.totnucleotides,
              sequence.totmatches, solution.totsols);

      if (noalternative)
        printf ("Results are written in file \"%s\"\n", solname);
      else
      {
        if (solution.totsols == 0)
          printf ("No results written\n");
        else
        {
          /* We have no alternative solutions? */
          if (sequence.totmatches == solution.totsols)
            printf ("Results are written in file \"%s\"\n", solname);
          else
          {
            /* We have only alternative solutions? */
            if (sequence.totmatches == 0)
              printf ("Results are written in file \"%s\"\n", altname);
            else
              /* We have both alternative and non-alternative solutions! */
              printf ("Results are written in files \"%s\" and \"%s\"\n",
                      solname, altname);
          }
        }
      }
    }

    #ifdef AMIGA
      if (reverse)
        printf ("Loading: %4.2f, Normal scan: %4.2f, Complement: %4.2f, "
                "Reverse scan: %4.2f Total time: %4.2f\n",
                (tempscour - tempsdeb) / 100.0,
                (tempsfin1 - tempscour) / 100.0,
                (tempsrev  - tempsfin1) / 100.0,
                (tempsfin2 - tempsrev) / 100.0,
                (tempsfin2 - tempsdeb) / 100.0);
      else
        printf ("Loading: %4.2f, Normal scan: %4.2f, Total time: %4.2f\n",
                (tempscour - tempsdeb) / 100.0,
                (tempsfin1 - tempscour) / 100.0,
                (tempsfin1 - tempsdeb) / 100.0);
    #endif
  }
  else
  {
    if (! Alignment (&motif, &sequence, &solution))
      Goodbye (2);

    /* Can we talk? */
    if (! silent)
      printf ("\n\nResults are written in file \"%s\"\n", solname);
  }

  /* Bye! */
  Goodbye (OK);
}

/* ------------------------------ Goodbye () ------------------------------ */

/* Function that frees all memory used and quits the program with the
   specified return value.

   09/12/92 - Creation. */

void Goodbye (int value)
{
  FreeMotif (&motif);
  FreeSequence (&sequence);
  FreeSolution (&solution);

  exit (value);
}

/* ----------------------------- ParseArgs () ----------------------------- */

/* Function that analyses the arguments passed to the main program. It adds
   the suffix for motif name if it's missing.

   09/12/92 - Creation.
   17/01/93 - Addition of a switch to specify the buffer length.
   21/01/93 - Addition of a switch to use motif's priority list (like in
              Rnamot v1.1)
   29/01/93 - Don't add the .pat suffix for the motif or the .seq suffix
              for the sequence so that the program can work with genbanks
              that don't already have those suffixes.
              New option to disable the saving of alternative solutions.
   03/02/93 - Elimination of the [-m] switch since empirical results show
              a gain of only 0.3 seconds for scanning a trna pattern in
              a 1 megabyte sequence randomly generated.
   07/02/93 - Rnamot now requires a necessary parameter which indicates the
              mode of use ('s' for solutions search and 'a' for alignment).
              This is good since an invocation of Rnamot without parameters
              will now force the display of information on usage. The old
              approach asked the user to enter the names of the descriptor
              and sequence files and went in a running mode even when the
              user was interested only to know how to use the program. It's
              a much more natural way of doing things.
              Options [-c] and [-n] can't be used in ALIGNMENT mode.
   10/02/93 - Addition of new swtiches [-a] and [-b] in alignment mode and
              [-b] in search mode and modification of switch [-r] of search
              mode to [-c].
   11/02/93 - Addition of the fast search option [-f] that tells the scanning
              algorithm to reject portions of the sequence that contains only
              "N" nucleotides for the first and the second elements of the
              optimal priority order array. If the switch is off, we only
              consider the first element of the array for rejection.
   15/02/93 - Modified the [-f] switch to [-e]. Now the fast search mode is
              always in use and the user MUST specify the [-e] switch if he
              wants to do an exhaustive search (no rejection at all).
   08/05/93 - Elimination of the [-a] switch. It does not make sense to offer
              the possibility to not align the sequences found if we're in
              alignment mode.
   17/05/93 - Addition of the [-f] switch that allows the output results to
              be formatted in 80 columns. */

int ParseArgs (int argc, char **argv)
{
  int i;

  /* We have no parameters? */
  if ((argc == 1) || (argv[1][0] != '-'))
    return BUG;

  /* Determine the mode of use */
  switch (argv [1][1])
  {
    case 's' : mode = SEARCH; break;
    case 'a' : mode = ALIGNMENT; break;
    default  : return BUG;
  }

  /* Analyse arguments */
  for (i = 2; i < argc; i++)
  {
    /* We have a valid parameter? */
    if (argv [i][0] != '-')
      return BUG;

    /* Switch to proper parameter */
    switch (argv [i][1])
    {
      /* If search mode, scan both normal and reverse sequence(s) and if
         alignment mode, write separator bars in output file */
      case 'b':

        /* Search mode? */
        if (mode == SEARCH)
          reverse = TRUE;
        else
          writebars = TRUE;

	break;

      /* Scan complementary sequence(s) only? */
      case 'c':

        /* Option [-c] inoperative in ALIGNMENT mode */
        if (mode == ALIGNMENT)
        {
          fprintf (stderr,
            "The [-c] option shall not be used in the ALIGNMENT mode\n");
          return BUG;
        }

	reverse = TRUE;
        normal = FALSE;
	break;

      /* Exhaustive search? */
      case 'e':

        fastsearch = FALSE;
        break;

      /* Format output in 80 columns? */
      case 'f':

        formatted = TRUE;
        break;

      /* Don't generate alternative solutions file */
      case 'n':

        /* Option [-n] inoperative in ALIGNMENT mode */
        if (mode == ALIGNMENT)
        {
          fprintf (stderr,
            "The [-n] option shall not be used in the ALIGNMENT mode\n");
          return BUG;
        }

        noalternative = TRUE;
        break;

      /* Use priority list in the motif file */
      case 'p':
        usemotifpriority = TRUE;
        break;

      /* Display results to screen */
      case 't':
	silent = FALSE;
	break;

      /* Specify a file name? */
      case 's':
      case 'd':
      case 'o':

	/* Do we have a file name? */
	if (i == argc - 1)
	  return BUG;

	/* Go to next parameter in list */
	i++;

	/* Is that the file name? */
	if (argv [i][0] == '-')
	  return BUG;

	/* Ok, we have it! */
	switch (argv[i - 1][1])
	{
	  case 's': seqnamepos = i; break;
	  case 'd': desnamepos = i; break;
	  case 'o': solnamepos = i; break;
	}

	break;

      #ifdef DEVELOPPER
      /* Debug mode? */
      case 'x':
        debugmode = TRUE;
        break;
      #endif

      /* We have an unknown switch? */
      default:
        fprintf (stderr, "Unknown switch\n");
	return BUG;
    }
  }

  /* Initialize sequence file name */
  if (seqnamepos)
    strncpy (seqname, argv[seqnamepos], 60);
  else
  {
    printf ("Sequence file name: ");
    scanf ("%60s", seqname);
  }

  /* Initialize descriptor file name */
  if (desnamepos)
    strncpy (desname, argv[desnamepos], 60);
  else
  {
    printf ("Descriptor file name: ");
    scanf ("%60s", desname);
  }

  /* Initialize output file name */
  if (solnamepos)
  {
    /* Prepare output file names */
    strncpy (solname, argv[solnamepos], 56);
    strncpy (altname, argv[solnamepos], 56);
    strcat  (solname, ".sol");
    strcat  (altname, ".alt");
  }
  else
  {
    strcpy (solname, "sol");
    strcpy (altname, "alt");
  }

  /* TRACE */
/*
  printf ("The parameters are:\n");
  printf ("Mode of use             : %s\n", (mode == SEARCH) ? "SEARCH" : "ALIGNMENT");
  printf ("Sequence file name      : %s\n", seqname);
  printf ("Descriptor file name    : %s\n", desname);
  printf ("Solution file name      : %s\n", solname);
  printf ("Alternates file name    : %s\n", altname);
  printf ("Output in 80 columns    : %s\n", (formatted) ? "YES" : "NO");
  printf ("Write bars              : %s\n", (writebars) ? "YES" : "NO");
  printf ("Search normal sequence  : %s\n", (normal) ? "YES" : "NO");
  printf ("Search comp. sequence   : %s\n", (reverse) ? "YES" : "NO");
  printf ("Talk mode active        : %s\n", (silent) ? "NO" : "YES");
  printf ("Use desctiptor priority : %s\n", (usemotifpriority) ? "YES" : "NO");
  printf ("Generate alternatives   : %s\n", (noalternative) ? "NO" : "YES");
  printf ("Debug mode              : %s\n", (debugmode) ? "YES" : "NO");
  printf ("Fast search             : %s\n", (fastsearch) ? "YES" : "NO");
*/

  return OK;
}


