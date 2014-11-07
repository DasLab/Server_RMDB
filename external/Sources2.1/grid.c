/* ------------------------------------------------------------------------
   Grid.c
   ------

     Functions that handle grids. */

/* ------------------------------- Includes ------------------------------- */

#include "rnamot.h"

/* -------------------------- External variables -------------------------- */

extern int mode;
extern boolean writebars;

/* -------------------------- AdjustIntervals () -------------------------- */

/* Function that adjusts the intervals of two elements in the grid.

   17/01/93 - Creation.
   27/01/93 - Extend the intervals of the elements to their minimum
              required if they have no space at all between them.
   28/01/93 - Use length field in the typStrand structure.
   02/02/93 - Added paramter "solution" which is used to distinguish a grid
              in construction and a solution grid. When a grid is
              incomplete, we can use helix's interval adjustment to
              continue the search but when it's a solution grid, the
              helixes are crystallized and their position may not change.
              In that situation, their intervals are used as reference
              points to adjust their single strand neighbours. */

void AdjustIntervals (typGrid *GridPtr, typMotif *MotifPtr,
                      int posgrid1, int posgrid2, int solution)
{
  long avail1, avail2;
  long distance;
  typStrand *Strand1, *Strand2;
  typSE *SEPtr1, *SEPtr2;
  long offset;

  /* Keep pointers on strands */
  Strand1 = &(GridPtr->strands[posgrid1]);
  Strand2 = &(GridPtr->strands[posgrid2]);

  /* Keep pointers on the elements in the grid */
  SEPtr1 = &(MotifPtr->template[posgrid1]);
  SEPtr2 = &(MotifPtr->template[posgrid2]);

  /* Calculate available space */
  if ((solution) && (SEPtr1->type == 'H'))
    avail1 = 0;
  else
    avail1 = SEPtr1->length.max - Strand1->length;

  if ((solution) && (SEPtr2->type == 'H'))
    avail2 = 0;
  else
    avail2 = SEPtr2->length.max - Strand2->length;

  /* Calculate minimal distance to fill between posgrid1 and posgrid2 */
  distance = Strand2->first - Strand1->last - 1 -
             MotifPtr->disttab[posgrid1 * MotifPtr->nbSE + posgrid2].max;

  /* The two elements don't have any space to fill between them? */
  if (distance == 0)
  {
    /* The elements are next one to the other? */
    if (Strand2->first - Strand1->last - 1 == 0)
    {
      /* Calculate required minimal offset to fill */
      if ((offset = SEPtr1->length.min - Strand1->length) > 0)
      {
        Strand1->first -= offset;
        Strand1->length += offset;
      }

      /* Calculate required minimal offset to fill */
      if ((offset = SEPtr2->length.min - Strand2->length) > 0)
      {
        Strand2->last += offset;
        Strand2->length += offset;
      }
    }

    return;
  }

  /* All available space is required? */
  if (distance == avail1 + avail2)
  {
    Strand1->last   += avail1;
    Strand1->length += avail1;
    Strand2->first  -= avail2;
    Strand2->length += avail2;
  }
  else
  {
    /* The posgrid1 element has not enough available space for filling the
       distance to posgrid2? */
    if ((offset = distance - avail1) > 0)
    {
      Strand2->first  -= offset;
      Strand2->length += offset;
    }

    /* The posgrid2 element has not enough available space for filling the
       distance to posgrid1? */
    if ((offset = distance - avail2) > 0)
    {
      Strand1->last   += offset;
      Strand1->length += offset;
    }
  }
}

/* ------------------------------ CopyGrid () ----------------------------- */

/* Function that copies a grid into another.

   07/01/93 - Creation.
   21/01/93 - Copy mismatchs value.
   03/02/93 - Copy wobbles value.
   07/02/93 - Copy solution flag. */

void CopyGrid (typGrid *GridSrc, typGrid *GridDst)
{
  register int i;

  GridDst->size      = GridSrc->size;
  GridDst->score     = GridSrc->score;
  GridDst->saved     = GridSrc->saved;
  GridDst->mismatchs = GridSrc->mismatchs;
  GridDst->wobbles   = GridSrc->wobbles;
  GridDst->solution  = GridSrc->solution;

  for (i = 0; i < GridSrc->size; i++)
    GridDst->strands[i] = GridSrc->strands[i];
}

