/* ------------------------------------------------------------------------
   Sequence.c
   ----------

     Functions that support sequence file reading and sequence structures
   initialization, with consistency checking and memory usage optimization. */

/* ------------------------------ Constants ------------------------------- */

/* Compilation switch demo version. When active, limits the number of
   sequences that can be searched or aligned to 10. */
/*
#define DEMO
*/

/* ------------------------------- Includes ------------------------------- */

#include "rnamot.h"

/* -------------------------- External variables -------------------------- */

extern long bufferlength;
extern char Complement[];
extern boolean fastsearch;
extern int fileformat;

/* --------------------------- Global variables --------------------------- */

/* Special rejection flags */
short int rejectn [6] = {0x8000, 0x2000, 0x0800, 0x0200, 0x0080, 0x0020};
short int rejectr [6] = {0x4000, 0x1000, 0x0400, 0x0100, 0x0040, 0x0010};

/* ------------------------- ComplementSequence () ------------------------ */

/* Function that complements a sequence.

   22/01/93 - Creation.
   11/02/93 - Be sure to filtrate special bits in nucleotides before
              complementing.
   15/02/93 - The sequence is now stored in a short int array. */

void ComplementSequence (typSequence *SequencePtr)
{
  int i, j;
  short int temp;

  for (i = 0, j = SequencePtr->length - 1; i < SequencePtr->length / 2;
       i++, j--)
  {
    temp = SequencePtr->sequence[j];
    SequencePtr->sequence[j] = Complement [SequencePtr->sequence[i] & NUCMASK];
    SequencePtr->sequence[i] = Complement [temp & NUCMASK];
  }

  /* The sequence is now complemented */
  SequencePtr->complemented = TRUE;
}

/* ---------------------------- FreeSequence () --------------------------- */

/* Function that cleans a sequence structure.

   09/12/92 - Creation.
   29/01/93 - Free commentary field.
   08/02/93 - Close sequence file if necessary. */

void FreeSequence (typSequence *SequencePtr)
{
  typBuffer *BufferPtr;

  /* Close sequence file */
  if (SequencePtr->fsequence)
    fclose (SequencePtr->fsequence);

  /* Free sequence name */
  if (SequencePtr->name)
    free (SequencePtr->name);

  /* Free commentary */
  if (SequencePtr->commentary)
    free (SequencePtr->commentary);

  /* Free sequence */
  if (SequencePtr->sequence)
    free (SequencePtr->sequence);

  /* Free memory buffers */
  if (SequencePtr->bufferlist)
  {
    BufferPtr = SequencePtr->bufferlist;
    SequencePtr->bufferlist = BufferPtr->next;

    if (BufferPtr->sequence)
      free (BufferPtr->sequence);
  }
}

/* ------------------------- InitializeSequence () ------------------------ */

/* Function that initializes variables for a new sequence structure.

   09/12/92 - Creation.
   29/01/93 - Added commentary field.
   30/01/93 - Added values of 1st SE's interval in order to have a correct
              percentage of work done displayed.
   08/02/93 - Initialize sequence file pointer.
   08/03/93 - Don't allocate memory for the commentary here so we can keep
              all the commentary (and not only the first 60 characters).
   21/03/93 - Added complemented flag to the sequence structure. */

int InitializeSequence (char *name, typSequence *SequencePtr)
{
  /* Initialize pointers */
  SequencePtr->sequence       = NULL;
  SequencePtr->bufferlist     = NULL;
  SequencePtr->lastbuffer     = NULL;
  SequencePtr->nbbuffers      = 0;
  SequencePtr->length         = 0;
  SequencePtr->nbsequences    = 0;
  SequencePtr->totnucleotides = 0;
  SequencePtr->totmatches     = 0;
  SequencePtr->scanfirst      = 0;
  SequencePtr->scanlength     = 0;
  SequencePtr->scanzoneok     = FALSE;
  SequencePtr->bufferlength   = bufferlength;
  SequencePtr->commentary     = NULL;
  SequencePtr->fsequence      = NULL;
  SequencePtr->complemented   = FALSE;

  /* Allocate memory for the sequence file name */
  if (! (SequencePtr->name = (char *) malloc (strlen (name) + 1)))
  {
    fprintf (stderr, "Error, memory allocation for the sequence name\n");
    return BUG;
  }

  strcpy (SequencePtr->name, name);

  return OK;
}

