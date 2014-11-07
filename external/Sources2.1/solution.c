/* ------------------------------------------------------------------------
   Solution.c
   ----------

     Functions that manage solutions. */

/* ------------------------------- Includes ------------------------------- */

#include "rnamot.h"


/* -------------------------- External variables -------------------------- */

extern int mode;
extern boolean reverse;
extern boolean silent;
extern boolean noalternative;
extern boolean formatted;

/* ---------------------------- AddSolution () ---------------------------- */

/* Function that adds a solution to the solution structure.

   03/01/93 - Creation.
   21/01/93 - Elimination of the mismatchs variable and keep mismatch count
              in the grid structure itself.
   07/02/93 - Only add solutions in the grid if we're in the SEARCH mode.
              If we're in ALIGNMENT mode, then the bestfault and bestgrid
              grids are updated.
   13/04/93 - Don't use the AlreadyFound() function anymore. A solution
              can't be present twice in the list now that intervals are
              managed correctly. */

void AddSolution (typGrid *GridPtr, typMotif *MotifPtr,
                  typSequence *SequencePtr, typSolution *SolutionPtr)
{
  int lasttotsols;
  typGrid *GridTemp;

  /* Create a temporary grid */
  GridTemp = CreateGrid (MotifPtr);

  /* Copy the solution in a temporary grid */
  CopyGrid (GridPtr, GridTemp);

  /* That grid is a solution */
  GridTemp->solution = TRUE;

  /* Fill the intervals of the searched strands in the grid */
  FillStrands (GridTemp, MotifPtr);

  /* That solution has already been found? */
/*
  if (AlreadyFound (SolutionPtr, MotifPtr, GridTemp))
    return;
*/

  /* Fill the holes for the non searched elements */
  FillHoles (GridTemp, MotifPtr);

  /* Calculate the score of that grid */
  GridTemp->score = GridScore (GridTemp, MotifPtr, SequencePtr);

  /* We have found a new best fault? */
  if (GridTemp->score < SolutionPtr->bestfault->score)
    CopyGrid (GridTemp, SolutionPtr->bestfault);

  /* We found a new best grid? */
  if (GridTemp->score < SolutionPtr->bestgrid->score)
    CopyGrid (GridTemp, SolutionPtr->bestgrid);

  /* Insert grid in solution */
  if (mode == SEARCH)
  {
    /* Keep last total sols value */
    lasttotsols = SolutionPtr->nbsols + SolutionPtr->nbalts;

    if (! InsertGrid (GridTemp, SolutionPtr))
    {
      FreeGrid (GridTemp);
      return;
    }

    /* We can talk? */
    if (! silent && (lasttotsols != (SolutionPtr->nbsols + SolutionPtr->nbalts)))
    {
      printf ("\r%6d  %s %7d  %5d  %5d   %6d    %6d",
              SequencePtr -> nbsequences,
              SequencePtr->complemented ? " YES" : "  NO",
              SequencePtr->length,
              SolutionPtr->nbsols,
              SolutionPtr->nbalts,
              SolutionPtr->totsols,
              SolutionPtr->totalts);

      fflush (stdout);
    }
  }

  FreeGrid (GridTemp);
}

/* ---------------------------- AlreadyFound () --------------------------- */

/* Function that indicates if a grid has already been found as a solution,
   i.e. verifies if a grid is present in the grid list of the solution
   structure.

   17/01/93 - Creation.
   02/01/93 - Pass the motif structure in argument so we verify the
              position at which we found each element in the priority list
              as a comparaison for distinguishing two grids. */

int AlreadyFound (typSolution *SolutionPtr, typMotif *MotifPtr,
                  typGrid *GridPtr)
{
  typGridList *GridListPtr = SolutionPtr->gridlist;

  while (GridListPtr)
  {
    /* The grid is already in the list? */
    if (GridCmp (MotifPtr, GridPtr, &(GridListPtr->info)))
      return TRUE;

    GridListPtr = GridListPtr->next;
  }

  return FALSE;
}