/* ----------------------------- CreateGrid () ---------------------------- */

/* Function that creates and initializes a typGrid structure.

   20/12/92 - Creation.
   03/02/93 - Initialize wobbles value.
   07/02/93 - Initialize solution flag. */

typGrid *CreateGrid (typMotif *MotifPtr)
{
  int i;
  typGrid *GridPtr;

  if (! (GridPtr = (typGrid *) malloc (sizeof (typGrid))))
  {
    fprintf (stderr, "Error, creation of a grid\n");
    return NULL;
  }

  /* Initialize grid */
  GridPtr->size      = MotifPtr->nbSE;
  GridPtr->score     = INITIALSCORE;
  GridPtr->saved     = FALSE;
  GridPtr->solution  = FALSE;
  GridPtr->mismatchs = 0;
  GridPtr->wobbles   = 0;

  /* Allocate typStrand array */
  if (! (GridPtr->strands = (typStrand *) malloc (sizeof (typStrand) *
                            GridPtr->size)))
  {
    fprintf (stderr, "Error, creation of a typStrand array for a grid\n");
    free (GridPtr);
    return NULL;
  }

  /* Initialize strands */
  for (i = 0; i < GridPtr->size; i++)
  {
    GridPtr->strands[i].first  = -1;
    GridPtr->strands[i].last   = -1;
    GridPtr->strands[i].pos    = 1;
    GridPtr->strands[i].pospat = -1;
    GridPtr->strands[i].length = 0;
    GridPtr->strands[i].left   = -1;
    GridPtr->strands[i].right  = -1;
  }

  return GridPtr;
}

/* ----------------------------- FillHoles () ----------------------------- */

/* Function that fills the non searched elements in the solution grid.

   02/02/93 - Creation. */

void FillHoles (typGrid *GridTemp, typMotif *MotifPtr)
{
  int posgrid;
  typStrand *StrandPtr;

  for (posgrid = 0; posgrid < GridTemp->size; posgrid++)
  {
    /* Keep a pointer on the current strand */
    StrandPtr = &(GridTemp->strands[posgrid]);

    /* This element is not empty? */
    if (! StrandIsNull (*StrandPtr))
      continue;

    /* It's the first element in the grid? */
    if (posgrid == 0)
    {
      /* The following element is not null? */
      if ((GridTemp->size > 1) && (! StrandIsNull (GridTemp->strands[1])))
      {
        PutStrand (GridTemp, posgrid, GridTemp->strands[1].first - 1,
                                      GridTemp->strands[1].first - 1, FALSE);
        AdjustIntervals (GridTemp, MotifPtr, 0, 1, TRUE);
      }

      continue;
    }

    /* It's the last element in the grid? */
    if (posgrid == GridTemp->size - 1)
    {
      /* The preceding element is not null? */
      if (! StrandIsNull (GridTemp->strands[posgrid - 1]))
      {
        PutStrand (GridTemp, posgrid, GridTemp->strands[posgrid - 1].last + 1,
                                      GridTemp->strands[posgrid - 1].last + 1,
                                      FALSE);
        AdjustIntervals (GridTemp, MotifPtr, posgrid - 1, posgrid, TRUE);
      }

      continue;
    }

    /* This element has two non empty neighbours? */
    if ((! StrandIsNull (GridTemp->strands[posgrid - 1])) &&
        (! StrandIsNull (GridTemp->strands[posgrid + 1])))
    {
      /* Is there any space in that hole? */
      if ((GridTemp->strands[posgrid + 1].first -
           GridTemp->strands[posgrid - 1].last - 1) > 0)
        PutStrand (GridTemp, posgrid,
                   GridTemp->strands[posgrid - 1].last + 1,
                   GridTemp->strands[posgrid + 1].first - 1, FALSE);
    }
  }
}

/* --------------------------- FillStrands () --------------------------- */

/* Function that fills the "holes" (null strands) in a grid.

   01/02/93 - Creation.
   02/02/93 - Redesign of the algorithm. */

