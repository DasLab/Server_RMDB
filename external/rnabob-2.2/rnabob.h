/* rnabob.h
 * 
 * Header file for all of RNABOB.
 * 
 */

#ifndef RELEASE
#define RELEASE     "2.2"
#define RELEASEDATE "March 1999"
#endif

#include <stdio.h>
#include "rk.h" 

typedef struct pattype {
  int                opcode;	/* Type of node */
  char              *satom;     /* saved atom: Atom constraints */
  char              *catom;     /* construct atom: Post-construction, 
				   atom to search for */
  char              *fatom;	/* found atom: Actual string which matches */
  int                gapmax;	/* maximum length of a GAP */
  int                relation;	/* Dynamically construct this atom?  */
  char               relop[5];	/* Instruction array for dynamic construct */
  struct parenttype *relpar;    /* Reference node for dynamic construct */
  int                smmat;	/* saved mismatches: mismatch no. allowed
				   at this node */
  struct parenttype *matchpar;  /*  ...less the mismatches already occurring
				    in this parent list equals the number
				    of mismatches allowed */
  int                fmmat;     /* found mmat: actual no. of mismatches found
				   at this node */
  int                clen;      /* construct length; gapmax for gaps, atom
				   length for EXACTLYs */
  int                flen;      /* found length: actual length found at this 
				   node */
  struct pattype     *next;     /* next node in the automaton */
} Patnode;

struct parenttype {
  Patnode            *ptr;
  struct parenttype  *nextpar;
};


typedef struct seqexp {
  Patnode *program;
				/* Optimizations. Seqmust must appear
				 within offsmin to offsmax nucs of the
				 start position of a match. Allows a
				 big primary sequence constraint to
				 be included, for ultra-speed. */
				/* Not implemented yet :) */
  Hashseq    seqmust;
  int        offsmin;
  int        offsmax;
} Seqexp;





/* definition   number     opnd?   meaning */
#define END       0      /* no     End of compiled pattern */		
#define EXACTLY   1      /* seq    Match this sequence string */
#define GAP       2      /* none   Match any nucleotide up to gapmax times */
#define RELATION  3      /* seq    dynamically construct this atom from
			           correlated atom in relpar, using
				   transformation instructions in relop[]
				   and superceding instructions in operand */

extern Seqexp   *seqcomp(FILE *descfp);
extern int       seqexec(Seqexp *prog, char *sequence);

