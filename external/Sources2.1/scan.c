/* ------------------------------------------------------------------------
   Scan.c
   ------

     Functions that support sequence scanning and pattern matching. */

/* ------------------------------- Includes ------------------------------- */

#include "rnamot.h"

/* ------------------------------ Constants ------------------------------- */

/* 03/04/93: Use of a DEBUG constant which compiles a version of Rnamot
             that displays search intervals of single-strands and helixes
             and positions of partial and complete matches. This is only
             for debugging purpose and should be turned of for compiling
             the final version. */

/*
#define	DEBUG
*/


/* Compilation switch for the modifications of 04/04/93 that reinforces
   the interval verification allocated for helixes and assures a better
   search performance for helixes without restrictive patterns. */

#define INTERVALCHECK


/* -------------------------- External variables -------------------------- */

/* rnamot.c */
extern int mode;
extern boolean silent;
extern boolean noalternative;
extern boolean fastsearch;
extern boolean debugmode;

/* energy.c */
extern char BaseToPair [16][16];

/* sequence.c */
extern short int rejectn [6];
extern short int rejectr [6];


/* ----------------------------- Alignment () ----------------------------- */

/* Function that searches sequences for the best match possible and if not
   found, the best fault is kept. Then, the sequences are aligned and saved
   in output files.

   07/02/93 - Creation.
   08/02/93 - Alignment and saving of results coded.
   10/02/93 - Use [-a] switch in alignment mode.
   08/05/93 - Elimination of the [-a] switch.
   09/05/93 - Now align the solutions on the single-strands that have non
              NULL first and last values (they must not necessary have a
              restrictive pattern). To do that, we find the maximum length
              of that strand in all the solutions found. That value is
              then assigned back to ALL the "length" fields of all the
              found sequences. The SaveGrid () function now verifies if the
              length value is greater than the "last - first + 1" value, in
              which case it outputs the correct amount of delimiter chars.
*/

int Alignment (typMotif *MotifPtr, typSequence *SequencePtr,
               typSolution *SolutionPtr)
{
  int SE;
  int index;
  int finished = FALSE;
  int nbfaults = 0;
  int maxpos, maxspace;
  int minlength;
  boolean firstfault;
  typSE *SEPtr;
  typGrid *GridPtr;
  typGridList *ListTemp;
  typStrand *StrandPtr;

  /* Create grid */
  if (! (GridPtr = CreateGrid (MotifPtr)))
    return BUG;

  /* Analyze sequences */
  while (! finished)
  {
    switch (ReadSequence (SequencePtr))
    {
      case EOF:
	finished = TRUE;
	break;

      case BUG:

        /* Free search grid */
        FreeGrid (GridPtr);

        return BUG;
        break;

      case OK:

        /* Create grids */
        if ((! (SolutionPtr->bestgrid = CreateGrid (MotifPtr))) ||
            (! (SolutionPtr->bestfault = CreateGrid (MotifPtr))))
        {
          fprintf (stderr, "Error, unable to create grids for solution\n");
          return BUG;
        }

        /* Initialize last position displayed (when silent is FALSE) */
        SequencePtr->lastout = 0;

        /* The values for percentage of work done are not yet entered */
        SequencePtr->scanzoneok = FALSE;

	/* Can we speak? Display initial percentage of work done */
	if (! silent)
          DisplayRunData (SequencePtr, SolutionPtr, 0);

        /* Mark the sequence */
        if (fastsearch)
          MarkSequence (MotifPtr, SequencePtr);

        /* Do the pattern matching */
        FindMotif (MotifPtr, SequencePtr, SolutionPtr, GridPtr, 0);

        /* If we can speak, display number of matches */
        if (! silent)
          DisplayRunData (SequencePtr, SolutionPtr, 100);

        /* We found a best grid (a real solution)? */
        if (SolutionPtr->bestgrid->score != INITIALSCORE)
        {
          /* Add this grid in the solution structure */
          if (! InsertGrid (SolutionPtr->bestgrid, SolutionPtr))
            return BUG;
        }
        else
        {
          /* Add this grid in the solution structure */
          if (! InsertGrid (SolutionPtr->bestfault, SolutionPtr))
            return BUG;

          /* One more fault */
          nbfaults++;
        }

        /* Free solution grids */
        if (SolutionPtr->bestgrid)
        {
          FreeGrid (SolutionPtr->bestgrid);
          SolutionPtr->bestgrid = NULL;
        }

        if (SolutionPtr->bestfault)
        {
          FreeGrid (SolutionPtr->bestfault);
          SolutionPtr->bestfault = NULL;
        }

	break;
    }
  }

  /* Free search grid */
  FreeGrid (GridPtr);

  /* Open results file */
  if (! (SolutionPtr->fsol = fopen (SolutionPtr->solname, "w")))
  {
    fprintf (stderr, "Error, unable to open solution file \"%s\"\n",
             SolutionPtr->solname);
    return BUG;
  }

  /* Write general information */
  fprintf (SolutionPtr->fsol, "%d sequences, %d missed (%4.2f%%)\n",
           SolutionPtr->nbsols, nbfaults,
           (100.0 * nbfaults) / SolutionPtr->nbsols);

  /* Write numbers of the sequences that generated fault solutions */
  fprintf (SolutionPtr->fsol, "Missed sequences:\n(");

  index = 0;
  firstfault = TRUE;
  ListTemp = SolutionPtr->gridlist;

  while (ListTemp)
  {
    index++;

    /* That grid is a fault? */
    if (! ListTemp->info.solution)
    {
      if (firstfault)
      {
        fprintf (SolutionPtr->fsol, "%d", index);
        firstfault = FALSE;
      }
      else
        fprintf (SolutionPtr->fsol, ", %d", index);
    }

    ListTemp = ListTemp->next;
  }

  fprintf (SolutionPtr->fsol, ")\n\n");

  /* Now, we proceed to the sequence alignment itself. The grids are aligned
     on the helixes that have restrictive patterns only. The first step is to
     determine for each of those helixes, the maximum starting position for
     the restrictive pattern and the maximum space to the right of a
     restrictive pattern in its strand. */

  /* Analyze each SE in the template */
  for (SE = 0; SE < MotifPtr->nbSE; SE++)
  {
    /* Keep a pointer on that SE */
    SEPtr = &(MotifPtr->template[SE]);

    /* This SE is an helix with a restrictive pattern? */
    if ((SEPtr->type == 'H') && (SEPtr->strict))
    {
      /* Initialize maxpos and maxspace */
      maxpos = 0;
      maxspace = 0;

      ListTemp = SolutionPtr->gridlist;

      /* Analyze each grid in the solution */
      while (ListTemp)
      {
        /* Keep a pointer on that strand */
        StrandPtr = &(ListTemp->info.strands[SE]);

        /* That strand is not null and we found the pattern in that grid? */
        if ((! StrandIsNull (*StrandPtr)) && (StrandPtr->pospat != -1))
        {
          /* Have we found a new maxpos? */
          if (StrandPtr->pospat - StrandPtr->first > maxpos)
            maxpos = StrandPtr->pospat - StrandPtr->first;

          /* Have we found a new maxspace? */
          if (StrandPtr->length - (StrandPtr->pospat - StrandPtr->first +
              SEPtr->patlength) > maxspace)
            maxspace = StrandPtr->length - (StrandPtr->pospat -
                       StrandPtr->first +  SEPtr->patlength);
        }

        ListTemp = ListTemp->next;
      }

      /* Must we enlarge that interval? */
      if (maxpos + maxspace + SEPtr->patlength > SEPtr->length.max)
      {
        if (! silent)
          printf ("Structural element %c%d must be enlarged to align "
                  "on primary pattern\n", SEPtr->type, SEPtr->nb);

        /* Enlarge the interval */
        SEPtr->length.max = maxpos + maxspace + SEPtr->patlength;
      }

      /* Now we align the sequences on that helix */
      ListTemp = SolutionPtr->gridlist;

      while (ListTemp)
      {
        /* Keep a pointer on that strand */
        StrandPtr = &(ListTemp->info.strands[SE]);

        /* That strand is not null and we found the pattern in that grid? */
        if ((! StrandIsNull (*StrandPtr)) && (StrandPtr->pospat != -1))
        {
          /* Shift the pattern position */
          StrandPtr->pospat += maxpos -
                               (StrandPtr->pospat - StrandPtr->first);
        }

        ListTemp = ListTemp->next;
      }
    }

    /* If this element is a single strand (with or without a restrictive
       pattern), we try to determine what is the maximum length of the
       corresponding interval. */

    if (SEPtr->type == 'S')
    {
      minlength = 0;
      ListTemp = SolutionPtr->gridlist;

      /* Analyze each grid in the solution to find the maximum length for
         that single strand. */
      while (ListTemp)
      {
        /* Keep a pointer on that strand */
        StrandPtr = &(ListTemp->info.strands[SE]);

        /* That strand is not null? Verify if we have found a new minlength. */
        if ((! StrandIsNull (*StrandPtr)) && (minlength < (StrandPtr->length)))
          minlength = StrandPtr->length;

        ListTemp = ListTemp->next;
      }

      /* Now we align the sequences on that single-strand */
      ListTemp = SolutionPtr->gridlist;

      while (ListTemp)
      {
        /* Keep a pointer on that strand */
        StrandPtr = &(ListTemp->info.strands[SE]);

        if (! StrandIsNull (*StrandPtr))
          StrandPtr->length = minlength;

        ListTemp = ListTemp->next;
      }
    }
  }

  /* Reset the number of sequences already read */
  SequencePtr->nbsequences = 0;

  /* Read sequences back in memory */
  for (index = 0, ListTemp = SolutionPtr->gridlist;
       index < SolutionPtr->nbsols; index++, ListTemp = ListTemp->next)
    switch (ReadSequence (SequencePtr))
    {
      case EOF:
	finished = TRUE;
	break;

      case BUG:

        return BUG;
        break;

      case OK:

        /* Write sequence header */
        fprintf (SolutionPtr->fsol, "> %s\n", SequencePtr->commentary);

        /* Save the grid */
        SaveGrid (SolutionPtr->fsol, &(ListTemp->info), MotifPtr, SequencePtr);

	break;
    }

  /* Free grid list in solution */
  FreeGridList (SolutionPtr);

  return OK;
}

