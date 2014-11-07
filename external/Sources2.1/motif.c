/* ------------------------------------------------------------------------
   Motif.c
   -------

     Functions that support motif file reading and motif structures
   initialization, with consistency checking and memory usage optimization. */

/* ------------------------------- Includes ------------------------------- */

#include <math.h>
#include "rnamot.h"

/* -------------------------- External variables -------------------------- */

extern boolean usemotifpriority;
extern boolean debugmode;

/* ----------------------------- BestOrder () ----------------------------- */

/* Function that generates the best order array corresponding to the values
   of search probability calculated by the PatternProbs () function.

   16/12/92 - Creation. */

void BestOrder (typMotif *MotifPtr)
{
  int i;
  int posmin;
  int finished = FALSE;
  float minprob;
  typSE *SEPtr;

  while (! finished)
  {
    /* Initialize values */
    minprob = 1.0;
    posmin = -1;

    /* Scan SE template to find minimum probability */
    for (i = 0; i < MotifPtr->nbSE; i++)
      if ((MotifPtr->template[i].probflag) &&
	  (MotifPtr->template[i].patprob < minprob))
      {
	posmin = i;
	minprob = MotifPtr->template[i].patprob;
      }

    /* We have found a lowest value? */
    if (posmin != -1)
    {
      /* Keep a pointer to that SE */
      SEPtr = &(MotifPtr->template[posmin]);

      /* Add this SE to the best priority order array */
      MotifPtr->bestpriority[MotifPtr->nbbestpriority++] = posmin;

      /* This SE shall not be consulted again */
      SEPtr->probflag = FALSE;

      /* Was that SE a stem? If so, the corresponding stem will also be
	 marked as no longer analysed. */
      if (SEPtr->type == 'H')
	MotifPtr->template[MotifPtr->stems[SEPtr->nb - 1].pos2].probflag =
	  FALSE;
    }
    else
      finished = TRUE;
  }
}

/* --------------------------- DistanceArray () --------------------------- */

/* Function that generates values for the SE distance array.

   20/12/92 - Creation. */

void DistanceArray (typMotif *MotifPtr)
{
  int i, j;
  int nbSE = MotifPtr->nbSE;

  /* Initialize distance array between all structural elements */
  for (i = 0; i < nbSE; i++)
  {
    MotifPtr->disttab[i * nbSE + i].min = 0;
    MotifPtr->disttab[i * nbSE + i].max = 0;

    if (i < nbSE - 1)
    {
      MotifPtr->disttab[i * nbSE + i + 1].min = 0;
      MotifPtr->disttab[i * nbSE + i + 1].max = 0;
    }

    for (j = i + 2; j < nbSE; j++)
    {
      MotifPtr->disttab[i * nbSE + j].min =
        MotifPtr->disttab[i * nbSE + j - 1].min +
        MotifPtr->template[j - 1].length.min;

      MotifPtr->disttab[i * nbSE + j].max =
        MotifPtr->disttab[i * nbSE + j - 1].max +
        MotifPtr->template[j - 1].length.max;
    }
  }

  /* Trace distance array values? */
  if (debugmode)
  {
    printf ("Distance array trace\n");
    for (i = 0; i < nbSE; i++)
    {
      printf ("Ligne %d: ", i);

      for (j = i; j < nbSE; j++)
        printf (" %ld:%ld", MotifPtr->disttab[i * nbSE + j].min,
                MotifPtr->disttab[i * nbSE + j].max);
      printf ("\n\n");
    }
  }
}

/* -------------------------- FindSingleStrand () ------------------------- */

/* Function that scans the template in order to find a particular single-
   strand element. If it is not found, returns -1, else returns the index
   of the element in the template array.

   01/12/92 - Creation. */

int FindSingleStrand (int SEnumber, typMotif *MotifPtr)
{
  int i;

  for (i = 0; i < MotifPtr->nbSE; i++)
    if ((MotifPtr->template[i].type == 'S') &&
	(MotifPtr->template[i].nb == SEnumber))
      return i;

  /* Single strand not found! */
  return -1;
}

/* ----------------------------- FreeMotif () ----------------------------- */

/* Function that cleans a motif structure.

   01/12/92 - Creation.
   16/12/92 - Best priority order array deallocation. */

void FreeMotif (typMotif *MotifPtr)
{
  int i;

  /* Free motif name */
  if (MotifPtr->name)
    free (MotifPtr->name);

  /* Free template array */
  if (MotifPtr->template)
  {
    /* Free restrictive patterns */
    for (i = 0; i < MotifPtr->nbSE; i++)
      if (MotifPtr->template[i].pattern)
        free (MotifPtr->template[i].pattern);

    free (MotifPtr->template);
  }

  /* Free stems array */
  if (MotifPtr->stems)
    free (MotifPtr->stems);

  /* Free priority order array */
  if (MotifPtr->priority)
    free (MotifPtr->priority);

  /* Free best priority order array */
  if (MotifPtr->bestpriority)
    free (MotifPtr->bestpriority);

  /* Free SE distances array */
  if (MotifPtr->disttab)
    free (MotifPtr->disttab);
}

/* -------------------------- InitializeMotif () -------------------------- */

/* Function that initializes variables for a new motif structure.

   01/12/92 - Creation.
   16/12/92 - Best priority order array initialization. */