void FillStrands (typGrid *GridTemp, typMotif *MotifPtr)
{
  int posSE, posgrid;

  for (posSE = 0; posSE < MotifPtr->nbbestpriority; posSE++)
  {
    /* Find the index of that element in the grid */
    posgrid = MotifPtr->bestpriority [posSE];

    /* If that element is a single-strand, we adjust its intervals */
    if (MotifPtr->template[posgrid].type == 'S')
    {
      /* Can we adjust with the left neighbour? */
      if (posgrid > 0)
        if (! StrandIsNull (GridTemp->strands[posgrid - 1]))
          AdjustIntervals (GridTemp, MotifPtr, posgrid - 1, posgrid, TRUE);

      /* Can we adjust with the right neighbour? */
      if (posgrid < MotifPtr->nbbestpriority - 1)
        if (! StrandIsNull (GridTemp->strands[posgrid + 1]))
          AdjustIntervals (GridTemp, MotifPtr, posgrid, posgrid + 1, TRUE);
    }
  }
}

/* ------------------------------ FreeGrid () ----------------------------- */

/* Function that cleans a typGrid structure.

   20/12/92 - Creation. */

void FreeGrid (typGrid *GridPtr)
{
  if (! GridPtr)
    return;

  /* Free strands array */
  if (GridPtr->strands)
    free (GridPtr->strands);

  /* Free typGrid structure */
  free (GridPtr);
}

/* ------------------------------ GridCmp () ------------------------------ */

/* Function that compares two grids and returns TRUE if they are identical
   (i.e. intervals are the same, position of patterns in those interval may
   be different).

   17/01/93 - Creation.
   02/02/93 - Pass the motif structure in argument so we verify the
              position at which we found each element in the priority list
              as a comparaison for distinguishing two grids. */

int GridCmp (typMotif *MotifPtr, typGrid *GridA, typGrid *GridB)
{
  int posSE, posgrid1, posgrid2;

  /* Verify position found for all elements that had to be scanned */
  for (posSE = 0; posSE < MotifPtr->nbbestpriority; posSE++)
  {
    /* Find the position of that element in the grid */
    posgrid1 = MotifPtr->bestpriority[posSE];

    /* First values of that element are different? */
    if (GridA->strands[posgrid1].first != GridB->strands[posgrid1].first)
      return FALSE;

    /* Last values of that element are different? */
    if (GridA->strands[posgrid1].last != GridB->strands[posgrid1].last)
      return FALSE;

    /* If that element is a stem, we verify the values of the second stem */
    if (MotifPtr->template[posgrid1].type == 'H')
    {
      /* Find the position of the second stem in the grid */
      posgrid2 = MotifPtr->template[posgrid1].secondstemnb;

      /* First values of that element are different? */
      if (GridA->strands[posgrid2].first != GridB->strands[posgrid2].first)
        return FALSE;

      /* Last values of that element are different? */
      if (GridA->strands[posgrid2].last != GridB->strands[posgrid2].last)
        return FALSE;
    }
  }

  /* The two grids are identical */
  return TRUE;
}

/* ----------------------------- GridScore () ----------------------------- */

/* Function that returns an evaluation score for a grid.

   03/01/93 - Creation.
   17/01/93 - Major modifications.
   21/01/93 - Final modifications.
   06/02/93 - Added paramter MotifPtr->nbSE - 1 to the NextPos function.
              It's supposed to indicate the posSE value but here, the grid
              is complete and we're not interested to eliminate SE that
              have all 'N' nucleotides in the sequence.
   17/02/93 - Add penalty to score if non restrictive pattern is not present. */

