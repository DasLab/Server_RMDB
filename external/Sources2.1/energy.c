/* ------------------------------------------------------------------------
   Energy.c
   --------

     Functions to calculate match energy. */

/* ------------------------------- Includes ------------------------------- */

#include "rnamot.h"

/* --------------------------- Global variables --------------------------- */

/* Array of base mask match values */

char BaseToPair [16][16] = {
{ 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15},
{ 15,  6,  7,  6,  8,  6,  7,  6,  0,  0,  0,  0,  0,  0,  0,  0},
{ 15,  9, 10,  9,  2,  2,  2,  2, 11,  9, 10,  9,  2,  2,  2,  2},
{ 15,  6,  7,  6,  2,  2,  2,  2,  0,  0,  0,  0,  0,  0,  0,  0},
{ 15, 12,  3,  3, 13, 12,  3,  3,  5,  5,  3,  3,  5,  5,  3,  3},
{ 15,  6,  3,  3,  8,  6,  3,  3,  0,  0,  0,  0,  0,  0,  0,  0},
{ 15,  9,  3,  3,  2,  2,  2,  2,  5,  5,  3,  3,  2,  2,  2,  2},
{ 15,  6,  3,  3,  2,  2,  2,  2,  0,  0,  0,  0,  0,  0,  0,  0},
{ 15,  1, 14,  1,  4,  1,  4,  1, 15,  1, 14,  1,  4,  1,  4,  1},
{ 15,  1,  7,  1,  4,  1,  4,  1,  0,  0,  0,  0,  0,  0,  0,  0},
{ 15,  1, 10,  1,  2,  1,  2,  1, 11,  1, 10,  1,  2,  1,  2,  1},
{ 15,  1,  7,  1,  2,  1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0},
{ 15,  1,  3,  1,  4,  1,  3,  1,  5,  1,  3,  1,  4,  1,  3,  1},
{ 15,  1,  3,  1,  4,  1,  3,  1,  0,  0,  0,  0,  0,  0,  0,  0},
{ 15,  1,  3,  1,  2,  1,  2,  1,  5,  1,  3,  1,  2,  1,  2,  1},
{ 15,  1,  3,  1,  2,  1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0}};

/* Stacking energy of internal base pairs */
int Stacken [6][6] =
{ -9,  -9, -21, -17,  -7,  -5,
 -11,  -9, -23, -18,  -5,  -7,
 -18, -17, -29, -20, -15, -15,
 -23, -21, -34, -29, -19, -13,
  -7,  -5, -13, -15,  -5,  -6,
  -5,  -7, -19, -15,  -5,  -5};

/* ------------------------------ Mismatch () ----------------------------- */

/* Function that indicates if there's a mismatch between two bases.

   21/01/93 - Creation. */

int Mismatch (int value)
{
  return value >= 6;
}

/* ---------------------------- NbMismatchs () ---------------------------- */

/* Function that returns the number of mismatchs in an helix.

   03/01/93 - Creation.
   15/02/93 - Pass (typSequence *) parameter instead of (char *). */

int NbMismatchs (long first, long last, long length, typSequence *SequencePtr)
{
  int i;
  int counter = 0;
  short int *sequence = SequencePtr->sequence;

  for (i = 0; i < length; i++)
    if (Mismatch ((int) BaseToPair [sequence[first + i] & NUCMASK]
                                   [sequence[last - i]  & NUCMASK]))
      counter++;

  return counter;
}

/* --------------------------- PartialEnergy () --------------------------- */

float PartialEnergy (unsigned char p1, unsigned char p2)
{
  if (Mismatch ((int) p1) || Mismatch ((int) p2))
    return 0.0;

  return 0.1 * Stacken[p1][p2];
}

/* ---------------------------- SimpleEnergy () --------------------------- */

/* Calculate the energy of an helix.

   15/02/93 - Pass (typSequence *) parameter instead of (char *). */

float SimpleEnergy (long first, long last, long length,
                    typSequence *SequencePtr)
{
  int i;
  short int *sequence = SequencePtr->sequence;
  float sum = 0.0;

  for (i = 0; i < length - 1; i++)
    sum += PartialEnergy (BaseToPair [sequence[first + i]     & NUCMASK]
                                     [sequence[last - i]      & NUCMASK],
                          BaseToPair [sequence[first + i + 1] & NUCMASK]
                                     [sequence[last - i - 1]  & NUCMASK]);

  return sum;
}
