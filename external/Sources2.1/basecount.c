/* ------------------------------------------------------------------------
   BASECOUNT.C
   ---------

   Author: Alain Laferriere */

/* ------------------------------- Includes ------------------------------- */

#include <stdio.h>
#include <string.h>

/* ----------------------------- Main program ----------------------------- */
void main (int argc, char *argv[])
{
  FILE *f, *fo;
  int seqcount = 0;
  long basecount = 0;
  int i, c;
  int j = 0;
  char title[255];

  /* Parameter validation */
  if (argc != 2)
  {
    fprintf (stderr, "Usage: basecount <sequence file>\n");
    fprintf (stderr, "Author: Alain Laferriere 1993\n");
    exit (0);
  }

  /* Open the sequences file */
  if (! (f = fopen (argv [1], "r")))
  {
    fprintf (stderr, "Unable to open sequence file \"%s\"\n", argv [1]);
    exit (2);
  }

  /* Reach next '>' character */
  while (((c = fgetc (f)) != EOF) && (c != '>'));

  while (c != EOF) {
    i = 0;
    while (((c = fgetc (f)) != EOF) && (c != '\n')) {
      title [i] = c;
      i++;
    }
    title[i]='\0';
    if ((strstr(title, "ribosomal")!=NULL) ||
	(strstr(title, "rrna")!=NULL) ||
	(strstr(title, "rRNA")!=NULL)) {
      while (((c = fgetc (f)) != EOF) && (c != '>'))
	if ((c != '\n') && (c != ' '))
	  basecount ++;
    } else
      while (((c = fgetc (f)) != EOF) && (c != '>'));
    if (c == '>') {
      seqcount++;
      printf ("\r%d %ld", seqcount, basecount);
      fflush (stdout);
    }
  }

  printf ("\n");  
  fclose (f);
}