int InitializeMotif (char *name, typMotif *MotifPtr)
{
  /* Initialize all pointers */
  MotifPtr->name         = NULL;
  MotifPtr->template     = NULL;
  MotifPtr->stems        = NULL;
  MotifPtr->priority     = NULL;
  MotifPtr->bestpriority = NULL;
  MotifPtr->disttab      = NULL;
  MotifPtr->maxwobbles   = MAXWOBBLES;
  MotifPtr->maxmismatchs = MAXMISMATCHS;

  /* We have to count the SE first */
  MotifPtr->countSEdone = FALSE;

  /* Allocate memory for the motif file name */
  if (! (MotifPtr->name = (char *) malloc (strlen (name) + 1)))
  {
    fprintf (stderr, "Error, memory allocation for the descriptor name\n");
    return BUG;
  }

  strcpy (MotifPtr->name, name);

  return OK;
}

/* ---------------------------- PatternProbs () --------------------------- */

/* Function that calculates the probabilities of finding each SE in regard
   to their restrictive patterns.

   16/12/92 - Creation.
   18/01/93 - Ajustment of helix probabilities to consider the fact that
              scanning helix is an algorithm in O (n * n) in worst case.
   30/01/93 - Modify probabilities of helixes to consider mismatches. If
              an helix has a restrictive pattern, then the mismatches are
              removed from the remaining space's (length.min - patlength)
              probability (since mismatches in the restrictive pattern
              itself are not considered).
   10/02/93 - Added a probability gain (penalty) for helixes. This gain
              takes into account the maximal width of an helix (maximum
              length of both stems plus maximum distance between the two
              stems).
              Corrections in the heuristic for probabilities lead to
              discover that taking in account the "free space" between
              the minimum length of a strand and its restrictive pattern
              was a bad idea. The old algorithm gave the same probability
              for a single strand like "S1 4:5 A " and "S1 4:5 AAAA". As
              we can see, the second one is really more restrictive than
              the first! The same thing happens with the helixes. Also,
              the adjustment of probabilities for helixes (putting an
              helix's probability to power 0.5 to take the order of the
              algorithm into account was also a mistake. Empirical tests
              shows that a value like 0.9 is a lot better. Finally, the
              penalty factor for helix width is observed to be best at
              around 0.5.

              Possible optimization:
              ---------------------

                Study the best value to give to an helix without
                restrictive pattern and also take the "free space" into
                account for single strands. */

void PatternProbs (typMotif *MotifPtr)
{
  int i, j;
  float prob, gain;
  int stem1, stem2;
  long minwidth, maxwidth;
  typSE *SE1, *SE2;
  typStemLoc *StemLocPtr;

  /* First, let's calculate the maximal width for each helix */
  for (i = 0; i < MotifPtr->nbH / 2; i++)
  {
    /* Keep index on both stems */
    stem1 = MotifPtr->stems[i].pos1;
    stem2 = MotifPtr->stems[i].pos2;

    /* Calculate maximal helix width */
    MotifPtr->stems[i].maxwidth =
      MotifPtr->template[stem1].length.max * 2 +
      MotifPtr->disttab[stem1 * MotifPtr->nbSE + stem2].max;

    /* Update minwidth and maxwidth values */
    if (i == 0)
    {
      minwidth = MotifPtr->stems[i].maxwidth;
      maxwidth = MotifPtr->stems[i].maxwidth;
    }
    else
    {
      if (MotifPtr->stems[i].maxwidth < minwidth)
        minwidth = MotifPtr->stems[i].maxwidth;

      if (MotifPtr->stems[i].maxwidth > maxwidth)
        maxwidth = MotifPtr->stems[i].maxwidth;
    }
  }

  /* Calculate initial probabilities in respect to the restrictive patterns
     and helix lengths */
  for (i = 0; i < MotifPtr->nbSE; i++)
  {
    /* Keep pointer on this SE */
    SE1 = &(MotifPtr->template[i]);

    /* The probability of this SE has not already been calculated? */
    if (! (SE1->probflag))
    {
      switch (SE1->type)
      {
	case 'S':

          /* Set initial probability value */
          prob = 1.0;

          /* This single strand has a restrictive pattern? */
          if (SE1->strict)
          {
            /* Calculate probability to find this pattern */
            for (j = 0; j < SE1->patlength; j++)
              prob *= NbBases (SE1->pattern[j]) / 4.0;
          }

          /* Keep the calculated probability */
          SE1->patprob = prob;

          /* The probability of this SE has been calculated */
          SE1->probflag = TRUE;

	  break;

	case 'H':

          /* Keep pointer on associated SE */
	  SE2 = &(MotifPtr->template[SE1->secondstemnb]);

	  /* This stem has a restrictive pattern? */
	  if (SE1->strict)
	  {
            /* Set initial probability value */
            prob = 1.0;

            /* Calculate probability to find this pattern */
            for (j = 0; j < SE1->patlength; j++)
            {
	      prob *= NbBases (SE1->pattern[j]) / 4.0;
              prob *= NbBases (SE2->pattern[SE2->patlength - j - 1]) / 4.0;
            }
	  }
	  else
	    prob = (float) pow (3.0 / 8.0,
                   (double) SE1->length.min - SE1->maxfaults);

          /* Keep the calculated probabilities */
          SE1->patprob = prob;
          SE2->patprob = prob;

          /* The probabilities of these SE had been calculated */
          SE1->probflag = TRUE;
          SE2->probflag = TRUE;

	  break;
      }
    }
  }

  /* Adjustment to take maximal helix width into account */
  if (maxwidth > minwidth)
  {
    for (i = 0; i < MotifPtr->nbH / 2; i++)
    {
      /* Keep a pointer on that StemLoc */
      StemLocPtr = &(MotifPtr->stems[i]);

      /* Keep pointers on those stems in the template */
      SE1 = &(MotifPtr->template[StemLocPtr->pos1]);
      SE2 = &(MotifPtr->template[StemLocPtr->pos2]);

      /* Calculate the probability gain of that helix */
      gain = (0.05 * (StemLocPtr->maxwidth - minwidth)) /
             (maxwidth - minwidth);

      /* Adjust the probability of that helix */
      SE1->patprob += gain;
      SE2->patprob += gain;

      /* If the probability of the helix is now greater than 1.0, we
         make a little adjustment just to be sure it's still gonna be
         searched */
      if (SE1->patprob >= 1.0)
      {
        SE1->patprob = 0.999999;
        SE2->patprob = 0.999999;
      }
    }
  }
}