/* ----------------------------- ChangeLine () ---------------------------- */

/* Function that makes sure to not write more than 80 characters on a same
   line in an output file.

   06/01/93 - Creation. */

void ChangeLine (FILE *f, int *col)
{
  (*col)++;

  if (formatted && (*col == 80))
  {
    fprintf (f, "\n");
    *col == 1;
  }
}

/* --------------------------- DisplayRunData () -------------------------- */

/* Function that displays the current status of the program.

   21/03/93 - Creation. */

void DisplayRunData (typSequence *SequencePtr, typSolution *SolutionPtr,
                     int ratio)
{
  if (mode == SEARCH)
    printf ("\r%6d  %s %7d  %5d  %5d   %6d    %6d     %3d%%",
            SequencePtr->nbsequences,
            SequencePtr->complemented ? " YES" : "  NO",
            SequencePtr->length,
	    SolutionPtr->nbsols,
            SolutionPtr->nbalts,
	    SolutionPtr->totsols,
            SolutionPtr->totalts,
            ratio);
  else
    printf ("\r%6d %7d    %s   %3d%%",
            SequencePtr->nbsequences,
            SequencePtr->length,
            (SolutionPtr->bestgrid->score < INITIALSCORE) ? "YES" : " NO",
            ratio);

  fflush (stdout);
}

/* ---------------------------- FreeGridList () --------------------------- */

/* Function that frees a grid list in a typSolution structure.

   22/12/92 - Creation. */

void FreeGridList (typSolution *SolutionPtr)
{
  typGridList *GridListPtr;

  if (SolutionPtr->gridlist)
  {
    while (SolutionPtr->gridlist)
    {
      GridListPtr = SolutionPtr->gridlist;
      SolutionPtr->gridlist = GridListPtr->next;

      free (GridListPtr->info.strands);
      free (GridListPtr);
    }

    SolutionPtr->gridlist = NULL;
  }
}

/* ---------------------------- FreeSolution () --------------------------- */

/* Function that cleans a solution structure.

   20/12/92 - Creation.
   22/12/92 - Free grid list in solution.
   06/01/93 - Close solution files if open.
   21/01/93 - Free bestgrid and bestfault if allocated. */

void FreeSolution (typSolution *SolutionPtr)
{
  /* Free bestgrid */
  if (SolutionPtr->bestgrid)
    FreeGrid (SolutionPtr->bestgrid);

  /* Free bestfault */
  if (SolutionPtr->bestfault)
    FreeGrid (SolutionPtr->bestfault);

  /* Close solution file? */
  if (SolutionPtr->fsol)
    fclose (SolutionPtr->fsol);

  /* Close alternatives file? */
  if (SolutionPtr->falt)
    fclose (SolutionPtr->falt);

  /* Free grid list */
  FreeGridList (SolutionPtr);

  /* Free optimal solution file name */
  if (SolutionPtr->solname)
    free (SolutionPtr->solname);

  /* Free alternative solutions file name */
  if (SolutionPtr->altname)
    free (SolutionPtr->altname);
}

/* ------------------------- InitializeSolution () ------------------------ */

/* Function that initializes variables for a new solution structure.

   20/12/92 - Creation.
   06/01/93 - File handlers added.
   21/03/93 - Total number of alternative solutions added. */

