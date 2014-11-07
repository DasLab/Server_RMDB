/* ------------------------------------------------------------------------
   RNASTAT.C
   --------

   See rnamot.doc for program information.

   Author: 1.1 - Daniel Gautheret
	   2.0 - Alain Laferriere */

/* ------------------------------- Includes ------------------------------- */

#include "rnamot.h"

/* #define AMIGA */

/* --------------------------- Global variables --------------------------- */

boolean silent = TRUE;            /* Be silent and don't display results */
boolean debugmode = TRUE;        /* Debug mode */

int desnamepos = 0;               /* Position of des. file name in args */

char desname [61];                /* Descriptor file name */

typMotif motif;                   /* The motif we try to find */

/* Description of rnamot's available switches */
char options[] =
{"Options:\n \
  [-d descriptor] : Name of the descriptor file\n \n"};

/* ----------------------------- Main program ----------------------------- */

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
    fprintf (stderr, "Usage: RNASTAT [-d desname] \n");
    fprintf (stderr, "Authors: v1.1 Daniel Gautheret 1991\n");
    fprintf (stderr, "         v2.0 Alain Laferriere 1993\n");
    exit (0);
  }

  #ifdef AMIGA
  DateStamp (datedeb);
  tempsdeb = datedeb [1] * 6000.0 + datedeb [2] * 2.0;
  #endif

  /* Initialize the motif structure */
  if (! InitializeMotif (desname, &motif))
    exit (1);

  /* Read the motif file */
  if (! ReadMotif (&motif))
    Goodbye (4);

  /* Trace motif */
  if (debugmode)
    TraceMotif (&motif);

  /* Let's go to work... */

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
              wants to do an exhaustive search (no rejection at all). */

int ParseArgs (int argc, char **argv)
{
  int i;

  /* We have no parameters? */
  if ((argc == 1) || (argv[1][0] != '-'))
    return BUG;

  /* Determine the mode of use */

  /* Analyse arguments */
  for (i = 1; i < argc; i++)
  {
    /* We have a valid parameter? */
    if (argv [i][0] != '-')
      return BUG;

    /* Switch to proper parameter */
    switch (argv [i][1])
    {
      /* Specify a file name? */
      case 'd':

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
	  case 'd': desnamepos = i; break;
	}

	break;

      /* We have an unknown switch? */
      default:
        fprintf (stderr, "Unknown switch\n");
	return BUG;
    }
  }

  /* Initialize sequence file name */

  /* Initialize descriptor file name */
  if (desnamepos)
    strncpy (desname, argv[desnamepos], 60);
  else
  {
    printf ("Descriptor file name: ");
    scanf ("%60s", desname);
  }

  return OK;
}


