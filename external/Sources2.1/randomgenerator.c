/* ------------------------------------------------------------------------
   RANDOMGENERATOR.C
   -----------------

   Program that can generate random RNA sequences of desired length.

   Author: 2.0 - Alain Laferriere */

/* ------------------------------- Includes ------------------------------- */

#include <stdio.h>

/* ----------------------------- Main program ----------------------------- */

void main (int argc, char *argv[])
{
  FILE *f;
  int count, nbnucleotides;

  /* Validate parameters */
  if (argc != 3)
  {
    fprintf (stderr, "Usage: RandomGenerator <nb nucleotides> <output file>\n");
    exit (0);
  }

  /* Extract the number of nucleotides desired */
  nbnucleotides = atoi (argv [1]);

  /* Open the output file */
  if (! (f = fopen (argv [2], "w")))
  {
    fprintf (stderr, "Error, opening \"%s\" file\n", argv[2]);
    exit (1);
  }

  /* Write sequence header */
  fprintf (f, "> Sequence: \"%s\", Nb nucleotides: %d\n",
           argv[2], nbnucleotides);

  /* Generate the file */
  for (count = 0; count < nbnucleotides; count++)
  {
    switch (myrand() % 4)
    {
      case 0:
        fputc ('A', f);
        break;

      case 1:
        fputc ('C', f);
        break;

      case 2:
        fputc ('G', f);
        break;

      case 3:
        fputc ('U', f);
        break;
    }

    if ((count + 1) % 80 == 0)
      fputc ('\n', f);
  }

  fputc ('\n', f);
  fclose (f);
}

int myrand ()
{
  return (int) rand () / 21473879.86;
}