int InitializeSolution (char *solname, char *altname, typSolution *SolutionPtr)
{
  /* Initialize fields */
  SolutionPtr->solname = NULL;
  SolutionPtr->altname = NULL;
  SolutionPtr->fsol = NULL;
  SolutionPtr->falt = NULL;
  SolutionPtr->gridlist = NULL;
  SolutionPtr->totsols = 0;
  SolutionPtr->totalts = 0;
  SolutionPtr->bestgrid = NULL;
  SolutionPtr->bestfault = NULL;

  /* Allocate buffer for optimal solution file name */
  if (! (SolutionPtr->solname = (char *) malloc (strlen (solname) + 1)))
  {
    fprintf (stderr, "Error, memory allocation for the solution name\n");
    return BUG;
  }

  /* Allocate buffer for alternatives solutions file name */
  if (! (SolutionPtr->altname = (char *) malloc (strlen (altname) + 1)))
  {
    fprintf (stderr, "Error, memory allocation for the alternate name\n");
    free (SolutionPtr->solname);
    return BUG;
  }

  /* Copy names */
  strcpy (SolutionPtr->solname, solname);
  strcpy (SolutionPtr->altname, altname);

  return OK;
}

/* ----------------------------- InsertGrid () ---------------------------- */

/* Function that inserts a grid in a solution structure. The position of
   insertion is ordered by:

   1) The starting position of the first strand of the grid.
   2) The scores of each solution.

   03/01/93 - Creation.
   12/01/93 - Insertion order coded.
   29/01/93 - Don't insert alternative solutions if [-n] switch (no alt) is
              activated.
   07/02/93 - If the mode of use is ALIGNMENT, then always add the grids at
              the end of the list.
   21/03/93 - Update the total number of alternative and non-alternatives
              solutions found (totalts and totsols) when inserting the
              grids in the solution structure.
   04/04/93 - Correction of a bug that caused the insertion of an
              aternative solution to be considered as a new non-alternative
              solution (fourth case of insertion). */

