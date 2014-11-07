/* ------------------------------------------------------------------------
   EXTRACT.C
   ---------

   Sequence extractor (for use with the Genbank).

   Author: Alain Laferriere */

/* ------------------------------- Includes ------------------------------- */

#include <stdio.h>
#include <string.h>

/* ----------------------------- Main program ----------------------------- */
void main (int argc, char *argv[])
{
  FILE *f, *fo;
  int seqcount = 0;
  int seqsaved = 0;
  int i, c;
  char title[255], title2[255];

  /* Parameter validation */
  if (argc != 3)
  {
    fprintf (stderr, "Usage: extract <sequence file> <output file>\n");
    fprintf (stderr, "Author: Alain Laferriere 1993\n");
    exit (0);
  }

  /* Open the sequences file */
  if (! (f = fopen (argv [1], "r")))
  {
    fprintf (stderr, "Unable to open sequence file \"%s\"\n", argv [1]);
    exit (2);
  }

  if (! (fo = fopen (argv [2], "w")))
  {
    fprintf (stderr, "Unable to open output file \"%s\"\n", argv [2]);
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
    if (((strstr(title, "itochondrial")!=NULL)) &&
	(((strstr(title, "east")!=NULL) || 
	  (strstr(title, "cerevisi")!=NULL))))      {
        seqsaved++;
	fprintf (fo, ">");
        fprintf (fo, "%s\n", title);
	while (((c = fgetc (f)) != EOF) && (c != '>') && (c != 'N'))
	  fprintf (fo, "%c", c);
	if (c == 'N') {
	  while (((c = fgetc (f)) != EOF) && (c != '>'));
          fprintf (fo, "\n");
        }
      }
    else
      while (((c = fgetc (f)) != EOF) && (c != '>'));
    if (c == '>') {
      seqcount++;
      printf ("\r%d %d", seqcount, seqsaved);
      fflush (stdout);
    }
  }

  printf ("\n");  
  fclose (f);
  fclose (fo);
}
