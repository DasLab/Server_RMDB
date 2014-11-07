/* ------------------------------------------------------------------------
   EXTRACT.C
   ---------

   Sequence extractor (for use with the Genbank).

   Author: Alain Laferriere */

/* ------------------------------- Includes ------------------------------- */

#include <stdio.h>

/* ----------------------------- Main program ----------------------------- */
void main (int argc, char *argv[])
{
  FILE *f;
  int start, end;
  int seqcount = 0;
  int c;
  int charcount;

  /* Parameter validation */
  if (argc != 4)
  {
    fprintf (stderr, "Usage: extract <sequences file> <start> <end>\n");
    fprintf (stderr, "Author: Alain Laferriere 1993\n");
    exit (0);
  }

  /* Extract starting and ending sequences */
  start = atoi (argv [2]);
  end   = atoi (argv [3]);

  /* Validate starting end ending sequence numbers */
  if ((start < 1) || (end < start))
  {
    fprintf (stderr, "Error, invalid starting and ending sequence numbers!\n");
    exit (1);
  }

  /* Open the sequences file */
  if (! (f = fopen (argv [1], "r")))
  {
    fprintf (stderr, "Unable to open sequences file \"%s\"\n", argv [1]);
    exit (2);
  }

  /* Reach starting sequence */
  while (seqcount < start)
  {
    /* Reach next '>' character */
    while (((c = fgetc (f)) != EOF) && (c != '>'));

    /* Do we have a sequence beginning? */
    if (c == '>') seqcount++;

    /* Do we have the end of file? */
    if (c == EOF) break;
  }

  /* Are we positionned to the beginning of a sequence? */
  while (c == '>')
  {
    /* Output sequence name */
    do
    {
      putchar (c);
      c = fgetc (f);
    }
    while (c != '\n');

    /* Write the end of line */
    putchar (c);

    /* Reset character counter */
    charcount = 0;

    /* Output sequences */
    do
    {
      if (c != '\n')
      {
        putchar (c);
        charcount++;

        if (charcount == 80)
        {
          putchar ('\n');
          charcount = 0;
        }
      }

      c = fgetc (f);
    }
    while ((c != '>') && (c != EOF));

    /* Are we finished? */
    if ((seqcount == end) || (c == EOF)) break;

    /* Are we on a new sequence beginning? */
    if (c == '>')
    {
      printf ("\n\n");
      seqcount++;
    }
  }

  putchar ('\n');

  fclose (f);
}