/* ------------------------------ Analyze () ------------------------------ */

/* Function that manages the organization of the motif scan in the sequence.

   20/12/92 - Creation.
   21/01/93 - Bestgrid and bestfault grids are now part of the solution
              structure.
   21/03/93 - Display initial information here. */

int Analyze (typMotif *MotifPtr, typSequence *SequencePtr,
             typSolution *SolutionPtr)
{
  typGrid *GridPtr;

  /* Create grid */
  if (! (GridPtr = CreateGrid (MotifPtr)))
    return BUG;

  /* Create grids */
  if ((! (SolutionPtr->bestgrid = CreateGrid (MotifPtr))) ||
      (! (SolutionPtr->bestfault = CreateGrid (MotifPtr))))
  {
    fprintf (stderr, "Error, unable to create grids for solution\n");
    return BUG;
  }

  /* Initialize number of solutions */
  SolutionPtr->nbsols = 0;
  SolutionPtr->nbalts = 0;

  /* Initialize last position displayed (when silent is FALSE) */
  SequencePtr->lastout = 0;

  /* The values for percentage of work done are not yet entered */
  SequencePtr->scanzoneok = FALSE;

  /* Can we speak? */
  if (! silent)
    DisplayRunData (SequencePtr, SolutionPtr, 0);

  /* Do the pattern matching */
  FindMotif (MotifPtr, SequencePtr, SolutionPtr, GridPtr, 0);

  /* If we can speak, display number of matches */
  if (! silent)
    DisplayRunData (SequencePtr, SolutionPtr, 100);

  /* Update number of matches found */
  SequencePtr->totmatches += SolutionPtr->nbsols + SolutionPtr->nbalts;

  /* Free grids */
  FreeGrid (GridPtr);

  /* Update the total number of nucleotides scanned */
  SequencePtr->totnucleotides += SequencePtr->length;

  /* We found solutions? */
  if (SolutionPtr->nbsols + SolutionPtr->nbalts > 0)
  {
    /* Save best solutions */
    if (! SaveSolutions (MotifPtr, SequencePtr, SolutionPtr))
    {
      /* Free grid list in solution */
      FreeGridList (SolutionPtr);

      return BUG;
    }

    /* Save alternative solutions */
    if (! SaveAlternatives (MotifPtr, SequencePtr, SolutionPtr))
    {
      /* Free grid list in solution */
      FreeGridList (SolutionPtr);

      return BUG;
    }
  }

  /* Free grid list in solution */
  FreeGridList (SolutionPtr);

  /* Free solution grids */
  if (SolutionPtr->bestgrid)
  {
    FreeGrid (SolutionPtr->bestgrid);
    SolutionPtr->bestgrid = NULL;
  }

  if (SolutionPtr->bestfault)
  {
    FreeGrid (SolutionPtr->bestfault);
    SolutionPtr->bestfault = NULL;
  }

  return OK;
}

/* ----------------------------- FindMotif () ----------------------------- */

/* Function that recursively scans the sequence by backtracking in order to
   find the motif.

   22/12/92 - Creation.
   21/01/93 - Major modifications. */

void FindMotif (typMotif *MotifPtr, typSequence *SequencePtr,
		typSolution *SolutionPtr, typGrid *GridPtr, int posSE)
{
  switch (MotifPtr->template[MotifPtr->bestpriority[posSE]].type)
  {
    case 'H':
      /* Scan the intervals and try to find the stem */
      FindOneStem (MotifPtr, SequencePtr, SolutionPtr, GridPtr, posSE);
      break;

    case 'S':
      /* Scan the interval and try to find the SE */
      FindOneSS (MotifPtr, SequencePtr, SolutionPtr, GridPtr, posSE);
      break;

    default:
      fprintf (stderr, "Error, invalid SE type in FindMotif!!\n");
      break;
  }
}

/* ----------------------------- FindOneSS () ----------------------------- */

/* Function that scans an portion of the sequence in order to find a
   particular single-strand.

   03/01/93 - Creation.
   17/01/93 - Update in order to verify intervals consistency.
   30/01/93 - Interval of first SE to scan is put in the sequence structure
              in order to be able to display accurate percentage of work
              done. Also, percentage is now displayed on the same line.
   03/04/93 - s1first and s1last variables renamed as s1min and s1max. */

