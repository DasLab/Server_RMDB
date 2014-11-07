/*****************************************************************
 * @LICENSE@
 *****************************************************************/

/* sre_ctype.c
 * 
 * For portability. Some systems have functions tolower, toupper
 * as macros (for instance, MIPS M-2000 RISC/os!)
 * 
 * RCS $Id: sre_ctype.c,v 1.2 1998/10/09 18:07:16 eddy Exp eddy $
 */

#include <ctype.h>
#include "squid.h"

#ifdef MEMDEBUG
#include "dbmalloc.h"
#endif

int
sre_tolower(int c)
{
  if (isupper(c)) return tolower(c);
  else return c;
}

int
sre_toupper(int c)
{
  if (islower(c)) return toupper(c);
  else return c;
}