/* ---------------------------- MarkSequence () --------------------------- */

/* Function that marks the nucleotides in a sequence that will for sure
   lead to a bad solution. These are the nucleotides part of a stream of
   "N". We only consider the marked nucleotides for the first SE to search
   in the priority order array.

   11/02/93 - Creation.
              Added code to also mark the second element of the best
              priority order array (fastsearch switch).
   15/02/93 - Use the maxmark field in the motif structure. */

void MarkSequence (typMotif *MotifPtr, typSequence *SequencePtr)
{
  int i, j, index;
  long counter[6];
  long minlength[6];
  typSE *SEPtr;
  boolean nstream = FALSE;
  boolean markreverse[6];

  /* Initialize variables */
  for (i = 0; i < 6; i++)
  {
    counter[i] = 0;
    markreverse[i] = FALSE;
  }

  /* Initialize mark information for all SEs to mark */
  for (i = 0; i < MotifPtr->maxmark; i++)
  {
    /* Keep the index of current SE in the template */
    index = MotifPtr->bestpriority[i];

    /* Keep a pointer on that SE */
    SEPtr = &(MotifPtr->template[index]);

    /* Initialize minlength */
    if (SEPtr->type == 'S')
      minlength[i] = SEPtr->patlength;
    else
    {
      /* We'll have to mark reverse positions */
      markreverse[i] = TRUE;

      /* This helix has a restrictive pattern? */
      if (SEPtr->patlength > 0)
        minlength[i] = SEPtr->patlength;
      else
        minlength[i] = SEPtr->length.max;
    }
  }

  /* Do mark the 'N' nucleotides */
  for (i = 0; i < SequencePtr->length; i++)
  {
    /* Is that character a 'N' nucleotide? */
    if (SequencePtr->sequence[i] == BASE_N)
    {
      /* Are we starting a new stream of 'N'? */
      if (nstream == FALSE)
        nstream = TRUE;

      /* Increment "N" counters and mark if appropriate */
      for (j = 0; j < MotifPtr->maxmark; j++)
      {
        counter[j]++;

        if (counter[j] > minlength[j])
        {
          SequencePtr->sequence[i - minlength[j] + 1] |= rejectn [j];

          if (markreverse[j])
            SequencePtr->sequence[i] |= rejectr [j];
        }
      }
    }
    else
      /* Is that the end of a stream of 'N'? */
      if (nstream)
      {
        nstream = FALSE;

        /* Reset counters */
        for (j = 0; j < MotifPtr->maxmark; j++)
          counter[j] = 0;
      }
  }
}

/* ------------------------------ ReadEol () ------------------------------ */

/* Function that reads all the characters until the end of the line and
   saves them in the 's' character array.

   13/05/93 - Creation (Daniel Gauthere) */

void ReadEol (FILE *f, char *s)
{
  int c;
  int i = 0;

  while (((c = fgetc (f)) != '\n') && (c != EOF))
  {
    s[i] = c;
    i++;
  }
  s[i] = '\0';    
}

/* ---------------------------- ReadSequence () --------------------------- */

