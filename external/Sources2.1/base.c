/* ------------------------------------------------------------------------
   Base.c
   ------

     Functions that support bases manipulation. */

/* ------------------------------- Includes ------------------------------- */

#include "rnamot.h"

/* --------------------------- Global variables --------------------------- */

/* Array of base mask complement values. The values in the right comments
   indicate the corresponding original mask values.

   22/01/93 - Creation.
   07/02/93 - Use pre-constructed base masks. */

char Complement [16] =
  {0,
   BASE_U,	/* A                 */
   BASE_G,	/* C                 */
   BASE_K,	/* M (A | C)         */
   BASE_C,	/* G                 */
   BASE_Y,      /* R (G | A)         */
   BASE_S,      /* S (G | C)         */
   BASE_B,      /* V (G | C | A)     */
   BASE_A,      /* U                 */
   BASE_W,      /* W (U | A)         */
   BASE_R,      /* Y (U | C)         */
   BASE_D,      /* H (U | C | A)     */
   BASE_M,      /* K (U | G)         */
   BASE_H,      /* D (U | G | A)     */
   BASE_V,      /* B (U | G | C)     */
   BASE_N};     /* N (U | G | C | A) */

/* ----------------------------- BaseToMask () ---------------------------- */

/* Function that translates a base character into the correct base mask.

   15/12/92 - Creation.
   07/02/93 - Use pre-constructed base masks. */

int BaseToMask (int c)
{
  switch (toupper (c))
  {
    case 'A': return BASE_A;
    case 'C': return BASE_C;
    case 'G': return BASE_G;
    case 'U':
    case 'T': return BASE_U;
    case 'M': return BASE_M;
    case 'R': return BASE_R;
    case 'W': return BASE_W;
    case 'S': return BASE_S;
    case 'Y': return BASE_Y;
    case 'K': return BASE_K;
    case 'V': return BASE_V;
    case 'H': return BASE_H;
    case 'D': return BASE_D;
    case 'B': return BASE_B;
    case 'X':
    case 'N': return BASE_N;
  }

  return 0;
}

/* ----------------------------- MaskToBase () ---------------------------- */

/* Function that translates a base mask in the correct base character.

   15/12/92 - Creation.
   16/12/92 - Optimization.
   07/02/93 - Use pre-constructed base masks.
   11/02/93 - Be sure to filtrate special bits in nucleotides. */

char MaskToBase (char c)
{
  switch ((int) c & NUCMASK)
  {
    case BASE_A: return 'A';
    case BASE_C: return 'C';
    case BASE_M: return 'M';
    case BASE_G: return 'G';
    case BASE_R: return 'R';
    case BASE_S: return 'S';
    case BASE_V: return 'V';
    case BASE_U: return 'U';
    case BASE_W: return 'W';
    case BASE_Y: return 'Y';
    case BASE_H: return 'H';
    case BASE_K: return 'K';
    case BASE_D: return 'D';
    case BASE_B: return 'B';
    case BASE_N: return 'N';
  }

  return ' ';
}

/* ------------------------------ NbBases () ------------------------------ */

/* Function that returns the number of bases corresponding to a base mask.

   16/12/92 - Creation.
   07/02/93 - Use pre-constructed base masks.
   11/02/93 - Be sure to filtrate special bits in nucleotides. */

int NbBases (char c)
{
  switch ((int) c & NUCMASK)
  {
    case BASE_N: return 4;

    case BASE_V:
    case BASE_H:
    case BASE_D:
    case BASE_B: return 3;

    case BASE_M:
    case BASE_R:
    case BASE_S:
    case BASE_W:
    case BASE_Y:
    case BASE_K: return 2;

    case BASE_A:
    case BASE_C:
    case BASE_G:
    case BASE_U: return 1;
  }

  return 0;
}