void FindOneSS (typMotif *MotifPtr, typSequence *SequencePtr,
		typSolution *SolutionPtr, typGrid *GridPtr, int posSE)
{
  long pos;
  float score;
  int ratio;
  typSE *SEPtr;
  typGrid *GridTemp;
  long s1min, s1max;
  int posgrid;

  /* Keep the template index */
  posgrid = MotifPtr->bestpriority[posSE];

  /* Keep the template pointer */
  SEPtr = &(MotifPtr->template[posgrid]);

  /* Pick the interval for the single-strand */
  if (! PickStrand (MotifPtr, SequencePtr, posgrid, GridPtr, &s1min, &s1max))
    return;

  #ifdef DEBUG
  printf ("\nS%d [%d-%d]\n", SEPtr->nb, s1min, s1max);
  #endif

  /* Must we initialize the interval for the percentage of sequence scanned? */
  if ((! SequencePtr->scanzoneok) && (posSE == 0))
  {
    SequencePtr->scanfirst  = s1min;
    SequencePtr->scanlength = s1max - s1min + 1;
    SequencePtr->scanzoneok = TRUE;
  }

  /* Estimation of closeness to the solution */
  score = (MotifPtr->nbbestpriority * 1000.0) / (posSE + 1);

  /* Create a temporary grid */
  GridTemp = CreateGrid (MotifPtr);

  /* Continue backtracking search for all occurances of the desired pattern
     in the interval */
  for (pos = NextPos (s1min, s1max, SEPtr, MotifPtr, SequencePtr, TRUE,
                      posSE);
      (pos != -1);
       pos = NextPos (pos + 1, s1max, SEPtr, MotifPtr, SequencePtr, TRUE,
                      posSE))
  {
    /* If we can speak, display percentage of work done... */
    if ((! silent) && (posSE == 0) &&
       (((pos - SequencePtr->lastout) > (SequencePtr->scanlength / 50))))
    {
      SequencePtr->lastout = pos;
      ratio = (int) ((100.0 * (pos - SequencePtr->scanfirst)) /
                      SequencePtr->scanlength);
      DisplayRunData (SequencePtr, SolutionPtr, ratio);
    }

    /* Backup the grid before continuing backtrack search */
    CopyGrid (GridPtr, GridTemp);

    /* Put strand in grid */
    PutStrand (GridPtr, posgrid, pos, pos + SEPtr->patlength - 1, TRUE);

    /* Adjust intervals */
    UpdateRight (GridPtr, MotifPtr, SequencePtr, posSE);
    UpdateLeft (GridPtr, MotifPtr, posSE);

    /* Have we found a solution? */
    if (posSE == MotifPtr->nbbestpriority - 1)
    {
      #ifdef DEBUG
      printf ("\nA (S%d) complete solution has been found!\n", SEPtr->nb);
      TraceGrid (GridPtr);
      #endif

      /* Add that solution if it has not already been found */
      AddSolution (GridPtr, MotifPtr, SequencePtr, SolutionPtr);
    }
    else
    {
      #ifdef DEBUG
      printf ("\nA (S%d) partial solution has been found!\n", SEPtr->nb);
      TraceGrid (GridPtr);
      #endif

      /* Go for backtracking search... */
      FindMotif (MotifPtr, SequencePtr, SolutionPtr, GridPtr, posSE + 1);
    }

    /* Restore the grid and continue backtrack search */
    CopyGrid (GridTemp, GridPtr);
  }

  /* We have a new best fault? */
  if (score < SolutionPtr->bestfault->score)
  {
    CopyGrid (GridPtr, SolutionPtr->bestfault);
    SolutionPtr->bestfault->score = score;
  }

  /* Destroy temporary grid */
  FreeGrid (GridTemp);
}

/* ---------------------------- FindOneStem () ---------------------------- */

/* Function that scans two portions of the sequence in order to find a
   particular stem combination (helix).

   04/01/93 - Creation.
   21/01/93 - Major modifications.
   30/01/93 - Interval of first SE to scan is put in the sequence structure
              in order to be able to display accurate percentage of work
              done. Also, percentage is now displayed on the same line.
   31/01/93 - Eliminate the use of stem intervals (used to generate bad
              solutions).
   02/02/93 - Value of b2min is now dynamically modified for each value of
              pos2 generated. This corrects a bug that sometimes provoked
              the algorithm to find two stems of an helix having a distance
              inferior to the required minimal. Also, the s2lastmin value
              is eliminated. An incorrect use of intervals caused the
              algorithm to try to match stems that would not even fit their
              minimal lenght in respect to their minimal distance. This
              correction nearly doubles the search speed.
   03/02/93 - Small optimisation gained in duplicating the search code for
              searching helixes with and without restrictive patterns
              separately.
   07/02/93 - Added code to eliminate cases where the first SE we search is
              an helix without restrictive pattern that is found in a portion
              of the sequence that only contains 'N' nucleotides.
   10/02/93 - Now uses the marking algorithm in the sequences to eliminate
              bad positions. When the SE has a restrictive pattern, the
              eimination is assured by the NextPos function, but when it's
              an helix without restrictive pattern, the skipping of bad
              starting positions is made right here.
   11/02/93 - Be sure to filtrate special bits in nucleotides before trying
              to match them.
              Reject invalid positions for the first SE and if the fast
              search switch is activated [-f], also reject invalid positions
              for the second SE to search.
   03/04/93 - s1first and s1last variables renamed as s1min and s1max and
              s2first and s2last variables renamed as s2min and s2max.
   04/04/93 - Big modification of the intervals allocated for helixes
              without restrictive patterns. The old method caused the
              algorithm to look for impossible solutions, which were
              sometimes generated. Now, the interval consistency is
              dynamically adjusted for all starting positions of the first
              strand of an helix. All the new code is enclosed in the new
              INTERVALCHECK global define. Compiling Rnamot with that
              variable's definition commented generates the old version
              of Rnamot (i.e. the one that sometimes generates inconsistant
              solutions).
   29/08/93 - Correction of a bug with the interval algorithm. */