/* ----------------------------- ReadMotif () ----------------------------- */

/* Fonction that reads a motif file and initializes a motif structure. When
   it is first called, the motif has its countSEdone flag set to FALSE so
   the function scans the motif file in order to count the number of SE it
   contains. It then sets this flag to TRUE and calls itself again. This
   time, it allocates all required memory and does a complete analysis of
   the motif file and initializes the appropriate fields of the motif
   structure.

   26/11/92 - Creation.
   30/11/92 - Restrictive patterns read.
   02/12/92 - Strict pattern detection.
   03/12/92 - Priority order array, maximum mismatchs allowed and lots
	      of consistency checking added.
   16/12/92 - Restrictive pattern length and probability added in SE
              structure. Priority of finding each SE calculated and best
              priority order array generated.
   21/01/93 - Added code to use motif's priority list if usemotifpriority
              switch is activated by the user.
   31/01/93 - Verify if there's something to search for when rnamot
              constructs its best priority order. In that case, we skip
              the priority order line in the motif file. If the [-p] switch
              is used, then we read the priority order line and verify if
              all its components are valid elements (either helixes or
              single-strands with restrictive patterns).
   03/02/93 - Added code to read the maximum number of wobbles (GU or UG
              pairs) allowed in the helixes. */

int ReadMotif (typMotif *MotifPtr)
{
  FILE *fmotif;
  char c;
  int i;
  int stem1;                      /* Position of first stem in template */
  int stem2;                      /* Position of last stem in template */
  int stempos;                    /* Position of a H in template */
  int strandpos;                  /* Position of a S in template */
  int SEnumber;                   /* A SE number */
  int maxfaults;                  /* Maximal number of mismatchs for SE */
  int stemNumber;                 /* A stem number */
  int nbS = 0;                    /* Number of a single-strand in treatment */
  int nbH = 0;                    /* Number of a stem in treatment */
  int finished;                   /* Flag used when reading priority order */
  int value;                      /* A numerical value read in the motif */
  typSE *SE;                      /* Temporary structural element pointer */
  typStemLoc *StemLoc;            /* Temporary stem location pointer */
  typInterval length;             /* Minimal and maximal length of a SE */

  /* Open motif file */
  if (! (fmotif = fopen (MotifPtr->name, "rb")))
  {
    fprintf (stderr, "Error opening descriptor file \"%s\"\n", MotifPtr->name);
    return BUG;
  }

  /* If SE elements are counted, allocate required memory */
  if (MotifPtr->countSEdone)
  {
    /* Allocate memory for template array */
    if (! (MotifPtr->template =
    (typSE *) malloc (sizeof (typSE) * MotifPtr->nbSE)))
    {
      fprintf (stderr, "Error, allocation of template array of descriptor"
                       " \"%s\"\n", MotifPtr->name);
      return BUG;
    }

    /* Initialize template array */
    for (i = 0; i < MotifPtr->nbSE; i++)
    {
      MotifPtr->template[i].described      = FALSE;
      MotifPtr->template[i].pattern        = NULL;
      MotifPtr->template[i].strict         = FALSE;
      MotifPtr->template[i].prioritymember = FALSE;
      MotifPtr->template[i].nb             = 0;
      MotifPtr->template[i].patlength      = 0;
      MotifPtr->template[i].patprob        = 0.0;
      MotifPtr->template[i].probflag       = FALSE;
    }

    /* Allocate memory for stems array? */
    if (MotifPtr->nbH > 1)
    {
      if (! (MotifPtr->stems = (typStemLoc *)
             malloc (sizeof (typStemLoc) * (MotifPtr->nbH / 2))))
      {
        fprintf (stderr, "Error, allocation of stems array of descriptor"
                         " \"%s\"\n", MotifPtr->name);
        return BUG;
      }

      /* Initialize stem array */
      for (i = 0; i < MotifPtr->nbH / 2; i++)
        MotifPtr->stems[i].firstseen = FALSE;
    }

    /* Allocate memory for motif priority order array */
    if (! (MotifPtr->priority = (int *)
           malloc (sizeof (int) * (MotifPtr->nbS + MotifPtr->nbH / 2))))
    {
      fprintf (stderr, "Error, allocation of priority order array of "
		       "descriptor \"%s\"\n", MotifPtr->name);
      return BUG;
    }

    /* Allocate memory for best priority order array */
    if (! (MotifPtr->bestpriority = (int *)
           malloc (sizeof (int) * (MotifPtr->nbS + MotifPtr->nbH / 2))))
    {
      fprintf (stderr, "Error, allocation of best priority order array of "
                       "descriptor \"%s\"\n", MotifPtr->name);
      return BUG;
    }

    /* Initial number of elements in priority order arrays */
    MotifPtr->nbpriority = 0;
    MotifPtr->nbbestpriority = 0;

    /* Allocate memory for distance array */
    if (! (MotifPtr->disttab = (typInterval *)
           malloc (sizeof (typInterval) * MotifPtr->nbSE * MotifPtr->nbSE)))
    {
      fprintf (stderr, "Error, allocation of distance array of descriptor "
                       " \"%s\"\n", MotifPtr->name);
      return BUG;
    }
  }

  /* Skip commentary lines */
  if (! SkipCommentLines (fmotif))
  {
    fprintf (stderr, "Error, descriptor file \"%s\" is empty\n",
                      MotifPtr->name);
    return BUG;
  }

  /* Find first valid SE */
  fscanf (fmotif, "%*[^HhSs\n]");
  fscanf (fmotif, "%c", &c);

  while (c != '\n')
  {
    switch (toupper ((int) c))
    {
      case 'H' :
        if (MotifPtr->countSEdone)
        {
          /* Keep pointer on SE */
          SE = &(MotifPtr->template[nbS + nbH]);

          SE->type = 'H';

	  /* Read the stem number */
	  fscanf (fmotif, "%d", &stemNumber);

          /* Verify if it's a valid stem number */
          if ((stemNumber < 1) || (stemNumber > MotifPtr->nbH / 2))
          {
            fprintf (stderr,
              "Error, invalid stem number (H%d) in SE list of descriptor"
              " \"%s\"\n", stemNumber, MotifPtr->name);
            fclose (fmotif);
            return BUG;
          }

	  /* Keep the number */
          SE->nb = stemNumber;

          /* Keep pointer on stem location structure */
	  StemLoc = &(MotifPtr->stems[stemNumber - 1]);

          /* Is that the first stem? */
	  if (! StemLoc->firstseen)
	  {
	    StemLoc->firstseen = TRUE;
	    StemLoc->pos1 = nbS + nbH;
	  }
	  else
          {
	    StemLoc->pos2 = nbS + nbH;
            MotifPtr->template[StemLoc->pos1].secondstemnb = nbS + nbH;
            MotifPtr->template[StemLoc->pos2].secondstemnb = StemLoc->pos1;
          }
	}

	nbH++;

	break;

      case 'S' :
	if (MotifPtr->countSEdone)
	{
	  MotifPtr->template[nbS + nbH].type = 'S';
	  fscanf (fmotif, "%d", &SEnumber);

	  /* Verify if it's a valid single-strand number */
	  if ((SEnumber < 1) || (SEnumber > MotifPtr->nbS))
	  {
	    fprintf (stderr,
	      "Error, invalid single-strand number (S%d) in SE list of "
              "descriptor \"%s\"\n", SEnumber, MotifPtr->name);
	    fclose (fmotif);
	    return BUG;
	  }

	  /* Verify if this single-strand is already read */
	  if (FindSingleStrand (SEnumber, MotifPtr) != -1)
	  {
	    fprintf (stderr,
	      "Error, multiple single-strand number (S%d) in SE list of "
              "descriptor \"%s\"\n", SEnumber, MotifPtr->name);
	    fclose (fmotif);
	    return BUG;
	  }

	  /* Keep the number */
	  MotifPtr->template[nbS + nbH].nb = SEnumber;
	}

	nbS++;

	break;

      default :
	fprintf (stderr, "Invalid list of structural elements "
			 "in descriptor \"%s\"\n", MotifPtr->name);
	fclose (fmotif);
	return BUG;
    }

    /* If we are counting SE, skip the SE number */
    if (! MotifPtr->countSEdone)
      fscanf (fmotif, "%*d");

    /* Reach next SE */
    fscanf (fmotif, "%*[^HhSs\n]");
    fscanf (fmotif, "%c", &c);
  }

  /* If we are counting SE, then update counters and continue analyze */
  if (! MotifPtr->countSEdone)
  {
    MotifPtr->nbS = nbS;
    MotifPtr->nbH = nbH;
    MotifPtr->nbSE = nbS + nbH;

    /* We have a odd number of stems? */
    if (MotifPtr->nbH % 2)
    {
      fprintf (stderr, "Odd number of stems in SE list of descriptor \"%s\"\n",
                        MotifPtr->name);
      fclose (fmotif);
      return BUG;
    }

    MotifPtr->countSEdone = TRUE;
    fclose (fmotif);
    return ReadMotif (MotifPtr);
  }

  /* Skip commentary lines */
  if (! SkipCommentLines (fmotif))
  {
    fprintf (stderr, "Error, descriptor file \"%s\" contains no SE "
                     "descriptors\n", MotifPtr->name);
    return BUG;
  }

  /* Find first valid SE descriptor */
  fscanf (fmotif, "%*[^HhSs]");
  fscanf (fmotif, "%c", &c);

  while (! feof (fmotif) && (c != EOF))
  {
    switch (toupper ((int) c))
    {
      case 'H':
	/* Read the SE number */
	fscanf (fmotif, "%d", &SEnumber);

	/* This stem exists? */
        if ((SEnumber < 0) || (SEnumber > MotifPtr->nbH / 2))
        {
          fprintf (stderr,
            "Error, inexistant H%d in descriptor \"%s\"\n",
            SEnumber, MotifPtr->name);
          fclose (fmotif);
          return BUG;
        }

        /* Memorize index of stems in template */
        stem1 = MotifPtr->stems[SEnumber - 1].pos1;
        stem2 = MotifPtr->stems[SEnumber - 1].pos2;

        /* This stem has already been described? */
        if (MotifPtr->template[stem1].described)
        {
	  fprintf (stderr,
            "Error, multiple description entries for stem H%d of descriptor"
            " \"%s\"\n", SEnumber, MotifPtr->name);
	  fclose (fmotif);
          return BUG;
        }

        /* Read min and max lengths and max mismachs allowed */
	fscanf (fmotif, "%ld:%ld %d",
                         &(length.min), &(length.max), &maxfaults);

	/* This interval is valid? */
	if (length.max < length.min)
	{
	  fprintf (stderr,
	    "Error, inconsistance in length of H%d in descriptor "
	    " \"%s\"\n", SEnumber, MotifPtr->name);
          fclose (fmotif);
	  return BUG;
	}

	/* Memorize stem intervals */
        MotifPtr->template[stem1].length = length;
        MotifPtr->template[stem2].length = length;

	/* Memorize stem maximum faults */
	MotifPtr->template[stem1].maxfaults = maxfaults;
	MotifPtr->template[stem2].maxfaults = maxfaults;

	/* This stem has been described */
        MotifPtr->template[stem1].described = TRUE;
	MotifPtr->template[stem2].described = TRUE;

        /* Read restrictive pattern if present */
        if (! ReadSEPattern (MotifPtr, fmotif, stem1, stem2))
        {
          fclose (fmotif);
          return BUG;
        }

        /* Skip commentary lines */
        if (SkipCommentLines (fmotif))
          /* Read beginning of next line */
          c = getc (fmotif);

	break;

      case 'S' :

	/* Read the SE number */
	fscanf (fmotif, "%d", &SEnumber);

	/* This single-strand exists? */
	if ((SEnumber < 0) || (SEnumber > MotifPtr->nbS))
	{
	  fprintf (stderr,
	    "Error, inexistant single-strand (S%d) in descriptor "
	     "\"%s\"\n", SEnumber, MotifPtr->name);
	  fclose (fmotif);
	  return BUG;
	}

	/* Find the position of this SE in template */
	if ((strandpos = FindSingleStrand (SEnumber, MotifPtr)) == -1)
	{
	  fprintf (stderr,
	    "Error, inexistant single-strand (S%d) in descriptor "
            "\"%s\"\n", SEnumber, MotifPtr->name);
          fclose (fmotif);
          return BUG;
        }

        /* This single-strand has already been described? */
        if (MotifPtr->template[strandpos].described)
        {
          fprintf (stderr,
            "Error, multiple description entries for single-strand S%d in "
            "descriptor \"%s\"\n", SEnumber, MotifPtr->name);
          fclose (fmotif);
          return BUG;
        }

        /* Read min and max lengths */
        fscanf (fmotif, "%d:%d", &(length.min), &(length.max));

        /* This interval is valid? */
        if (length.max < length.min)
        {
          fprintf (stderr,
	    "Error, inconsistance in length of S%d in descriptor "
            "\"%s\"\n", SEnumber, MotifPtr->name);
          fclose (fmotif);
          return BUG;
	}

        /* Memorize single-strand interval */
        MotifPtr->template[strandpos].length = length;

	/* Read restrictive pattern if present */
        if (! ReadSEPattern (MotifPtr, fmotif, strandpos, strandpos))
        {
          fclose (fmotif);
          return BUG;
        }

        /* This single-strand has been described */
        MotifPtr->template[strandpos].described = TRUE;

        /* Skip commentary lines */
        if (SkipCommentLines (fmotif))
          /* Read beginning of next line */
          c = getc (fmotif);

        break;

      case 'R' :

        /* Verify if all SE descriptors had been read */
        for (i = 0; i < MotifPtr->nbSE; i++)
          if (MotifPtr->template[i].described == FALSE)
          {
            fprintf (stderr, "Error, description of %c%d missing in descriptor"
              " \"%s\"\n", MotifPtr->template[i].type, MotifPtr->template[i].nb,
              MotifPtr->name);
            fclose (fmotif);
	    return BUG;
          }

        /* User has not selected [-p]? Don't read the priority order line! */
        if (! usemotifpriority)
        {
          fscanf (fmotif, "%*[^\n]");
          fscanf (fmotif, "%*c");

          finished = TRUE;
        }
        else
          finished = FALSE;

        while (! finished)
        {
          /* Skip blanks */
          while ((c = getc (fmotif)) == ' ');

          switch (toupper ((int) c))
	  {
            case 'H' :

              /* Are we supposed to be finished? */
	      if (MotifPtr->nbpriority == (MotifPtr->nbS + MotifPtr->nbH / 2))
              {
                fprintf (stderr, "Error, too many entries in priority list "
                         "of descriptor \"%s\"\n", MotifPtr->name);
		fclose (fmotif);
		return BUG;
              }

	      /* Read the SE number */
              fscanf (fmotif, "%d", &SEnumber);
              
              /* This stem exists? */
              if ((SEnumber < 0) || (SEnumber > MotifPtr->nbH / 2))
              {
                fprintf (stderr, "Error, invalid stem number of priority"
			 "list of descriptor \"%s\"\n", MotifPtr->name);
                fclose (fmotif);
                return BUG;
              }

              /* Find position of first stem in template */
              stempos = MotifPtr->stems[SEnumber - 1].pos1;

              /* Is this stem already member of the priority list? */
              if (MotifPtr->template[stempos].prioritymember)
              {
                fprintf (stderr, "Error, duplicate stem (H%d) in priority"
                         "list of descriptor \"%s\"\n",
                         MotifPtr->template[stempos].nb, MotifPtr->name);
                fclose (fmotif);
                return BUG;
              }

              /* Add this SE in priority array */
              MotifPtr->priority[MotifPtr->nbpriority++] = stempos;

              /* Mark this stem as a member of priority list */
              MotifPtr->template[stempos].prioritymember = TRUE;

              break;

	    case 'S' :

              /* Are we supposed to be finished? */
	      if (MotifPtr->nbpriority == (MotifPtr->nbS + MotifPtr->nbH / 2))
	      {
                fprintf (stderr, "Error, too many entries in priority list "
                  "of descriptor \"%s\"\n", MotifPtr->name);
                fclose (fmotif);
		return BUG;
	      }

              /* Read the SE number */
	      fscanf (fmotif, "%d", &SEnumber);

              /* This single-strand exists? */
              if ((SEnumber < 0) || (SEnumber > MotifPtr->nbS))
              {
                fprintf (stderr, "Error, invalid single-strand number of "
                  "priority list of descriptor \"%s\"\n", MotifPtr->name);
                fclose (fmotif);
                return BUG;
              }

              /* Find the position of this SE in template */
              if ((strandpos = FindSingleStrand (SEnumber, MotifPtr)) == -1)
              {
                fprintf (stderr, "Error, inexistant single-strand number in "
                  "priority list of descriptor \"%s\"\n",
                  SEnumber, MotifPtr->name);
                fclose (fmotif);
                return BUG;
              }

              /* Is this single-strand already member of the priority list? */
	      if (MotifPtr->template[strandpos].prioritymember)
              {
                fprintf (stderr, "Error, duplicate single-strand (S%d) in "
                  "priority list of descriptor \"%s\"\n",
                  MotifPtr->template[strandpos].nb, MotifPtr->name);
                fclose (fmotif);
                return BUG;
              }

              /* Does that single-strand have a restrictive pattern? */
	      if (! MotifPtr->template[strandpos].strict)
              {
                fprintf (stderr, "Error, no restrictive pattern for "
                  "single-strand S%d in priority list of descriptor \"%s\"\n",
                  MotifPtr->template[strandpos].nb, MotifPtr->name);
                fclose (fmotif);
                return BUG;
              }

	      /* Add this SE in priority array */
              MotifPtr->priority[MotifPtr->nbpriority++] = strandpos;

              /* Mark this single-strand as a member of priority list */
	      MotifPtr->template[strandpos].prioritymember = TRUE;

              break;

            case '\n' :

	      /* End of priority list */
              finished = TRUE;

	      break;

            default :

              fprintf (stderr, "Error, invalid character in priority list of "
                "descriptor \"%s\"\n", SEnumber, MotifPtr->name);
              fclose (fmotif);
	      return BUG;
          }
        }

        /* Skip commentary lines */
        if (SkipCommentLines (fmotif))
          /* Read beginning of next line */
          c = getc (fmotif);

        break;

      case 'M' :

        /* Read the maximum number of mismatchs allowed */
        fscanf (fmotif, "%d", &value);

        /* Does that value makes sense? */
        if (value >= 0)
          MotifPtr->maxmismatchs = value;

        /* Skip commentary lines */
        if (SkipCommentLines (fmotif))
          /* Read beginning of next line */
          c = getc (fmotif);

        break;

      case 'W' :

        /* Read the maximum number of wobbles allowed */
        fscanf (fmotif, "%d", &value);

        /* Does that value makes sense? */
        if (value >= 0)
          MotifPtr->maxwobbles = value;

        /* Skip commentary lines */
        if (SkipCommentLines (fmotif))
          /* Read beginning of next line */
          c = getc (fmotif);

        break;

      case '\n' :

        /* Skip commentary lines */
        if (SkipCommentLines (fmotif))
          /* Read beginning of next line */
          c = getc (fmotif);

        break;

      default:

        /* Reach the end of line */
	fscanf (fmotif, "%*[^\n]");
	fscanf (fmotif, "%*c");
        fscanf (fmotif, "%c", &c);

        break;
    }
  }

  fclose (fmotif);

  /* Verify if all SE descriptors had been read */
  for (i = 0; i < MotifPtr->nbSE; i++)
    if (MotifPtr->template[i].described == FALSE)
    {
      fprintf (stderr, "Error, description of %c%d missing in descriptor"
        " \"%s\"\n", MotifPtr->template[i].type, MotifPtr->template[i].nb,
        MotifPtr->name);
      fclose (fmotif);
      return BUG;
    }

  /* Generate distance array */
  DistanceArray (MotifPtr);

  /* If the user does not want to use the optimal priority list, use the
     one in the motif */
  if (usemotifpriority)
  {
    /* Copy the motif priority list in the best priority list (all the rest
       of the program works with the best priority list) */
    if (MotifPtr->nbpriority > 0)
    {
      /* We had a priority order list in the motif */
      for (i = 0; i < MotifPtr->nbpriority; i++)
        MotifPtr->bestpriority[i] = MotifPtr->priority[i];

      /* Update the number of elements in the best order list */
      MotifPtr->nbbestpriority = MotifPtr->nbpriority;
    }
    else
    {
      /* There was no priority list, so we order the search elements by
         helix numbers (like in Rnamot version 1.1) */
      for (i = 0; i < MotifPtr->nbH / 2; i++)
        MotifPtr->bestpriority[i] = MotifPtr->stems[i].pos1;

      /* Update the number of elements in the best order list */
      MotifPtr->nbbestpriority = MotifPtr->nbH / 2;
    }
  }
  else
  {
    /* Calculate the search probabilities of each SE */
    PatternProbs (MotifPtr);

    if (debugmode)
    {
      printf ("**> Trace of computed probabilities for SE:\n");

      for (i = 0; i < MotifPtr->nbSE; i++)
        printf ("Prob of %c%d (length: %d): %f\n",
                MotifPtr->template[i].type,
                MotifPtr->template[i].nb,
                MotifPtr->template[i].patlength,
                MotifPtr->template[i].patprob);
    }

    /* Generate best priority order array */
    BestOrder (MotifPtr);

    /* We have nothing to search for? */
    if (MotifPtr->nbbestpriority == 0)
    {
      fprintf (stderr, "Error, descriptor \"%s\" contains nothing that can be "
                       "searched\n", MotifPtr->name);
      return BUG;
    }
  }

  /* Trace best priority order array */
  if (debugmode)
  {
    printf ("**> Trace of best priority array (usemotifpriority: %s):\n",
            (usemotifpriority) ? "YES" : "NO");

    for (i = 0; i < MotifPtr->nbbestpriority; i++)
      printf ("%c%d, prob: %f\n",
              MotifPtr->template[MotifPtr->bestpriority[i]].type,
              MotifPtr->template[MotifPtr->bestpriority[i]].nb,
              MotifPtr->template[MotifPtr->bestpriority[i]].patprob);
  }

  /* If the optimal priority order array contains more than 6 structural
     elements to be searched, then the maximum number of marked elements
     is 6. If it is less than of equal to 6 then the maximum number of
     marked elements is the number of elements to search. */
  if ((MotifPtr->maxmark = MotifPtr->nbbestpriority) > 6)
    MotifPtr->maxmark = 6;

  return OK;
}

