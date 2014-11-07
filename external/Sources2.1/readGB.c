/* Reads Genbank format (NCBI flat file) */
/*---------------------------------------*/

void read_eol (f, s)
  FILE *f;
  char *s;
{
  int c;
  int i = 0;
  while (((c = fgetc (f)) != '\n') && (c != EOF)) {
    s[i] = c;
    i++;
  }
  s[i] = '\0';    
}

int ReadSequenceGB (typSequence *SequencePtr)
{
  typBuffer *BufferPtr = NULL;
  int sequencepos = 0;
  int c, i;
  long begcomm, endcomm;
  char word[255], line[255];

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

  /* We have the end of file? */
  if (feof (SequencePtr->fsequence))
  {
    fclose (SequencePtr->fsequence);
    SequencePtr->fsequence = NULL;
    return EOF;
  }

  /* Find beginning of sequence */

  fscanf (f, "%s", word);
  while ((strcmp (word, "DEFINITION")) != 0 && 
	           (! feof (SequencePtr->fsequence))) {
    read_eol (f, line);
    fscanf (f, "%s", word);
  }

  /* We have the end of file? */
  if (feof (SequencePtr->fsequence))
  {
    fclose (SequencePtr->fsequence);
    SequencePtr->fsequence = NULL;
    return EOF;
  }

  read_eol (f, line);

  /* Allocate memory for the sequence's commentary */
  if (! (SequencePtr->commentary = (char *) malloc (strlen(line))))
  {
    fprintf (stderr, "Error, memory allocation for the sequence commentary\n");
    return BUG;
  }

  strcpy (SequencePtr->commentary, line);

  fscanf (f, "%s", word);
  while ((strcmp (word, "ORIGIN")) != 0 && 
	           (! feof (SequencePtr->fsequence))) {
    read_eol (f, line);
    fscanf (f, "%s", word);
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
  while ((c != '/') && (! feof (SequencePtr->fsequence)))
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