void FindOneStem (typMotif *MotifPtr, typSequence *SequencePtr,
                  typSolution *SolutionPtr, typGrid *GridPtr, int posSE)
{
  long pos1, pos2;
  int ratio;
  int faultcount;
  int wobblecount;
  long length;
  long b1, b2;
  long s1min, s1max;
  long s2min, s2max;
  long lmin, lmax;
  long distmin, distmax;
  int maxfaults;
  float score;
  int stem1, stem2;
  typSE *SEPtr1, *SEPtr2;
  typGrid *GridTemp;
  long b2min, pos2min;
  int ncounter;
  boolean marked;
  short int normalmark, reversemark;

  #ifdef INTERVALCHECK

  long rightindex, leftindex;
  long minlength1, minlength2, minlength;
  long maxlength1, maxlength2, maxlength;
  long minleft, minright, minjeuleft, minjeuright, maxjeuright;
  boolean intercheck = FALSE;

  #endif

  /* Find stem indexes in the template */
  stem1 = MotifPtr->bestpriority[posSE];
  stem2 = MotifPtr->template[stem1].secondstemnb;

  /* Initialize stem pointers in template */
  SEPtr1 = &(MotifPtr->template[stem1]);
  SEPtr2 = &(MotifPtr->template[stem2]);

  /* Pick the interval for the first stem */
  if (! (PickStrand (MotifPtr, SequencePtr, stem1, GridPtr, &s1min, &s1max)))
    return;

  #ifdef DEBUG
  printf ("\nH%d (1) [%d-%d]\n", SEPtr1->nb, s1min, s1max);
  #endif

  /* Must we initialize the interval for the percentage of sequence scanned? */
  if ((! SequencePtr->scanzoneok) && (posSE == 0))
  {
    SequencePtr->scanfirst  = s1min;
    SequencePtr->scanlength = s1max - s1min + 1;
    SequencePtr->scanzoneok = TRUE;
  }

  /* Pick the interval for the second stem */
  if (! (PickSecondStem (MotifPtr, SequencePtr, stem2, GridPtr,
         &s2min, &s2max)))
    return;

  #ifdef DEBUG
  printf ("\nH%d (2) [%d-%d]\n", SEPtr2->nb, s2min, s2max);
  #endif

  /* Estimation of closeness to the solution */
  score = (MotifPtr->nbbestpriority * 1000.0) / (posSE + 1);

  /* Create a temporary grids */
  GridTemp = CreateGrid (MotifPtr);

  /* Keep min and max length and maxfaults of the helix */
  lmin = SEPtr1->length.min;
  lmax = SEPtr1->length.max;
  maxfaults = SEPtr1->maxfaults;

  /* Keep minimal and maximal distances */
  distmin = MotifPtr->disttab[stem1 * MotifPtr->nbSE + stem2].min;
  distmax = MotifPtr->disttab[stem1 * MotifPtr->nbSE + stem2].max;

  /* If that element is not strict (no restrictive pattern) then initialize
     mark variables */
  if (! SEPtr1->strict)
  {
    /* Must we check this SE as marked? */
    if (fastsearch && (posSE < MotifPtr->maxmark))
    {
      marked = TRUE;
      normalmark = rejectn [posSE];
      reversemark = rejectr [posSE];
    }
    else
      marked = FALSE;
  }

  #ifdef INTERVALCHECK

  /* Initialize maxlengths */
  maxlength1 = maxlength2 = MotifPtr->template[stem1].length.max;

  /* Find right neighbour of first stem */
  rightindex = GridPtr->strands[stem1].right;

  /* Initialize the check variable */
  intercheck = (rightindex != -1) && (rightindex < stem2);

  /* There is a structural element in the grid between the two stems? */
  if (intercheck)
  {
    /* Find left neighbour of second stem */
    leftindex = GridPtr->strands[stem2].left;

    /* Calculate minimal starting position of right neighbour of first stem */
    minleft = GridPtr->strands[rightindex].first -
              MotifPtr->disttab[stem1 * MotifPtr->nbSE + rightindex].min;

    /* Calculate minimal starting position (minus adjustment) */
    if (MotifPtr->template[rightindex].type == 'S')
      minjeuleft = minleft -
                  (MotifPtr->template[rightindex].length.max -
                   GridPtr->strands[rightindex].length);
    else
      minjeuleft = minleft;

    /* Verify if minjeuleft is still in first stem's interval */
    if (minjeuleft < s1min)
      minjeuleft = s1min;

    /* Calculate maximal ending position of left neighbour of second stem */
    minright = GridPtr->strands[leftindex].last +
               MotifPtr->disttab[leftindex * MotifPtr->nbSE + stem2].min;

    /* Calculate maximal starting position (plus minimal adjustment) */
    if (MotifPtr->template[leftindex].type == 'S')
      minjeuright = minright +
                   (MotifPtr->template[leftindex].length.max -
                    GridPtr->strands[leftindex].length);
    else
      minjeuright = minright;

    /* Verify if minjeuright is not greater than s2max */
    if (minjeuright > s2max)
      minjeuright = s2max;

    /* Calculate maximal starting position (plus maximal adjustment) */
    if (MotifPtr->template[leftindex].type == 'S')
      maxjeuright = GridPtr->strands[leftindex].last +
                    MotifPtr->disttab[leftindex * MotifPtr->nbSE + stem2].max +
                   (MotifPtr->template[leftindex].length.max -
                    GridPtr->strands[leftindex].length);
    else
      maxjeuright = GridPtr->strands[leftindex].last +
                    MotifPtr->disttab[leftindex * MotifPtr->nbSE + stem2].max;

    /* Verify if minjeuright is not greater than s2max */
    if (maxjeuright > s2max)
      maxjeuright = s2max;

    /* Calculate maximum length of first stem */
    maxlength1 = minleft - s1min;

    if (maxlength1 > lmax)
      maxlength1 = lmax;

    /* Calculate maximum length of second stem */
    maxlength2 = s2max - minright;

    if (maxlength2 > lmax)
      maxlength2 = lmax;

    /* Calculate initial maximum length possible */
    maxlength = min (maxlength1, maxlength2);

    /* Adjust stem intervals */
    if (maxlength1 > maxlength)
      if ((MotifPtr->disttab[stem1 * MotifPtr->nbSE + rightindex].max -
           MotifPtr->disttab[stem1 * MotifPtr->nbSE + rightindex].min) >
           (maxlength1 - maxlength))
        s1min += maxlength1 - maxlength;

    if (maxlength2 > maxlength)
      s2max -= maxlength2 - maxlength;
  }
  #endif

  /* Here we'll duplicate some code but since it's the most time consuming
     part of the program it optimizes a few cycles that are very appreciated.
     So, if the helix does not have a restrictive pattern, there's no need to
     use the NextPos and PrevPos functions. */

  /* This helix does have a restrictive pattern? */
  if (SEPtr1->strict)
  {
    /* Continue backtracking search for all occurances of the desired helix
       in the interval */
    for (pos1 = NextPos (s1min, s1max, SEPtr1, MotifPtr, SequencePtr, TRUE,
                         posSE);
        (pos1 != -1) && (pos1 <= s1max);
         pos1 = NextPos (pos1 + 1, s1max, SEPtr1, MotifPtr, SequencePtr, TRUE,
                         posSE))
    {
      /* If we can speak, display percentage of work done... */
      if ((! silent) && (posSE == 0) &&
         (((pos1 - SequencePtr->lastout) > (SequencePtr->scanlength / 50))))
      {
        SequencePtr->lastout = pos1;
        ratio = (int) ((100.0 * (pos1 - SequencePtr->scanfirst)) /
                        SequencePtr->scanlength);
        DisplayRunData (SequencePtr, SolutionPtr, ratio);
      }

      /* Calculate first valid starting position for second stem */
      pos2 = min (s2max, pos1 + 2 * SEPtr1->length.max + distmax - 1);

      /* Calculate last valid starting position for second stem */
      pos2min = max (s2min, pos1 + 2 * lmin + distmin - 1);

      /* Continue backtracking search for all occurances of the second stem
         in the interval */
      for (pos2 = PrevPos (pos2, pos2min, SEPtr2, MotifPtr, SequencePtr,
                           posSE);
          (pos2 != -1) && (pos2 >= pos2min);
           pos2 = PrevPos (pos2 - 1, pos2min, SEPtr2, MotifPtr, SequencePtr,
                           posSE))
      {
        /* Calculate minimal valid position */
        b2min = pos2 - ((pos2 - pos1 + 1) - distmin) / 2 + 1;

        /* Initialize length */
        length = 1;

        /* Initialize strands index */
        b1 = pos1;
        b2 = pos2;

        /* Initialize ncounter */
        ncounter = 0;

        /* Initialize fault and wobble counters */
        faultcount = 0;
        wobblecount = 0;

        while ((length <= lmax) && (b2 >= b2min))
        {
          /* Update ncounter */
          if ((SequencePtr->sequence[b1] & NUCMASK) == BASE_N) ncounter++;
          if ((SequencePtr->sequence[b2] & NUCMASK) == BASE_N) ncounter++;

          /* Update fault counter */
          if (BaseToPair [SequencePtr->sequence[b1] & NUCMASK]
                         [SequencePtr->sequence[b2] & NUCMASK] >= 6)
            faultcount++;

          /* Have we reached the maximum number of faults for that helix? */
          if (faultcount > maxfaults)
            break;

          /* Do we have reached a maximum number of mismatchs? */
          if (faultcount + GridPtr->mismatchs > MotifPtr->maxmismatchs)
            break;

          /* Update wobble counter */
          if (((SequencePtr->sequence[b1] & NUCMASK) == BASE_U &&
               (SequencePtr->sequence[b2] & NUCMASK) == BASE_G) ||
              ((SequencePtr->sequence[b1] & NUCMASK) == BASE_G &&
               (SequencePtr->sequence[b2] & NUCMASK) == BASE_U))
            wobblecount++;

          /* Do we have reached a maximum number of wobbles? */
          if (wobblecount + GridPtr->wobbles > MotifPtr->maxwobbles)
            break;

          /* It's a solution if the length of the helix is greater of equal to
             the required minimal length and the distance between the two stems
             does respect the minimal and maximal length allowed */

          if ((length >= lmin) &&
              ((b2 - b1 - 1) <= distmax) &&
              ((! fastsearch) ||
               (fastsearch && ((posSE >= MotifPtr->maxmark) ||
                              ((posSE < MotifPtr->maxmark) &&
                               (ncounter < 2 * length))))))
          {
            /* Backup the grid before continuing backtrack search */
            CopyGrid (GridPtr, GridTemp);

            /* Put strands in grid */
            PutStrand (GridPtr, stem1, pos1, b1, TRUE);
            PutStrand (GridPtr, stem2, b2, pos2, TRUE);

            /* Adjust intervals */
            UpdateRight (GridPtr, MotifPtr, SequencePtr, posSE);
            UpdateLeft (GridPtr, MotifPtr, posSE);

            /* Update the mismatch count of the grid */
            GridPtr->mismatchs += faultcount;

            /* Update the wobble count of the grid */
            GridPtr->wobbles += wobblecount;

            /* Have we found a solution? */
            if (posSE == MotifPtr->nbbestpriority - 1)
            {
              #ifdef DEBUG
              printf ("\nA (H%d) complete solution has been found!\n", SEPtr1->nb);
              TraceGrid (GridPtr);
              #endif

              /* Add that solution if it has not already been found */
              AddSolution (GridPtr, MotifPtr, SequencePtr, SolutionPtr);
            }
            else
            {
              #ifdef DEBUG
              printf ("\nA (H%d) partial solution has been found!\n", SEPtr1->nb);
              TraceGrid (GridPtr);
              #endif

              /* Go for backtracking search... */
              FindMotif (MotifPtr, SequencePtr, SolutionPtr, GridPtr, posSE + 1);
            }

            /* Restore the grid and continue backtrack search */
            CopyGrid (GridTemp, GridPtr);
          }

          /* Adjust pointers */
          b1++;
          b2--;

          /* Increment length */
          length++;
        }
      }
    }
  }
  else
  {
    /* This helix does not have a restrictive pattern, so we go for the
       exhaustive search. */
    for (pos1 = s1min; pos1 <= s1max; pos1++)
    {
      /* We are in fastsearch mode and this SE is in the mark list? */
      if (marked)
        if ((SequencePtr->sequence[pos1] & normalmark) == normalmark)
          continue;

      /* If we can speak, display percentage of work done... */
      if ((! silent) && (posSE == 0) &&
         (((pos1 - SequencePtr->lastout) > (SequencePtr->scanlength / 50))))
      {
        SequencePtr->lastout = pos1;
        ratio = (int) ((100.0 * (pos1 - SequencePtr->scanfirst)) /
                        SequencePtr->scanlength);
        DisplayRunData (SequencePtr, SolutionPtr, ratio);
      }

      #ifdef INTERVALCHECK

      maxlength = lmax;
      minlength1 = lmin;

      /* Must we check the intervals? */
      if (intercheck)
      {
        /* Calculate maximum length of first stem */
        maxlength = minleft - pos1;

        if (maxlength > lmax)
          maxlength = lmax;

        /* Calculate minimum length of first stem */

/* VERSION 2.0 */
/*
        minlength1 = minjeuleft - pos1;
*/

/* VERSION 2.1 */

        minlength1 = minjeuleft - pos1 -
                    (MotifPtr->disttab[stem1 * MotifPtr->nbSE + rightindex].max -
                     MotifPtr->disttab[stem1 * MotifPtr->nbSE + rightindex].min);


        /* Verify that minimal length of left stem is not lower than
           possible minimum. */
        if (minlength1 < lmin)
          minlength1 = lmin;

        /* Verify that minimal length of left stem is not greater than
           possible maximum. */
        if (minlength1 > maxlength)
          minlength1 = maxlength;

        /* Calculate minimal valid starting position for second stem */
        pos2min = minright + minlength1;

        /* Calculate valid starting position for second stem */

/* VERSION 2.0 */
/*
        pos2 = pos1 + 2 * maxlength + distmax - 1;
*/

/* VERSION 2.01 */

        pos2 = maxjeuright + maxlength;


        /* If we had a too big maximal distance possible between the two
           stems and pos2 is a value greater than s2max which is the
           maximal valid starting position allocated for that stem, then
           we just start at that position. */
        if (pos2 > s2max)
        {

          pos2 = s2max;

          /* Is it possible to fit a second stem of maximal length equal
             to first stem's maximal length at that position? If not,
             adjust starting position for stem2. */
          if (pos2 - maxlength > maxjeuright)
            pos2 -= pos2 - maxlength - maxjeuright;
        }
      }
      else
      {
        /* Case when no elements have been found between the two stems. */
        pos2min = max (s2min, pos1 + 2 * lmin + distmin - 1);
        pos2 = min (s2max, pos1 + 2 * maxlength + distmax - 1);
      }

      #else

      /* Calculate last valid starting position for second stem */
      pos2min = max (s2min, pos1 + 2 * lmin + distmin - 1);

      /* Calculate first valid starting position for second stem */
      pos2 = min (s2max, pos1 + 2 * SEPtr1->length.max + distmax - 1);

      #endif

      #ifdef DEBUG
      printf ("H%d pos1: %d, pos2: %d, pos2min: %d\n",
               SEPtr1->nb, pos1, pos2, pos2min);
      #endif

      /* Continue backtracking search for all occurances of the second stem
         in the interval */
      for (; pos2 >= pos2min; pos2--)
      {
        /* We are in fastsearch mode and this SE is in the mark list? */
        if (marked)
          if ((SequencePtr->sequence[pos2] & reversemark) == reversemark)
            continue;

        #ifdef INTERVALCHECK

        /* Initialise minimum length for second stem */
        minlength = minlength1;

        /* Calculate minimal valid position */
        if (intercheck)
        {
          /* Calculate minimal length of second stem */
          minlength2 = pos2 - minjeuright;

          if (minlength2 < minlength1)
            minlength2 = minlength1;

          if (minlength2 > maxlength)
            minlength2 = maxlength;

          /* Calculate minlength */
          minlength = max (minlength1, minlength2);

          /* Verify if the maximum length must be reduced */
          if (pos2 - minright < maxlength)
            maxlength = pos2 - minright;

          b2min = pos2 - maxlength + 1;
        }
        else
          b2min = pos2 - ((pos2 - pos1 + 1) - distmin) / 2 + 1;

        #else

        /* Calculate minimal valid position */
        b2min = pos2 - ((pos2 - pos1 + 1) - distmin) / 2 + 1;

        #endif

        #ifdef DEBUG
        printf ("\nH%d pos1: %d, pos2: %d, b2min: %d, minlength: %d, maxlength: %d\n",
                 SEPtr1->nb, pos1, pos2, b2min, minlength, maxlength);
        #endif

        /* Initialize length */
        length = 1;

        /* Initialize strands index */
        b1 = pos1;
        b2 = pos2;

        /* Initialize ncounter */
        ncounter = 0;

        /* Initialize fault and wobble counters */
        faultcount = 0;
        wobblecount = 0;

        #ifdef INTERVALCHECK

        while ((length <= maxlength) && (b2 >= b2min))

        #else

        while ((length <= lmax) && (b2 >= b2min))

        #endif

        {
          /* Update ncounter */
          if ((SequencePtr->sequence[b1] & NUCMASK) == BASE_N) ncounter++;
          if ((SequencePtr->sequence[b2] & NUCMASK) == BASE_N) ncounter++;

          /* Update fault counter */
          if (BaseToPair [SequencePtr->sequence[b1] & NUCMASK]
                         [SequencePtr->sequence[b2] & NUCMASK] >= 6)
            faultcount++;

          /* Have we reached the maximum number of faults for that helix? */
          if (faultcount > maxfaults)
            break;

          /* Do we have reached a maximum number of mismatchs? */
          if (faultcount + GridPtr->mismatchs > MotifPtr->maxmismatchs)
            break;

          /* Update wobble counter */
          if (((SequencePtr->sequence[b1] & NUCMASK) == BASE_U &&
               (SequencePtr->sequence[b2] & NUCMASK) == BASE_G) ||
              ((SequencePtr->sequence[b1] & NUCMASK) == BASE_G &&
               (SequencePtr->sequence[b2] & NUCMASK) == BASE_U))
            wobblecount++;

          /* Do we have reached a maximum number of wobbles? */
          if (wobblecount + GridPtr->wobbles > MotifPtr->maxwobbles)
            break;

          /* It's a solution if the length of the helix is greater or equal to
             the required minimal length and the distance between the two stems
             does respect the minimal and maximal length allowed */

          #ifdef INTERVALCHECK

          if ((length >= minlength) &&
              ((b2 - b1 - 1) <= distmax) &&
              ((! fastsearch) ||
               (fastsearch &&  ((posSE >= MotifPtr->maxmark) ||
                              ((posSE < MotifPtr->maxmark) &&
                               (ncounter < 2 * length))))))
          #else

          if ((length >= lmin) &&
              ((b2 - b1 - 1) <= distmax) &&
              ((! fastsearch) ||
               (fastsearch &&  ((posSE >= MotifPtr->maxmark) ||
                              ((posSE < MotifPtr->maxmark) &&
                               (ncounter < 2 * length))))))
          #endif

          {
            /* Backup the grid before continuing backtrack search */
            CopyGrid (GridPtr, GridTemp);

            /* Put strands in grid */
            PutStrand (GridPtr, stem1, pos1, b1, TRUE);
            PutStrand (GridPtr, stem2, b2, pos2, TRUE);

            /* Adjust intervals */
            UpdateRight (GridPtr, MotifPtr, SequencePtr, posSE);
            UpdateLeft (GridPtr, MotifPtr, posSE);

            /* Update the mismatch count of the grid */
            GridPtr->mismatchs += faultcount;

            /* Update the wobble count of the grid */
            GridPtr->wobbles += wobblecount;

            /* Have we found a solution? */
            if (posSE == MotifPtr->nbbestpriority - 1)
            {
              #ifdef DEBUG
              printf ("\nA (H%d) complete solution has been found!\n", SEPtr1->nb);
              TraceGrid (GridPtr);
              #endif

              /* Add that solution if it has not already been found */
              AddSolution (GridPtr, MotifPtr, SequencePtr, SolutionPtr);
            }
            else
            {
              #ifdef DEBUG
              printf ("\nA (H%d) partial solution has been found!\n", SEPtr1->nb);
              TraceGrid (GridPtr);
              #endif

              /* Go for backtracking search... */
              FindMotif (MotifPtr, SequencePtr, SolutionPtr, GridPtr, posSE + 1);
            }

            /* Restore the grid and continue backtrack search */
            CopyGrid (GridTemp, GridPtr);
          }

          /* Adjust pointers */
          b1++;
          b2--;

          /* Increment length */
          length++;
        }
      }
    }
  }

  /* We have a new best fault? */
  if (score < SolutionPtr->bestfault->score)
  {
    CopyGrid (GridPtr, SolutionPtr->bestfault);
    SolutionPtr->bestfault->score = score;
  }

  /* Destroy temporary grid */
  FreeGrid (GridTemp);
}