/* Function that reads a sequence in the sequence file. The values returned
   are:

    0 A bug occured in the treatment.
   -1 End of sequence file.
    1 Everything went ok.

   09/12/92 - Creation.
   29/01/93 - Read commentary into the sequence structure.
   08/02/93 - Keep sequence file pointer in the sequence structure.
   11/02/93 - Added markflag to indicate if we're interested in marking the
              nucleotides corresponding to bad matching positions for the
              first SE to search in the priority order array. This flag is
              necessary because in sequence alignment mode, we have to read
              the sequences a first time to analyse them (marking on) and
              then again to save the results in the solution file (marking
              off).
              Eliminated extra parameters and call MarkSequence from another
              point.
   15/02/93 - The sequence is now stored in a short int array.
   08/03/93 - Dynamically allocate memory for the sequence's commentary.
   21/03/93 - Initialize sequence's complemented flag.
   17/05/93 - Addition of code for reading FASTA or GENBANK formats for
              sequence files.
              Addition of code for implementing a demo version which limits
              the number of sequences that can be read to 10.
   17/06/93 - Correction of a bug that occured with GENBANK type sequences.
              It was due to an insufficient memory allocation for the
              comment. */

int ReadSequence (typSequence *SequencePtr)
{
  typBuffer *BufferPtr = NULL;
  int sequencepos = 0;
  int c, i;
  long begcomm, endcomm;
  char word[255], line[255], locus[255], comment[255];

  /* Are we reading the first sequence? */
  if (SequencePtr->nbsequences == 0)
  {
    /* Open sequence file */
    if (! (SequencePtr->fsequence = fopen (SequencePtr->name, "rb")))
    {
      fprintf (stderr, "Error opening sequence file \"%s\"\n",
			SequencePtr->name);
      return BUG;
    }
  }
  else
  {
    /* We have finished reading the sequence file? */
    if (SequencePtr->fsequence == NULL)
      return EOF;

    /* Clean up memory used by previous sequence */
    if (SequencePtr->sequence)
    {
      free (SequencePtr->sequence);
      SequencePtr->sequence = NULL;
    }

    /* Reset sequence length */
    SequencePtr->length = 0;

    /* Reset number of buffers */
    SequencePtr->nbbuffers = 0;
  }

  /* Demo version? */
  #ifdef DEMO

    /* Have we already read 10 sequences? */
    if (SequencePtr->nbsequences == 10)
    {
      fclose (SequencePtr->fsequence);
      SequencePtr->fsequence = NULL;
      return EOF;
    }

  #endif

  /* We have the end of file? */
  if (feof (SequencePtr->fsequence))
  {
    fclose (SequencePtr->fsequence);
    SequencePtr->fsequence = NULL;
    return EOF;
  }

  /* Find beginning of sequence */
  switch (fileformat)
  {
    case FASTA:
      /* Find the first '>' character */
      while (((c = getc (SequencePtr->fsequence)) != '>') &&
              (! feof (SequencePtr->fsequence)));
      break;

    case GENBANK:
      fscanf (SequencePtr->fsequence, "%s", word);

      while ((strcmp (word, "LOCUS")) != 0 && 
             (! feof (SequencePtr->fsequence)))
      {
        ReadEol (SequencePtr->fsequence, line);
        fscanf (SequencePtr->fsequence, "%s", word);
      }
      break;
  }

  /* We have the end of file? */
  if (feof (SequencePtr->fsequence))
  {
    fclose (SequencePtr->fsequence);
    SequencePtr->fsequence = NULL;
    return EOF;
  }

  switch (fileformat)
  {
    case FASTA:

      /* Keep the position of the beginning of the commentary */
      begcomm = ftell (SequencePtr->fsequence);

      /* Reach the end of line */
      while ((c = getc (SequencePtr->fsequence)) != '\n');

      /* Keep the position of the end of the commentary */
      endcomm = ftell (SequencePtr->fsequence);

      /* Allocate memory for the sequence's commentary */
      if (! (SequencePtr->commentary = (char *) malloc (endcomm - begcomm)))
      {
        fprintf (stderr, "Error, memory allocation for the sequence commentary\n");
        return BUG;
      }

      /* Get back at the beginning of the commentary */
      fseek (SequencePtr->fsequence, begcomm - endcomm, 1);

      /* Read the commentary */
      for (i = 0; i < endcomm - begcomm - 1; i++)
        SequencePtr->commentary [i] = getc (SequencePtr->fsequence);

      /* Put the end of string */
      SequencePtr->commentary[i] = '\0';

      /* Skip the end of line character */
      fscanf (SequencePtr->fsequence, "%*c");

      break;

    case GENBANK:

      fscanf (SequencePtr->fsequence, "%s", locus);
      ReadEol (SequencePtr->fsequence, line);
      fscanf (SequencePtr->fsequence, "%s", word);

      while ((strcmp (word, "DEFINITION")) != 0 && 
             (! feof (SequencePtr->fsequence)))
      {
        ReadEol (SequencePtr->fsequence, line);
        fscanf (SequencePtr->fsequence, "%s", word);
      }

      /* We have the end of file? */
      if (feof (SequencePtr->fsequence))
      {
        fclose (SequencePtr->fsequence);
        SequencePtr->fsequence = NULL;
        return EOF;
      }

      ReadEol (SequencePtr->fsequence, comment);
      sprintf (line, "%s %s", locus, comment);

      /* Allocate memory for the sequence's commentary */
      if (! (SequencePtr->commentary = (char *) malloc (strlen(line) + 1)))
      {
        fprintf (stderr, "Error, memory allocation for the sequence commentary\n");
        return BUG;
      }

      strcpy (SequencePtr->commentary, line);

      /* Find beginning of sequence */
      fscanf (SequencePtr->fsequence, "%s", word);

      while ((strcmp (word, "ORIGIN")) != 0 && 
             (! feof (SequencePtr->fsequence)))
      {
        ReadEol (SequencePtr->fsequence, line);
        fscanf (SequencePtr->fsequence, "%s", word);
      }

      ReadEol (SequencePtr->fsequence, line);

      break;
  }

  /* We have the end of file? */
  if (feof (SequencePtr->fsequence))
  {
    fclose (SequencePtr->fsequence);
    SequencePtr->fsequence = NULL;
    return EOF;
  }

  /* Read the sequence */
  c = getc (SequencePtr->fsequence);
  while ((((fileformat == FASTA) && (c != '>')) ||
          ((fileformat == GENBANK) && (c != '/'))) &&
         (! feof (SequencePtr->fsequence)))
  {
    /* Classify that base */
    c = BaseToMask (c);

    /* Is that character a valid base to add? */
    if (c)
    {
      /* Are we already working in an allocated memory buffer? */
      if (BufferPtr != NULL)
      {
	/* Add the character in it */
	BufferPtr->sequence[BufferPtr->length++] = c;

	/* Increment sequence length */
	SequencePtr->length++;

	/* Is that buffer full? */
	if (BufferPtr->length == SequencePtr->bufferlength)
	{
	  /* Are we adding the first buffer in the list? */
	  if (SequencePtr->bufferlist == NULL)
	    SequencePtr->bufferlist = BufferPtr;
	  else
	    SequencePtr->lastbuffer->next = BufferPtr;

	  /* Update last buffer pointer */
	  SequencePtr->lastbuffer = BufferPtr;

	  /* One more buffer in the list */
	  SequencePtr->nbbuffers++;

	  /* The temporary buffer is not to be used again */
	  BufferPtr = NULL;
	}
      }
      else
      {
	/* Allocate a memory buffer */
	if (! (BufferPtr = (typBuffer *) malloc (sizeof (typBuffer))))
	{
	  fprintf (stderr, "Error, memory allocation for a buffer\n");
	  return BUG;
	}

	/* Allocate memory for buffer's sequence */
	if (! (BufferPtr->sequence = (char *) malloc
				     (SequencePtr->bufferlength)))
	{
	  fprintf (stderr, "Error, memory allocation for a sequence buffer\n");
	  free (BufferPtr);
	  return BUG;
	}

	/* Add the character in it */
	BufferPtr->sequence[0] = c;

	/* Increment sequence length */
	SequencePtr->length++;

	/* Initialize buffer */
	BufferPtr->length = 1;
	BufferPtr->next = NULL;
      }
    }

    c = getc (SequencePtr->fsequence);
  }

  /* We have the end of file? */
  if (feof (SequencePtr->fsequence))
  {
    fclose (SequencePtr->fsequence);
    SequencePtr->fsequence = NULL;
  }

  /* Get back one character in the file */
  ungetc (c, SequencePtr->fsequence);

  /* Do we have to add a last buffer in the list? */
  if (BufferPtr)
  {
    /* Are we adding the first buffer in the list? */
    if (SequencePtr->bufferlist == NULL)
      SequencePtr->bufferlist = BufferPtr;
    else
      SequencePtr->lastbuffer->next = BufferPtr;

    /* Update last buffer pointer */
    SequencePtr->lastbuffer = BufferPtr;

    /* One more buffer in the list */
    SequencePtr->nbbuffers++;

    /* The temporary buffer is not to be used again */
    BufferPtr = NULL;
  }

  /* Allocate final sequence buffer */
  if (! (SequencePtr->sequence = (short int *)
         malloc (sizeof (short int) * (SequencePtr->length + 1))))
  {
    fprintf (stderr, "Error, memory allocation for the final sequence\n");
    return BUG;
  }

  /* Copy all the buffers in the final sequence */
  while (SequencePtr->bufferlist)
  {
    BufferPtr = SequencePtr->bufferlist;
    SequencePtr->bufferlist = BufferPtr->next;

    /* Copy this buffer's sequence in the final sequence */
    for (i = 0; i < BufferPtr->length; i++)
      SequencePtr->sequence[sequencepos++] = BufferPtr->sequence[i];

    /* Free sequence */
    free (BufferPtr->sequence);
    free (BufferPtr);
  }

  /* Mark the end of the sequence */
  SequencePtr->sequence[sequencepos] = 0;

  /* One more sequence read */
  SequencePtr->nbsequences++;

  /* Now, the sequence is not complemented */
  SequencePtr->complemented = FALSE;

  return OK;
}

