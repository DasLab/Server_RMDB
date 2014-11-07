/* ------------------------------------------------------------------------
   EXTRACT.C
   ---------

   Sequence extractor (for use with the Genbank format).

   Author: Alain Laferriere */

/* ------------------------------- Includes ------------------------------- */

#include <stdio.h>
#include <string.h>

/* ----------------------------- Main program ----------------------------- */

int readline (f, l)
  char *l;
{
  int i=0, c;
  while (((c = fgetc (f)) != EOF) && (c != '\n')) {
    l[i] = c;
    i++;
  }
  l[i]='\0';
  return (c!=EOF);
}

void main (int argc, char *argv[])
{
  FILE *f, *fo;
  int seqcount = 0;
  int seqsaved = 0;
  int i, j, c, found, end;
  char line[200][255], l[255];

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

  while (readline(f, l)) {
    if (strstr(l, "LOCUS")!=NULL){
      i = 0;
      found = 0;
      do {
 	strcpy (line[i], l);
	if ((strstr(l, "ORGANISM")!=NULL) &&
	    (strstr(l, "irus")!=NULL) &&
	     (strstr(l, "")!=NULL))
	  found = 1;
	i++;
	end = readline (f, l);
      } while ((end==1) && (strstr(l, "ORIGIN")==NULL));
      
      if (found) {
 	strcpy (line[i], l);
	seqsaved++;
	for (j=0; j<=i; j++)
	  fprintf (fo, "%s\n", line[j]);
	while (readline(f, l) && strstr(l, "//")==NULL)
	    fprintf (fo, "%s\n", l);
	fprintf (fo, "%s\n", l);
      }
      printf ("\r%d %d", seqcount, seqsaved);
      seqcount++;
      fflush (stdout);
    }
  }

  printf ("\n");  
  fclose (f);
  fclose (fo);
}