/* ------------------------------ NextPos () ------------------------------ */

/* Function that scans the sequence in ascending order to find a pattern,
   starting in the interval [PosFirst, PosLast].

   22/12/92 - Creation.
   13/01/93 - Correct use of interval coordinates.
   19/01/93 - Verification for the presence of a restrictive pattern.
   21/01/93 - Strictcheck parameter added, allows the function to be used
              even when a SE has a non-strict restrictive pattern and we
              want to find if it is present in a particular interval (for
              the grid score evaluation).
   06/02/93 - Added posSE parameter in order to eliminate intervals that
              contain only 'N' nucleotides when we are searching the
              pattern for the first SE in the priority array.
   10/02/93 - Eliminate the posSE parameter since the sequence is already
              marked for bad starting positions.
   11/02/93 - Be sure to filtrate special bits in nucleotides before trying
              to match them. Use posSE paramter to know when we must
              filtrate bad positions.
              If the fast search switch is activated [-f], filtrate invalid
              positions for the second element of the priority array.
   15/02/93 - Added the MotifPtr parameter and now uses a different method
              for filtering marked positions. */

long NextPos (long PosFirst, long PosLast, typSE *SEPtr, typMotif *MotifPtr,
              typSequence *SequencePtr, int strictcheck, int posSE)
{
  int patlength = SEPtr->patlength;
  register long i, j;
  register short int *seq = SequencePtr->sequence;
  register char *pat = SEPtr->pattern;
  boolean marked;
  short int normalmark;

  /* If that SE has no restrictive pattern, we can begin at PosFirst */
  if (strictcheck)
  {
    if (! SEPtr->strict)
      return PosFirst;
  }
  else
  {
    /* This SE has no pattern? */
    if (SEPtr->patlength == 0)
      return -1;
  }

  /* Must we check this SE as marked? */
  if (fastsearch && (posSE < MotifPtr->maxmark))
  {
    marked = TRUE;
    normalmark = rejectn [posSE];
  }
  else
    marked = FALSE;

  /* Search the pattern for all valid starting positions */
  for (i = PosFirst; i <= PosLast; i++)
  {
    /* We are in fastsearch mode and this SE is in the mark list? */
    if (marked)
      if ((seq[i] & normalmark) == normalmark)
        continue;

    /* Is there a match there? */
    for (j = 0; j < patlength; j++)
      if (! ((seq [i + j] & NUCMASK) & (pat [j] & NUCMASK)))
         break;

    /* Do we have a match? */
    if (j == patlength)
      return i;
  }

  /* Pattern not found in the interval */
  return -1;
}