float GridScore (typGrid *GridTemp, typMotif *MotifPtr,
                 typSequence *SequencePtr)
{
  int i;
  int stem1, stem2;
  float score = 0.0;
  typSE *SEPtr;
  typStrand *StrandPtr;

  /* For each element in the grid */
  for (i = 0; i < GridTemp->size; i++)
  {
    /* Keep pointer on SE in template */
    SEPtr = &(MotifPtr->template[i]);

    /* Keep pointer on Strand in grid */
    StrandPtr = &(GridTemp->strands[i]);

    /* If this SE has a non restrictive pattern, we verify if it's present in
       the grid */
    if ((! StrandIsNull (*StrandPtr)) && (! SEPtr->strict) &&
        (SEPtr->patlength > 0))
    {
      if (NextPos (StrandPtr->first, StrandPtr->last - SEPtr->patlength + 1,
           SEPtr, MotifPtr, SequencePtr, FALSE, MotifPtr->nbSE - 1) == -1)
        score += PATNOTFOUND;
    }
  }

  /* Evaluate score for helix */
  for (i = 0; i < MotifPtr->nbH / 2; i++)
  {
    /* Keep index of stems in template */
    stem1 = MotifPtr->stems[i].pos1;
    stem2 = MotifPtr->stems[i].pos2;

    /* We found that helix? */
    if (! StrandIsNull (GridTemp->strands[stem1]))
      score += HelixScore (stem1, stem2, GridTemp, MotifPtr, SequencePtr);
    else
      /* That helix was not found? Penalize the score... */
      if (MotifPtr->template[i].length.max != 0)
        score += 1000.0;
  }

  return score;
}

/* ---------------------------- HelixScore () ----------------------------- */

/* Function that returns an evalutation score for an helix.

   03/01/93 - Creation.
   21/01/93 - Verification for the starting position of the helix added. */

float HelixScore (int stem1, int stem2, typGrid *GridTemp, typMotif *MotifPtr,
                  typSequence *SequencePtr)
{
  long posstart, posend, length;
  float mismatchs;
  float energy, es;

  /* Keep starting and ending values. If that stem has no restrictive pattern,
     then use pospat as starting position, else use first (this is required
     because the algorithm for adjusting the intervals does not verify if the
     length of both parts of an helix are of the same length). */

  if (MotifPtr->template[stem1].strict)
  {
    posstart = GridTemp->strands[stem1].first;
    posend   = GridTemp->strands[stem2].last;
    length   = GridTemp->strands[stem1].length;
  }
  else
  {
    posstart = GridTemp->strands[stem1].pospat;
    posend   = GridTemp->strands[stem2].last,
    length   = GridTemp->strands[stem1].last - posstart + 1;
  }

  /* Evaluate mismatchs */
  mismatchs = 50.0 *
              NbMismatchs (posstart, posend, length, SequencePtr);

  /* Evaluate energy */
  energy = SimpleEnergy (posstart, posend, length, SequencePtr);

  if (energy >= 0.0)
    es = 1.0;
  else
    es = -1.0 / energy;

  return (mismatchs + MotifPtr->template[stem1].length.max - length + es);
}

/* ----------------------------- PutStrand () ----------------------------- */

/* Function that adds a strand information in the grid.

   23/12/92 - Creation.
   17/01/93 - Keep pattern starting position in pospat.
   28/01/93 - Keep strand length in the structure.
              Adjust right and left neighbours's indexes.
   08/02/93 - Added posupdate flag to indicate if we shall update or not
              the value of pospat (position of the restrictive pattern in
              the sequence). */

void PutStrand (typGrid *GridPtr, int posgrid, long posinf, long possup,
                int posupdate)
{
  int i;
  int left;
  int right;
  typStrand *StrandPtr = &(GridPtr->strands[posgrid]);

  StrandPtr->first  = posinf;
  StrandPtr->last   = possup;
  StrandPtr->length = possup - posinf + 1;

  /* Shall we update the value of pospat? */
  if (posupdate)
    StrandPtr->pospat = posinf;

  /* Find right and left neighbours */
  left  = StrandPtr->left;
  right = StrandPtr->right;

  /* Adjust left neighbours */
  if (left == -1)
    for (i = 0; i < posgrid; i++)
      GridPtr->strands[i].right = posgrid;
  else
    for (i = left; i < posgrid; i++)
      GridPtr->strands[i].right = posgrid;

  /* Adjust right neighbours */
  if (right == -1)
    for (i = GridPtr->size - 1; i > posgrid; i--)
      GridPtr->strands[i].left = posgrid;
  else
    for (i = right; i > posgrid; i--)
      GridPtr->strands[i].left = posgrid;
}

/* ------------------------------ SaveGrid () ----------------------------- */