/* --------------------------- ReadSEPattern () --------------------------- */

/* Function that reads a restrictive pattern either for a stem or for a
   single-strand. If the pattern if for a stem, it does verifies the length
   of both parts.

   02/12/92 - Creation.
   16/12/92 - Restrictive pattern length memorized in the SE.
   17/01/93 - Restrictive pattern if present must be of length equal to min
              length. */

int ReadSEPattern (typMotif *MotifPtr, FILE *fmotif, int pos1, int pos2)
{
  char c;
  int i;
  int patlength;
  int doublepattern = FALSE;
  int strict;

  /* Find first character of pattern restriction if present */
  while ((c = getc (fmotif)) == ' ');

  /* We have a pattern? */
  if (c != '\n')
  {
    /* Count the number of characters in the pattern */
    patlength = 0;
    while ((c != '\n') && (c != ':') && (c != ' '))
    {
      patlength++;

      /* Determine the type of restrictive pattern (strict or not strict) */
      if (patlength == 1)
	strict = isupper (c);
      else
	/* We have a inconsistant character in that pattern? */
	if ((! BaseToMask ((int) c)) ||
	    (isupper (c) && ! strict) || (islower (c) && strict))
	{
          fprintf (stderr, "Error, inconsistant restrictive pattern in %c%d "
                   "of descriptor \"%s\"\n", MotifPtr->template[pos1].type,
                   MotifPtr->template[pos1].nb, MotifPtr->name);
	  return BUG;
	}

      c = getc (fmotif);
    }

    /* Verify if the length of the pattern is too long (greater than min) */
    if (patlength > MotifPtr->template[pos1].length.min)
    {
      fprintf (stderr, "Error, restrictive pattern of %c%d in descriptor "
               "\"%s\" is too long\n", MotifPtr->template[pos1].type,
               MotifPtr->template[pos1].nb, MotifPtr->name);
      return BUG;
    }

    /* Allocate buffer for first SE's restrictive pattern */
    if (! (MotifPtr->template[pos1].pattern = (char *) malloc (patlength + 1)))
    {
      fprintf (stderr, "Error, allocation of pattern array of %c%d in "
                       "descriptor \"%s\"\n", MotifPtr->template[pos1].type,
                       MotifPtr->template[pos1].nb, MotifPtr->name);
      return BUG;
    }

    /* Allocate buffer for second restrictive pattern? */
    if (c == ':')
    {
      /* We are treating a single-strand element? */
      if (pos1 == pos2)
      {
	fprintf (stderr, "Error, double restricive pattern for "
	  "single-strand %c%d in descriptor \"%s\"\n",
          MotifPtr->template[pos1].type,
          MotifPtr->template[pos1].nb, MotifPtr->name);
	return BUG;
      }

      /* Allocate buffer for second stem's restrictive pattern */
      if (! (MotifPtr->template[pos2].pattern =
	    (char *) malloc (patlength + 1)))
      {
	fprintf (stderr,
	  "Error, allocation of second pattern array of %c%d in descriptor "
          "\"%s\"\n", MotifPtr->template[pos2].type,
          MotifPtr->template[pos2].nb, MotifPtr->name);
	return BUG;
      }

      /* We are reading a double restrictive pattern */
      doublepattern = TRUE;
    }

    /* Get back at beginning of pattern */
    fseek (fmotif, - patlength - 1, 1);

    /* Read first restrictive pattern */
    for (i = 0; i < patlength; i++)
      MotifPtr->template[pos1].pattern[i] = BaseToMask (getc (fmotif));

    /* Set end of pattern string */
    MotifPtr->template[pos1].pattern[patlength] = '\0';

    /* Keep strict flag in the SE */
    MotifPtr->template[pos1].strict = strict;

    /* Keep pattern length in the SE */
    MotifPtr->template[pos1].patlength = patlength;

    /* Read a second restrictive pattern? */
    if (doublepattern)
    {
      /* Skip the ':' character */
      (void) getc (fmotif);

      for (i = 0; i < patlength; i++)
      {
	c = getc (fmotif);

	/* We have an invalid character in that restrictive pattern? */
	if ((! BaseToMask ((int) c)) ||
	    (isupper (c) && ! strict) || (islower (c) && strict))
	{
	  fprintf (stderr, "Error, inconsistance in restrictive pattern of "
            "%c%d in descriptor \"%s\"\n", MotifPtr->template[pos2].type,
            MotifPtr->template[pos2].nb, MotifPtr->name);
	  return BUG;
	}

	MotifPtr->template[pos2].pattern[i] = BaseToMask ((int) c);
      }

      /* Set end of pattern string */
      MotifPtr->template[pos2].pattern[patlength] = '\0';

      /* Keep strict flag in the SE */
      MotifPtr->template[pos2].strict = strict;

      /* Keep pattern length in the SE */
      MotifPtr->template[pos2].patlength = patlength;
    }

    c = getc (fmotif);

    /* We are at the end of the pattern? */
    if ((c != '\n') && (c != ' '))
    {
      fprintf (stderr,
	"C: %c (%d), Error, inconsistance in restrictive pattern of %c%d "
	"in descriptor \"%s\"\n", c, (int) c, MotifPtr->template[pos1].type,
	MotifPtr->template[pos1].nb, MotifPtr->name);
      return BUG;
    }

    /* Reach end of line */
    while (c != '\n') c = getc (fmotif);
  }

  return OK;
}