/* --------------------------- PickSecondStem () -------------------------- */

/* Function that returns the proper interval for a second stem. It is
   important to know that the pos1first and pos1last values returned for
   the interval correspond to the reversed valid starting positions in the
   sequence.

   27/01/93 - Creation.
   28/01/93 - Correction of the first value returned.
   31/01/93 - Don't use helix adjustment (maximal - minimal length).
              Used to generate bad solutions.
   30/03/93 - Correction of many bugs that caused invalid intervals to be
              generated for the second stem of an helix. They are:

              - When the grid is empty, the pos1first value calculated did
                not take the minimal helix length into account so the
                interval was too large (left value too small)

              - When the grid is empty, the pos1last value calculated did
                not take the last element's minimal length into account so
                the interval was too large (right value too big)

              - When there was already an element to the left in the grid,
                the calculated firsta value was too high because we used
                the helix's maximal length instead of its minimal length
                and leaded the algorithm to skip small helixes

              - When there was already an element to the left in the grid,
                the calculated lasta value was too high because it did not
                take the minimal distance between the current stem and the
                last one in the grid into account and caused the generated
                interval to be too large.

   03/04/93 - Correction of a bug for the value of the maxpos variable used
              for the (posleft != -1) case. It was one position too high. */

int PickSecondStem (typMotif *MotifPtr, typSequence *SequencePtr, int posgrid,
                    typGrid *GridPtr, long *pos1first, long *pos1last)
{
  int posleft, posright;
  long firsta, firstb, lasta, lastb;
  typSE *SEPtr, *SEPtr1, *SEPtr2;
  long maxpos;

  /* Keep pointer on current element in template */
  SEPtr = &(MotifPtr->template[posgrid]);

  /* Find left and right neighbours */
  posleft  = GridPtr->strands[posgrid].left;
  posright = GridPtr->strands[posgrid].right;

  /* We have already found a SE to the left? */
  if (posleft != -1)
  {
    /* Keep pointer on SE */
    SEPtr1 = &(MotifPtr->template[posleft]);

    /* Find first valid position */
    firsta = GridPtr->strands[posleft].last +
             MotifPtr->disttab[posleft * MotifPtr->nbSE + posgrid].min +
             SEPtr->length.min;

    /* If the starting position is AFTER the end of the sequence, then it's
       not good at all. */
    if (firsta > SequencePtr->length - 1)
      return FALSE;

    /* Find last valid position */
    lasta = GridPtr->strands[posleft].last +
            MotifPtr->disttab[posleft * MotifPtr->nbSE + posgrid].max +
            SEPtr->length.max;

    /* Interval adjustment */
    if (SEPtr1->type == 'S')
      lasta += SEPtr1->length.max - GridPtr->strands[posleft].length;

    /* Is this position valid? */
    if (lasta > SequencePtr->length - 1)
      lasta = SequencePtr->length - 1;

    /* Don't scan in the last SE zone!! */
    if (posgrid < MotifPtr->nbSE - 1)
    {
      /* Calculate maximum valid position */
      maxpos = SequencePtr->length - 1 -
               MotifPtr->template[MotifPtr->nbSE - 1].length.min -
               MotifPtr->disttab[posgrid * MotifPtr->nbSE + MotifPtr->nbSE - 1].min;

      /* Is last position valid? */
      if (lasta > maxpos)
        lasta = maxpos;
    }
  }

  /* We have already found a SE to the right? */
  if (posright != -1)
  {
    /* Keep pointer on SE */
    SEPtr2 = &(MotifPtr->template[posright]);

    /* Find first valid position */
    firstb = GridPtr->strands[posright].first -
             MotifPtr->disttab[posgrid * MotifPtr->nbSE + posright].max - 1;

    /* Interval adjustment */
    if (SEPtr2->type == 'S')
      firstb -= SEPtr2->length.max - GridPtr->strands[posright].length;

    /* Is this position valid? */
    if (firstb < 0) firstb = 0;

    /* Don't scan in the first SE zone!! */
    if (firstb < MotifPtr->template[0].length.min +
                 MotifPtr->disttab [posgrid].min)
      firstb = MotifPtr->template[0].length.min +
               MotifPtr->disttab [posgrid].min;

    /* Calculate last valid position */
    lastb = GridPtr->strands[posright].first -
            MotifPtr->disttab[posgrid * MotifPtr->nbSE + posright].min - 1;

    /* If the ending position is BEFORE the beginning of the sequence, then
       it's not good at all. */
    if (lastb < 0)
      return FALSE;
  }

  /* We have found a SE to the left? */
  if (posleft != -1)
  {
    if (posright != -1)
    {
      /* We have two intervals, we choose the intersection */
      *pos1first = max (firsta, firstb);
      *pos1last = min (lasta, lastb);

      /* Return */
      return (*pos1last < *pos1first) ? FALSE : OK;
    }
    else
    {
      *pos1first = firsta;
      *pos1last = lasta;

      /* Return */
      return (*pos1last < *pos1first) ? FALSE : OK;
    }
  }

  /* No SE to the left, we have one to the right? */
  if (posright != -1)
  {
    *pos1first = firstb;
    *pos1last = lastb;

    /* Return */
    return (*pos1last < *pos1first) ? FALSE : OK;
  }

  /* There's no SE in the grid */
  *pos1first = MotifPtr->disttab[posgrid].min +
               MotifPtr->template[0].length.min +
               SEPtr->length.min - 1;

  /* If this SE is the last one in the grid, then its last valid starting
     position corresponds to the total length of the sequence, minus the
     pattern length if it has one, or minus the minimal length if there's
     no restrictive pattern */
  if (posgrid == MotifPtr->nbSE - 1)
    *pos1last = (long) SequencePtr->length - 1;
  else
    *pos1last = (long) SequencePtr->length - 1 -
      MotifPtr->disttab[posgrid * MotifPtr->nbSE + MotifPtr->nbSE - 1].min -
      MotifPtr->template[MotifPtr->nbSE - 1].length.min;

  /* We have a valid interval? */
  if (*pos1last < *pos1first)
    return FALSE;

  /* The interval is valid */
  return OK;
}