/* Function that writes a grid into a file.

   06/01/93 - Creation.
   21/01/93 - Use mismatchs count already present in the grid structure.
   03/02/93 - Last value of position has been corrected.
   07/02/93 - Write wobble count in the file.
   10/02/93 - Use the [-b] switch in alignment mode.
   09/05/93 - The single-strands in the grids now contain the minimal
              length they must have so that all occurances of that element
              in all the solutions have at least the same length. When we
              write a grid and the current element is a single-strand, we
              first output the [first, last] interval of the sequence.
              Then, if the element's "length" field is greater than the
              value of "last - first + 1", then it means we must ouput some
              delimiter characters in order to be able to align that strand.
*/

void SaveGrid (FILE *f, typGrid *GridTemp, typMotif *MotifPtr,
               typSequence *SequencePtr)
{
  int i, col;
  long a, b, j, k;
  long length, SElength;
  typSE *SEPtr;

  /* Print general solution information */
  fprintf (f, "|SCO:%8.2f|POS:%ld-%ld|MIS:%2d|WOB:%2d|\n",
           GridTemp->score,
           GridTemp->strands[0].first + 1,
           GridTemp->strands[MotifPtr->nbSE - 1].last + 1,
           GridTemp->mismatchs,
           GridTemp->wobbles);

  col = 1;

  /* Must we write separator bars? */
  if ((mode == SEARCH) || (writebars))
    fprintf (f, "|");

  for (i = 0; i < GridTemp->size; i++)
  {
    length = GridTemp->strands[i].length;
    SEPtr = &(MotifPtr->template[i]);
    SElength = SEPtr->length.max;

    if (SElength != 0)
    {
      if (length != 0)
      {
        k = 0;
        a = GridTemp->strands[i].first;
        b = GridTemp->strands[i].last;

        /* We have more than 50 nucleotides to write? */
        if ((b - a + 1) > 50)
          fprintf (f, ".. %d nuc ..", b - a);
        else
        {
          for (j = a; (j <= b) && (k < SElength); j++)
          {
            fprintf (f, "%c",
                     MaskToBase((char) (SequencePtr->sequence[j] & 0x00ff)));
            ChangeLine (f, &col);
            k++;
          }

          /* This element is a single-strand? */
          if (SEPtr->type == 'S')
          {
            /* Write the alignment spaces if necessary */
            for (j = 0; j < (length - (b - a + 1)); j++)
            {
              fprintf (f, "-");
              ChangeLine (f, &col);
            }
          }
        }
      }
    }

    if ((length == 0) && (SElength != 0))
    {
      fprintf (f, "-");
      ChangeLine (f, &col);
    }

    /* Must we write separator bars? */
    if ((mode == SEARCH) || (writebars))
      fprintf (f, "|");

    ChangeLine (f, &col);
  }

  fprintf (f, "\n");
}

/* ---------------------------- StrandIsNull () --------------------------- */

int StrandIsNull (typStrand Strand)
{
  return (Strand.first == -1) && (Strand.last == -1);
}

/* ----------------------------- TraceGrid () ----------------------------- */

/* Function that traces the current values of a grid.

   04/04/93 - Display left and right neighbours values. */

void TraceGrid (typGrid *GridPtr)
{
  int i;

  printf ("TraceGrid (%d elements, saved: %s, solution: %s, score: %4.3f)\n",
          GridPtr->size, GridPtr->saved ? "YES" : "NO",
          GridPtr->solution ? "YES" : "NO", GridPtr->score);

  for (i = 0; i < GridPtr->size; i++)
  {
    printf ("%2d - F: %4ld, L: %4ld, Pos: %2ld, Pospat: %2ld, Length: %3ld, "
            "L: %2ld, R: %2ld\n",
            i, GridPtr->strands[i].first, GridPtr->strands[i].last,
            GridPtr->strands[i].pos,
            GridPtr->strands[i].pospat,
            GridPtr->strands[i].length,
            GridPtr->strands[i].left,
            GridPtr->strands[i].right);
  }
}

/* ----------------------------- TraceGrids () ---------------------------- */

/* Function that traces the values of all grids in the solution structure.

   21/03/93 - Added the nbalts field in the solution structure. */