/* --------------------------- SequenceFormat () -------------------------- */

/* Function that analyses a sequence file to determine its format.

   17/05/93 - Creation. */

int SequenceFormat (typSequence *SequencePtr)
{
  int c;

  /* Open sequence file */
  if (! (SequencePtr->fsequence = fopen (SequencePtr->name, "r")))
  {
    fprintf (stderr, "Error opening sequence file \"%s\"\n",
                      SequencePtr->name);
    return BUG;
  }
  
  /* Find first non blank character */
  do
  {
    c = getc (SequencePtr->fsequence);
  }
  while (((c == ' ') || (c == '\n')) && (c != EOF));

  /* We have the end of file? */
  if (feof (SequencePtr->fsequence))
  {
    fclose (SequencePtr->fsequence);
    SequencePtr->fsequence = NULL;

    fprintf (stderr, "Error, sequence file \"%s\" is empty\n",
                      SequencePtr->name);
    return BUG;
  }

  fclose (SequencePtr->fsequence);

  return (c == '>') ? FASTA : GENBANK;
}

/* --------------------------- TraceSequence () --------------------------- */

/* Debugging function that traces the information of a sequence structure.

   09/12/92 - Creation. */

void TraceSequence (typSequence *SequencePtr)
{
  int i;

  printf ("\n***** Sequence \"%s\" information *****\n", SequencePtr->name);

  printf ("Length of current sequence: %ld\n", SequencePtr->length);
  printf ("Number of sequences read: %d\n", SequencePtr->nbsequences);
  printf ("Number of buffers used: %d\n", SequencePtr->nbbuffers);

  printf ("First characters of that sequence:\n");
  for (i = 0; i < ((SequencePtr->length > 10) ? 10 : SequencePtr->length); i++)
    printf ("Car[%d]: %c\n", i, MaskToBase ((char) SequencePtr->sequence[i]));
}