/* ---------------------------- PickStrand () ----------------------------- */

/* Function that returns the interval in which a particular single-strand
   structural element can be found in the sequence. The returned interval
   [pos1first, pos1last] corresponds to all the valid starting positions to
   search for the restrictive pattern of the single-strand in the sequence.

   22/12/92 - Creation.
   29/12/92 - Completion.
   07/01/93 - Adjustment of returned intervals.
   17/01/93 - The interval adjustment is made in consideration of the
              space already allocated to other elements in the grid, thus
              ensuring interval allocation integrity.
              Add a return value, so we don't scan invalid intervals
              (when there's an element to the left and the starting
              position is after the end of the sequence or when we have an
              element to the right and the ending position is before the
              beginning of the sequence).
   19/01/93 - Added code for helix treatment.
   25/01/93 - Special cases correction.
   31/01/93 - Don't use helix adjustment (maximal - minimal length).
              Used to generate bad solutions. */

int PickStrand (typMotif *MotifPtr, typSequence *SequencePtr, int posgrid,
                typGrid *GridPtr, long *pos1first, long *pos1last)
{
  int posleft, posright;
  long firsta, firstb, lasta, lastb;
  typSE *SEPtr, *SEPtr1, *SEPtr2;

  /* Keep pointer on that SE in the template */
  SEPtr = &(MotifPtr->template[posgrid]);

  /* Find left and right neighbours */
  posleft  = GridPtr->strands[posgrid].left;
  posright = GridPtr->strands[posgrid].right;

  /* We have already found a SE to the left? */
  if (posleft != -1)
  {
    /* Keep pointer on SE */
    SEPtr1 = &(MotifPtr->template[posleft]);

    /* Find first valid position */
    firsta = GridPtr->strands[posleft].last +
             MotifPtr->disttab[posleft * MotifPtr->nbSE + posgrid].min + 1;

    /* If the starting position is AFTER the end of the sequence, then it's
       not good at all. */
    if (firsta > SequencePtr->length - 1)
      return FALSE;

    /* This element has a restrictive pattern? If so, it's either a single
       strand or a stem with a pattern */

    /* If the element is a single strand, then we can use its adjustment */
    if (SEPtr->type == 'S')
    {
      if (SEPtr->strict)
        lasta = GridPtr->strands[posleft].last +
                MotifPtr->disttab[posleft * MotifPtr->nbSE + posgrid].max + 1 +
                SEPtr->length.max - SEPtr->patlength;
      else
        lasta = GridPtr->strands[posleft].last +
                MotifPtr->disttab[posleft * MotifPtr->nbSE + posgrid].max + 1 +
                SEPtr->length.max - SEPtr->length.min;
    }
    else
      lasta = GridPtr->strands[posleft].last +
              MotifPtr->disttab[posleft * MotifPtr->nbSE + posgrid].max + 1;

    /* Interval adjustment */
    if (SEPtr1->type == 'S')
      lasta += SEPtr1->length.max - GridPtr->strands[posleft].length;

    /* Is this position valid? */
    if (lasta > SequencePtr->length - 1)
      lasta = SequencePtr->length - 1;

    /* Don't scan in the last SE zone!! */
    if (posgrid < MotifPtr->nbSE - 1)
    {
      if (SEPtr->strict)
      {
        if (lasta > SequencePtr->length -
                    MotifPtr->template[MotifPtr->nbSE - 1].length.min -
                    SEPtr->patlength)
          lasta = SequencePtr->length -
                  MotifPtr->template[MotifPtr->nbSE - 1].length.min - 
                  SEPtr->patlength;
      }
      else
      {
        if (lasta > SequencePtr->length -
                    MotifPtr->template[MotifPtr->nbSE - 1].length.min -
                    SEPtr->length.min)
          lasta = SequencePtr->length -
                  MotifPtr->template[MotifPtr->nbSE - 1].length.min -
                  SEPtr->length.min;
      }
    }
    else
    {
      /* I'm the last SE in the grid. Make sure the last starting value is
         correct in regard to the restrictive pattern's length */
      if (SEPtr->strict)
      {
        if (lasta > SequencePtr->length - SEPtr->patlength)
          lasta = SequencePtr->length - SEPtr->patlength;
      }
      else
      {
        if (lasta > SequencePtr->length - SEPtr->length.min)
          lasta = SequencePtr->length - SEPtr->length.min;
      }
    }
  }

  /* We have already found a SE to the right? */
  if (posright != -1)
  {
    /* Keep pointer on SE */
    SEPtr2 = &(MotifPtr->template[posright]);

    /* Find first valid position */
    firstb = GridPtr->strands[posright].first -
             MotifPtr->disttab[posgrid * MotifPtr->nbSE + posright].max -
             SEPtr->length.max;

    /* Interval adjustment */
    if (SEPtr2->type == 'S')
      firstb -= SEPtr2->length.max - GridPtr->strands[posright].length;

    /* Is this position valid? */
    if (firstb < 0) firstb = 0;

    /* Don't scan in the first SE zone!! */
    if ((posgrid > 0) && (firstb < MotifPtr->template[0].length.min +
                                   MotifPtr->disttab [posgrid].min))
      firstb = MotifPtr->template[0].length.min +
               MotifPtr->disttab [posgrid].min;

    /* This element has a restrictive pattern? If so, it's either a single
       strand or a stem with a pattern */

    /* If the element is a single-strand, then we can use its adjustment */
    if (SEPtr->type == 'S')
    {
      if (SEPtr->strict)
        lastb = GridPtr->strands[posright].first -
                MotifPtr->disttab[posgrid * MotifPtr->nbSE + posright].min -
                SEPtr->patlength;
      else
        /* It's a stem with no pattern, so we correct the last starting
           position by substracting the stem's minimum length instead of the
           pattern length */
        lastb = GridPtr->strands[posright].first -
                MotifPtr->disttab[posgrid * MotifPtr->nbSE + posright].min -
                SEPtr->length.min;
    }
    else
      lastb = GridPtr->strands[posright].first -
              MotifPtr->disttab[posgrid * MotifPtr->nbSE + posright].min -
              SEPtr->length.min;

    /* If the ending position is BEFORE the beginning of the sequence, then
       it's not good at all. */
    if (lastb < 0)
      return FALSE;
  }

  /* We have found a SE to the left? */
  if (posleft != -1)
  {
    if (posright != -1)
    {
      /* We have two intervals, we choose the intersection */
      *pos1first = max (firsta, firstb);
      *pos1last = min (lasta, lastb);

      /* Return */
      return (*pos1last < *pos1first) ? FALSE : OK;
    }
    else
    {
      *pos1first = firsta;
      *pos1last = lasta;

      /* Return */
      return (*pos1last < *pos1first) ? FALSE : OK;
    }
  }

  /* No SE to the left, we have one to the right? */
  if (posright != -1)
  {
    *pos1first = firstb;
    *pos1last = lastb;

    /* Return */
    return (*pos1last < *pos1first) ? FALSE : OK;
  }

  /* We are scanning the first SE. Is it the first in the template? */
  if (posgrid == 0)
    *pos1first = 0;
  else
    *pos1first = MotifPtr->disttab[posgrid].min +
                 MotifPtr->template[0].length.min;

  /* If this SE is the last one in the grid, then its last valid starting
     position corresponds to the total length of the sequence, minus the
     pattern length if it has one, or minus the minimal length if there's
     no restrictive pattern */
  if (posgrid == MotifPtr->nbSE - 1)
  {
    /* The element is a single-strand for sure (an helix can't be the last
       in the grid here because the second stem of an helix is treated in
       the PickSecondStem function). We verify if we can use an adjustment
       for that strand. */

    if (SEPtr->strict)
      *pos1last = (long) SequencePtr->length - SEPtr->patlength;
    else
      *pos1last = (long) SequencePtr->length - SEPtr->length.min;
  }
  else
  {
    /* If the element is a single-strand, then we can use its adjustment */
    if (SEPtr->type == 'S')
    {
      /* This SE is not the last one in the grid. So its last valid starting
         position is the total length of the sequence, minus the minimal
         distance between it and the last SE in the grid, minus the minimal
         length of the last SE in the grid, minus the pattern length if it has
         one, or minus the minimal length if there's no restrictive pattern. */
      if (SEPtr->strict)
        *pos1last = (long) SequencePtr->length -
        MotifPtr->disttab[posgrid * MotifPtr->nbSE + MotifPtr->nbSE - 1].min -
        MotifPtr->template[MotifPtr->nbSE - 1].length.min - SEPtr->patlength;
      else
        *pos1last = (long) SequencePtr->length -
        MotifPtr->disttab[posgrid * MotifPtr->nbSE + MotifPtr->nbSE - 1].min -
        MotifPtr->template[MotifPtr->nbSE - 1].length.min - SEPtr->length.min;
    }
    else
      *pos1last = (long) SequencePtr->length -
      MotifPtr->disttab[posgrid * MotifPtr->nbSE + MotifPtr->nbSE - 1].min -
      MotifPtr->template[MotifPtr->nbSE - 1].length.min - SEPtr->length.min;
  }

  /* We have a valid interval? */
  if (*pos1last < *pos1first)
    return FALSE;

  /* The interval is valid */
  return OK;
}