void TraceGrids (typSolution *SolutionPtr)
{
  int counter = 0;
  typGridList *ListTemp = SolutionPtr->gridlist;

  printf ("There are %d grids (solutions) in the Solution\n",
           SolutionPtr->nbsols + SolutionPtr->nbalts);

  while (ListTemp)
  {
    printf ("Trace of grid %d (score: %6.2f)\n", counter++,
            ListTemp->info.score);
    TraceGrid (&(ListTemp->info));

    ListTemp = ListTemp->next;
  }
}

/* ----------------------------- UpdateLeft () ---------------------------- */

/* Function that adjusts the intervals of the left neighbours of a freshly
   added single-strand in the grid.

   17/01/93 - Creation.
   27/01/93 - Return when the element posSE is the first in the grid.
   28/01/93 - Just adjust with the left element.
   31/01/93 - Update neighbours of second stem if it's an helix. */

void UpdateLeft (typGrid *GridPtr, typMotif *MotifPtr, int posSE)
{
  int posgrid1, posgrid2;
  typSE *SEPtr;

  /* Find the index of first element in the grid */
  posgrid2 = MotifPtr->bestpriority[posSE];

  /* Keep a pointer on that element */
  SEPtr = &(MotifPtr->template[posgrid2]);

  /* If this element is a stem, we begin the adjustment with the second stem */
  if (SEPtr->type == 'H')
    posgrid2 = SEPtr->secondstemnb;

  /* This element is the first in the grid? */
  if (posgrid2 == 0) return;

  /* Adjust intervals with left neighbours */
  while ((posgrid1 = GridPtr->strands[posgrid2].left) != -1)
  {
    AdjustIntervals (GridPtr, MotifPtr, posgrid1, posgrid2, FALSE);
    posgrid2 = posgrid1;
  }
}

/* ---------------------------- UpdateRight () ---------------------------- */

/* Function that adjusts the intervals of the right neighbours of a freshly
   added single-strand in the grid.

   17/01/93 - Creation.
   27/01/93 - Adjustment of intervals if last element in the grid.
   28/01/93 - Use length field in the typStrand structure.
              Just adjust with the right element.
   31/01/93 - Update neighbours of second stem if it's an helix.
   01/02/93 - Correction of a bug when updating the last element in the grid
              (the length was not properly restored). */

void UpdateRight (typGrid *GridPtr, typMotif *MotifPtr,
                  typSequence *SequencePtr, int posSE)
{
  int posgrid1, posgrid2;
  typStrand *StrandPtr;
  typSE *SEPtr;
  long offset;

  /* Find the index of first element in the grid */
  posgrid1 = MotifPtr->bestpriority[posSE];

  /* Keep a pointer on that strand */
  StrandPtr = &(GridPtr->strands[posgrid1]);

  /* Keep a pointer on that element */
  SEPtr = &(MotifPtr->template[posgrid1]);

  /* This element is the last in the grid? */
  if (posgrid1 == MotifPtr->nbSE - 1)
  {
    /* Calculate offset to fill if we are near the end of the sequence */
    offset = SEPtr->length.min - StrandPtr->length -
             (SequencePtr->length - StrandPtr->last - 1);

    /* Must we pull the beginning of that strand? */
    if (offset > 0)
    {
      StrandPtr->first -= offset;
      StrandPtr->length += offset;
    }

    /* If this SE is the last in the grid, then it's not a stem for an helix
       (because posSE for an helix in the bestpriority array always indicates
       the index of the first stem in the template, so there is always a
       second stem and it's impossible for posgrid1 to be the last item and
       the grid and be a stem for an helix!). Sinci it can have no right
       neighbour, we just quit. */
    return;
  }

  /* If this element is a stem, we begin the adjustment with the second stem */
  if (SEPtr->type == 'H')
    posgrid1 = SEPtr->secondstemnb;

  /* Adjust intervals with right neighbours */
  while ((posgrid2 = GridPtr->strands[posgrid1].right) != -1)
  {
    AdjustIntervals (GridPtr, MotifPtr, posgrid1, posgrid2, FALSE);
    posgrid1 = posgrid2;
  }
}