/* -------------------------- SkipCommentLines () ------------------------- */

/* Function that skip all empty lines or comment lines in a file.

   13/01/92 - Creation. */

int SkipCommentLines (FILE *f)
{
  char c;
  int valid = FALSE;

  /* We are at the end of the file? */
  if (feof (f))
    return 0;

  /* Read characters until we have a valid beginning of line */
  while (! valid)
  {
    c = getc (f);

    if ((c != '\n') && (c != '#'))
    {
      valid = TRUE;

      /* Get back one character in the back */
      if (ungetc ((int) c, f) == EOF)
        return 0;

      continue;
    }

    /* If that's a commentary line, we skip it (return character included) */
    if (c == '#')
      fscanf (f, "%*[^\n]%*c");
  }

  return 1;
}

/* ---------------------------- TraceMotif () ----------------------------- */

/* Debugging function that traces the information of a motif structure.

   09/12/92 - Creation.
   15/02/93 - Trace maxmark value. */

void TraceMotif (typMotif *MotifPtr)
{
  int i, j;
  typSE *stem1, *stem2;
  typSE *SE;

  printf ("\n***** Descriptor \"%s\" information *****\n", MotifPtr->name);

  printf ("\n-- Number of structural elements and mismatchs\n");
  printf ("NbS: %d, NbH: %d, NbSE: %d, MaxMismatchs: %d, MaxWobbles: %d, MaxMark: %d\n",
	   MotifPtr->nbS, MotifPtr-> nbH, MotifPtr->nbSE,
	   MotifPtr->maxmismatchs, MotifPtr->maxwobbles, MotifPtr->maxmark);

  printf ("\n-- Stem trace\n");
  for (i = 0; i < MotifPtr->nbH / 2; i++)
  {
    stem1 = &(MotifPtr->template[MotifPtr->stems[i].pos1]);
    stem2 = &(MotifPtr->template[MotifPtr->stems[i].pos2]);

    printf ("H%d (stem1: %02d, stem2: %02d) %ld:%ld %d ",
	    stem1->nb,
	    MotifPtr->stems[i].pos1, MotifPtr->stems[i].pos2,
	    stem1->length.min,stem1->length.max, stem1->maxfaults);

    if (stem1->patlength > 0)
    {
      for (j = 0; j < stem1->patlength; j++)
	printf ("%c", MaskToBase (stem1->pattern[j]));

      printf (":");

      for (j = 0; j < stem2->patlength; j++)
	printf ("%c", MaskToBase (stem2->pattern[j]));

      printf (" (strict: %s)\n", (stem1->strict) ? "YES" : "NO");
    }
    else
      printf ("\n");
  }

  printf ("\n-- Single-strands trace\n");
  for (i = 0; i < MotifPtr->nbSE; i++)
  {
    SE = &(MotifPtr->template[i]);

    if (SE->type == 'S')
    {
      printf ("s%d %ld:%ld ", SE->nb, SE->length.min, SE->length.max);

      if (SE->patlength > 0)
      {
	if (SE->strict)
	  for (j = 0; j < SE->patlength; j++)
	    printf ("%c", MaskToBase (SE->pattern[j]));
	else
	  for (j = 0; j < SE->patlength; j++)
	    printf ("%c", tolower ((int) MaskToBase (SE->pattern[j])));

	printf (" (strict: %s)\n", (SE->strict) ? "YES" : "NO");
      }
      else
	printf ("\n");
    }
  }

  printf ("\n");
}