/* ------------------------------ PrevPos () ------------------------------ */

/* Function that scans the sequence in reverse order to find a pattern,
   starting at position PosStart.

   06/01/93 - Creation.
   19/01/93 - Major reconstruction.
   03/02/93 - No need to verify if the element contains a restrictive
              pattern, it has already been filtered out in the FindOneStem
              function.
   11/02/93 - Be sure to filtrate special bits in nucleotides before trying
              to match them. Use posSE paramter to know when we must
              filtrate bad positions.
              If the fast search switch is activated [-f], filtrate invalid
              positions for the second element of the priority array.
   15/02/93 - Added the MotifPtr parameter and now uses a different method
              for filtering marked positions. */

long PrevPos (long PosFirst, long PosLast, typSE *SEPtr, typMotif *MotifPtr,
              typSequence *SequencePtr, int posSE)
{
  int patlength = SEPtr->patlength;
  register long i, j;
  register short int *seq = SequencePtr->sequence;
  register char *pat = SEPtr->pattern;
  boolean marked;
  short int reversemark;

  /* Must we check this SE as marked? */
  if (fastsearch && (posSE < MotifPtr->maxmark))
  {
    marked = TRUE;
    reversemark = rejectr [posSE];
  }
  else
    marked = FALSE;

  /* Search the pattern for all valid starting positions */
  for (i = PosFirst; i >= PosLast; i--)
  {
    /* We are in fastsearch mode and this SE is in the mark list? */
    if (marked)
      if ((seq[i] & reversemark) == reversemark)
        continue;

    /* Is there a match there? */
    for (j = 0; j < patlength; j++)
      if (! ((seq [i - patlength + j + 1] & NUCMASK) & (pat [j] & NUCMASK)))
         break;

    /* Do we have a match? */
    if (j == patlength)
      return i;
  }

  /* Pattern not found in the interval */
  return -1;
}