int InsertGrid (typGrid *GridTemp, typSolution *SolutionPtr)
{
  long posnew, posold;
  float scorenew, scoreold;
  typGridList *GridListPtr;
  typGridList *ListTemp;

  /* Allocate a new list element */
  if (! (GridListPtr = (typGridList *) malloc (sizeof (typGridList))))
  {
    fprintf (stderr, "Error, not enough memory to insert a solution\n");
    return BUG;
  }

  /* Allocate memory for strands array */
  if (! (GridListPtr->info.strands = (typStrand *)
      malloc (sizeof (typStrand) * GridTemp->size)))
  {
    free (GridListPtr);
    return BUG;
  }

  /* Initialise next field */
  GridListPtr->next = NULL;

  /* Copy grid */
  CopyGrid (GridTemp, &(GridListPtr->info));

  /* Is the list empty? */
  if (SolutionPtr->gridlist == NULL)
  {
    SolutionPtr->gridlist = GridListPtr;

    /* One more non-alternative solution */
    SolutionPtr->nbsols++;
    SolutionPtr->totsols++;

    return OK;
  }

  /* If the mode is ALIGNMENT, always add the grids at the end of the list */
  if (mode == ALIGNMENT)
  {
    /* Find pointer on last element in the list */
    ListTemp = SolutionPtr->gridlist;

    while (ListTemp->next)
      ListTemp = ListTemp->next;

    /* Insert the new element at the end of the list */
    ListTemp->next = GridListPtr;
    SolutionPtr->nbsols++;

    return OK;
  }

  /* Keep starting positions */
  posnew = GridListPtr->info.strands[0].first;
  posold = SolutionPtr->gridlist->info.strands[0].first;

  /* Keep scores */
  scorenew = GridListPtr->info.score;
  scoreold = SolutionPtr->gridlist->info.score;

  /* We insert the grid in the head of the list if its starting position is
     lower than the first element's starting position */
  if (posnew < posold)
  {
    GridListPtr->next = SolutionPtr->gridlist;
    SolutionPtr->gridlist = GridListPtr;

    /* One more non-alternative solution */
    SolutionPtr->nbsols++;
    SolutionPtr->totsols++;

    return OK;
  }

  /* We insert the grid in the head of the list if its starting position is
     the same as the first element's starting position but its score is
     lower than the first element's */
  if ((! noalternative) && (posnew == posold) && (scorenew < scoreold))
  {
    GridListPtr->next = SolutionPtr->gridlist;
    SolutionPtr->gridlist = GridListPtr;

    /* One more alternative solution */
    SolutionPtr->nbalts++;
    SolutionPtr->totalts++;

    return OK;
  }

  /* We don't want alternative solutions? */
  if (noalternative)
  {
    /* We found a new best solution? Replace old best solution with it */
    if ((posnew == posold) && (scorenew < scoreold))
    {
      GridListPtr->next = SolutionPtr->gridlist->next;
      free (SolutionPtr->gridlist->info.strands);
      free (SolutionPtr->gridlist);
      SolutionPtr->gridlist = GridListPtr;

      return OK;
    }

    /* That grid is an alternative solution we don't want to insert? */
    if ((posnew == posold) && (scorenew >= scoreold))
    {
      free (GridListPtr->info.strands);
      free (GridListPtr);

      return OK;
    }
  }

  /* We scan the list and find the next insertion position */
  ListTemp = SolutionPtr->gridlist;

  while (ListTemp->next)
  {
    /* Update temporary position and score values */
    posold = ListTemp->next->info.strands[0].first;
    scoreold = ListTemp->next->info.score;

    /* We insert the grid in the head of the list if its starting position
       is lower than the first element's starting position */
    if (posnew < posold)
    {
      /* Is that a new non-alternative solution? */
      if (posnew != ListTemp->info.strands[0].first)
      {
        /* One more non-alternative solution */
        SolutionPtr->nbsols++;
        SolutionPtr->totsols++;
      }
      else
      {
        /* One more alternative solution */
        SolutionPtr->nbalts++;
        SolutionPtr->totalts++;
      }

      GridListPtr->next = ListTemp->next;
      ListTemp->next = GridListPtr;

      return OK;
    }

    /* We insert the grid in the head of the list if its starting position
       is the same as the first element's starting position but its score
       is lower than the first element's */
    if ((! noalternative) && (posnew == posold) && (scorenew < scoreold))
    {
      GridListPtr->next = ListTemp->next;
      ListTemp->next = GridListPtr;

      /* One more alternative solution */
      SolutionPtr->nbalts++;
      SolutionPtr->totalts++;

      return OK;
    }

    /* We don't want alternative solutions? */
    if (noalternative)
    {
      /* We found a new best solution? Replace old best solution with it */
      if ((posnew == posold) && (scorenew < scoreold))
      {
        GridListPtr->next = ListTemp->next->next;
        free (ListTemp->next->info.strands);
        free (ListTemp->next);
        ListTemp->next = GridListPtr;

        return OK;
      }

      /* That grid is an alternative solution we don't want to insert? */
      if ((posnew == posold) && (scorenew >= scoreold))
      {
        free (GridListPtr->info.strands);
        free (GridListPtr);

        return OK;
      }
    }

    ListTemp = ListTemp->next;
  }

  /* Insert the new element at the end of the list */
  ListTemp->next = GridListPtr;

  /* If the starting positions of the two last elements of the list are the
     same, it's an alternative solution */
  if (ListTemp->info.strands[0].first == GridListPtr->info.strands[0].first)
  {
    /* One more alternative solution */
    SolutionPtr->nbalts++;
    SolutionPtr->totalts++;
  }
  else
  {
    /* One more non-alternative solution */
    SolutionPtr->nbsols++;
    SolutionPtr->totsols++;
  }

  return OK;
}

/* -------------------------- SaveAlternatives () ------------------------- */

/* Function that saves alternative solutions in the alternative solutions
   file.

   12/01/93 - Creation.
   16/01/93 - Optimized by writing a better solution insertion algorithm.
              Now the solutions are ordered by starting position and then
              by score value.
   29/01/93 - Save sequence's commentary instead of sequence's name.
   15/02/93 - Quit function before opening the first time so we'll not
              create an empty file when the [-n] option is active.
   01/04/93 - Correction of a small bug which caused the "comp. sequence"
              message to always be written in the solution file.
              If number of alternative solutions is zero, then quit. */

int SaveAlternatives (typMotif *MotifPtr, typSequence *SequencePtr,
                      typSolution *SolutionPtr)
{
  typGridList *ListTemp;

  /* If we don't want alternative solutions, quit here and no file will be
     created. */
  if (noalternative)
    return OK;

  /* If we have no alternatives to save, quit */
  if (SolutionPtr->nbalts == 0)
    return OK;

  /* We have to open the alternatives file? */
  if (! SolutionPtr->falt)
  {
    if (! (SolutionPtr->falt = fopen (SolutionPtr->altname, "w")))
    {
      fprintf (stderr, "Error, unable to open alternatives file \"%s\"\n",
                SolutionPtr->altname);
      return BUG;
    }
  }

  /* Write header for alternative solutions file */
  fprintf (SolutionPtr->falt, "\n--- %s --- (%d bases)\n",
           SequencePtr->commentary, SequencePtr->length);

  if (SequencePtr->complemented)
    fprintf (SolutionPtr->falt,
             "---------- complementary sequence ----------\n");

  /* Let's save the alternative solutions */
  ListTemp = SolutionPtr->gridlist;

  while (ListTemp)
  {
    /* This solution has not already been saved? */
    if (! ListTemp->info.saved)
    {
      /* Save that alternative solution */
      SaveGrid (SolutionPtr->falt, &(ListTemp->info), MotifPtr, SequencePtr);

      /* That solution has been saved */
      ListTemp->info.saved = TRUE;
    }

    ListTemp = ListTemp->next;
  }

  return OK;
}

/* --------------------------- SaveSolutions () --------------------------- */

/* Function that saves the best solutions in the sol file and alternative
   solutions in the alt file.

   12/01/93 - Creation.
   16/01/93 - Optimized by writing a better solution insertion algorithm.
              Now the solutions are ordered by starting position and then
              by score value.
   29/01/93 - Save sequence's commentary instead of sequence's name.
   21/03/93 - Don't count the non-alternatives solutions here, but in the
              InsertGrid function.
   01/04/93 - Correction of a small bug which caused the "comp. sequence"
              message to always be written in the solution file.
              If number of solutions is zero, then quit. */

int SaveSolutions (typMotif *MotifPtr, typSequence *SequencePtr,
                   typSolution *SolutionPtr)
{
  long lastpos = -1;
  typGridList *ListTemp;

  /* If we have no alternatives to save, quit */
  if (SolutionPtr->nbsols == 0)
    return OK;

  /* We have to open the solution file? */
  if (! SolutionPtr->fsol)
  {
    if (! (SolutionPtr->fsol = fopen (SolutionPtr->solname, "w")))
    {
      fprintf (stderr, "Error, unable to open solution file \"%s\"\n",
                SolutionPtr->solname);
      return BUG;
    }
  }

  /* Write header for solutions file */
  fprintf (SolutionPtr->fsol, "\n--- %s --- (%d bases)\n",
           SequencePtr->commentary, SequencePtr->length);

  if (SequencePtr->complemented)
    fprintf (SolutionPtr->fsol,
             "---------- complementary sequence ----------\n");

  /* Let's save the best solutions */
  ListTemp = SolutionPtr->gridlist;
  while (ListTemp)
  {
    /* Do we have a new posmin solution? */
    if (ListTemp->info.strands[0].first > lastpos)
    {
      /* Save that best solution */
      SaveGrid (SolutionPtr->fsol, &(ListTemp->info), MotifPtr, SequencePtr);

      /* That solution has been saved */
      ListTemp->info.saved = TRUE;

      /* Update starting position of last saved solution */
      lastpos = ListTemp->info.strands[0].first;
    }

    ListTemp = ListTemp->next;
  }

  return OK;
}
