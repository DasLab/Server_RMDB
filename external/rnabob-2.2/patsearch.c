/* patsearch.c
 * 
 * Contains the sequence expression compiler seqcomp()
 * and the sequence expression pattern searcher seqexec().
 *
 * NOTICE : This code is heavily borrowed/heavily modified from
 *          Henry Spencer's regular expression package.
 *          As such, it is hereby marked with Henry's copyright
 *          notice:
 *          
 *-------------------------------------------------------------------
 * regcomp and regexec
 *      Copyright (c) 1986 by University of Toronto.
 *      Written by Henry Spencer.  Not derived from licensed software.
 *
 *      Permission is granted to anyone to use this software for any
 *      purpose on any computer system, and to redistribute it freely,
 *      subject to the following restrictions:
 *
 *      1. The author is not responsible for the consequences of use of
 *              this software, no matter how awful, even if they arise
 *              from defects in it.
 *
 *      2. The origin of this software must not be misrepresented, either
 *              by explicit claim or by omission.
 *
 *      3. Altered versions must be plainly marked as such, and must not
 *              be misrepresented as being the original software.
 *
 * ------------------------------------------------------------------
 * 
 */


/* Two parts: compile and execute.
 * 
 * Compile turns a descriptor file into a compiled pattern-program.
 * Execute searches through a sequence using the pattern-program.
 * 
 * The pattern compiler reads a descriptor file, with a format
 * very similar to the "rnamot" RNA descriptor syntax of Gautheret,
 * Major, and Cedergren (CABIOS 6:325, 1990).
 * 
 * As stated above, the implementation of 'seqexec' is based upon Henry 
 * Spencer's regexp package, which forms the guts of the Perl's pattern 
 * searching. The algorithm loosely corresponds to a linear 
 * nondeterministic finite state machine. Everything I know about 
 * ND-FSM's comes from Henry's code, _Introduction to Automata 
 * Theory, Languages, and Computation_ (Hopcroft and Ullman, 1979), 
 * and _Algorithms_ (Sedgewick, 1983).
 *
 * The program consists of a linear series of nodes. Each node contains
 * a single simple pattern element, called an "atom". EXACTLY nodes 
 * contain a primary sequence atom which must match, within allowed
 * mismatch constraints. A GAP node is nondeterministic (the program
 * has two choices of the next node to search, rather than just one);
 * it is currently implemented in a way which permits 0 to gapmax
 * bases of any sequence. The END node signals the end of the pattern
 * and therefore implies its success.
 * 
 * A node may have instructions for the dynamic construction of
 * downstream nodes, allowing for patterns which specify relationships
 * (for instance, base complementarity) between positions. 
 * 
 * There are two kinds of atoms at each node. satom is the search
 * atom,  the exact pattern specified by the descriptor. catom is the
 * construct atom, a pattern constructed from satom and any active
 * correlations at this node (see above). 
 * 
 * 
 */



#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include "rnabob.h"
#include "rk.h"
#include "squid.h"


/* 
 * seqcomp and friends
 * 
 */
#define FAIL(m)  {paterror(m); exit (1);}
#define MAXLN    256
#define TOKENS   "SHR"
#define SEPS     " \t\n"
#define HELIXOPS "TGYR"
#define GAPSYM   '*'
#define OPEN_GAPSYM '['
#define CLOSE_GAPSYM ']'
#define COMMENTSYM '#'

/* The strategy -- yes, there is one -- is to build the pattern-program
 * on "scaffolding" in a tree-like data structure.
 * 
 * - Branches: s, H, R statements from the descriptor.
 *   
 * - Leaves:   parse EXACTLY's and GAP's from the branches
 * 
 * - Wee swinging monkeys: at each H', R' statement in the branches,
 *             go to the leaves and assign relpar pointers in an
 *             antiparallel fashion
 *             
 * - Raking: connect all the leaves into a linear pattern-program        
 * 
 * - Pruning: free the branches       
 */

typedef struct branch {
  char             *name;
  int               built;
  char             *pseudoatom;
  char              relop[5];
  struct branch    *relpar;
  int               smmat;
  struct leaf      *leaflist;
  struct branch    *nxt;
} Branch;

typedef struct leaf {
  Patnode         *node;
  struct leaf     *prv;
  struct leaf     *nxt;
} Leaf;


static int  linenumber;		/* keep track of position in desc. file */

static int  getline1(char *s,FILE *fp);
static void read_topology(FILE *descfp);
static void grow_branches(FILE *descfp);
static void validate_branches(void);
static void grow_leaves(void);
static Seqexp *connect_leaves(void);
static void free_branches(void );
static void add_optimization(Seqexp *sxp);

#ifdef DEBUG
static void dumpbranches(Branch *branchlist);
static void dumpleaves(Branch *branch);
static void dumpnode(Patnode *node);
static void writehash();
#endif


static Branch *brlist;

Seqexp *
seqcomp(FILE *descfp)
{
  Seqexp     *sxp;
#ifdef DEBUG
  Patnode *nodep;	
#endif
				/* paranoia */
  if (descfp == NULL)
    Die("No descriptor file");		
                                /* read the topology description and make
				 a skeleton for the branches */
  read_topology(descfp);		
				/* read the explicit descriptions and
				 fill out the branches */
  grow_branches(descfp);
				/* check that each branch got filled */
  validate_branches();
				/* break branches into their component atoms
				 and make the nodes */
  grow_leaves();
				/* link the nodes together, both in their 
				   linear order and in their correlations */
  sxp = connect_leaves();
				/* discard the supporting tree structure */
  free_branches();
				/* construct optimization code from long
				 stretches of primary seq constraint*/
  add_optimization(sxp);

#ifdef DEBUG
  printf("\nI have a complete Seqexp, sir.\n");
  printf("Here it is, for your viewing pleasure:\n");
  for (nodep = sxp->program; nodep != NULL; nodep = nodep->next)
    {
      dumpnode(nodep);
      printf("\n");
    }
  printf("Optimization codes:\n");
  /*  printf("seqmust is: ");  writehash(sxp->seqmust); */
  printf("\noffsmax is: %d\n", sxp->offsmax);
  printf("offsmin is: %d\n\n\n", sxp->offsmin);
#endif

				/* return the completed program */
  return(sxp);
}


static void
read_topology(FILE *descfp)
{
  char    buffer[MAXLN];	/* storage for the current line */
  Branch *brcurrent, *brlast;   /* tmp pointers for branch list */
  char   *nm;                   /* the name of a Branch */

				/* Get the first non-commented line. 
				   It contains the topology description. */
  linenumber = 0;
  if (! getline1(buffer, descfp))
    Die("Descriptor file looks empty");

				/* Use the topology description to
				   build the framework of the branches. */
  brlist = (Branch *) malloc (sizeof(Branch));
  brcurrent = brlist;
  nm = strtok(buffer, SEPS);
  while (nm != NULL)
    {
      if (strchr(TOKENS, *nm) == NULL) 
	Die("Invalid pattern element name %s on line %d", nm, linenumber);

      brcurrent->name = (char *) malloc (strlen(nm) + 1);
      strcpy(brcurrent->name, nm);
      brcurrent->built = 0;
      brcurrent->relpar = NULL;
      brcurrent->nxt = (Branch *) malloc (sizeof(Branch));
      brlast = brcurrent;
      brcurrent = brcurrent->nxt;
      nm = strtok(NULL, SEPS);
    }
  free(brcurrent);
  brlast->nxt = NULL;
}


static void
grow_branches(FILE *descfp)
{
  Branch  *brcurrent;		/* pointer to a Branch in the list */
  char     buffer[MAXLN];	/* storage for the current line */
  char    *nm;   		/* name of a Branch  */
  char    *mismat;		/* mismatch parameter(s), unparsed */
  char    *pattern;		/* pattern, unparsed */
  char    *relops;		/* relation matrix (R only), unparsed */
  char    *s;                   /* a tmp character pointer */
  int      mmleft, mmright;	/* parsed mismatch parameters */
  char relmatrix[5];		/* parsed relational matrix */
  int      warn;		/* counter to watch out for redundancies */
  
				/* Read the remaining lines, one at a time.
				 They are the "explicit descriptors", in a
				 form of "name mismat pattern [relops]" */
  while (getline1(buffer, descfp))
    {				/* deal with each line of the descriptor */
				/* parse the entire line */
      nm = strtok(buffer, SEPS);
      if (strchr(TOKENS, *nm) == NULL)
	Die("Invalid pattern element name %s on line %d", nm, linenumber);

      if ((mismat = strtok(NULL, SEPS)) == NULL) 
	Die("No mismatch parameters for element %s on line %d",	nm, linenumber);

      if ((pattern = strtok(NULL, SEPS)) == NULL) 
	Die("No pattern given for element %s on line %d", nm, linenumber);

      if ((*nm == 'R') && ((relops = strtok(NULL, SEPS)) == NULL)) 
	Die("No relational matrix for element %s on line %d", nm, linenumber);

      if ((s = strtok(NULL, SEPS)) != NULL) 
	Die("Don't know what to do with %s on line %d",	s, linenumber);

				/* parse the mismatch string */
      if (strchr(mismat, ':') != NULL)
	{
	  if (!isdigit(*(s = strtok(mismat, ":")))) 
	    Die("Invalid mismatch parameter %s for %s on line %d", s, nm, linenumber);

	  mmleft = atoi(s);
	  if (!isdigit(*(s = strtok(NULL, SEPS)))) 
	    Die("Invalid mismatch parameter %s for %s on line %d", s, nm, linenumber);

	  mmright = atoi(s);
	}
      else
	{
	  if (!isdigit(*mismat)) 
	    Die("Invalid mismatch parameter %s for %s on line %d", mismat, nm, linenumber);

	  mmleft = atoi(mismat);
	  mmright = -1;
	}


				/* For every branch of this name in the
				   skeleton built from topology descript, flesh
				   it out. If more than one branch has
				   this name, warn the user */
      warn = 0;
      for (brcurrent = brlist; brcurrent != NULL; brcurrent = brcurrent->nxt)
	{			/* deal with each branch */
	  if (strcmp(brcurrent->name, nm) != 0) 
	    continue;
	  switch (*nm) {
	  case 'S':
	    brcurrent->pseudoatom = (char *) malloc (strlen(pattern) +1);
	    strcpy(brcurrent->pseudoatom, pattern);
	    brcurrent->smmat = mmleft;
	    if (mmright != -1) 
	      Die("Too many mismatch params for %s on line %d", nm, linenumber);

	    brcurrent->built++;
	    break;

	  case 'R':
	    if (strlen(relops) != 4) 
	      Die("Faulty relation operator %s for %s on line %d", relops, nm, linenumber);

	    seqencode(relmatrix, relops);
				/* deliberate fall-through to next block */
	  case 'H':
	    {
	      Branch *rel;
	      char   *pat1, *pat2;
	      char   *relnm;

	      if ((strchr(pattern, ':') == NULL) || ((s = strtok(pattern, ":")) == NULL)) 
		Die("Bad pattern %s for %s on line %d",	s, nm, linenumber);

	      pat1 = s;

	      if ((s = strtok(NULL, ":\n")) == NULL) 
		Die("Bad pattern %s for %s on line %d", s, nm, linenumber);

	      pat2 = s;

	      if (mmright == -1) 
		Die("Need two mismatch params for %s on line %d", nm, linenumber);

	      brcurrent->pseudoatom = (char *) malloc (strlen(pat1) +1);
	      strcpy(brcurrent->pseudoatom, pat1);
	      brcurrent->smmat = mmleft;
	      brcurrent->built++;

	      if ((*nm == 'h') || (*nm == 'H'))
		seqencode(relmatrix, HELIXOPS);
	      
	      relnm = (char *) malloc (strlen(nm) + 2);
	      relnm = strcpy(relnm, nm);
	      relnm = strcat(relnm, "'");
	      for (rel = brcurrent->nxt; rel != NULL; rel = rel->nxt)
		{		/* deal with downstream relatives */
		  if (strcmp(rel->name, relnm) != 0)
		    continue;
		  rel->pseudoatom = (char *) malloc (strlen(pat2) + 1);
		  strcpy(rel->pseudoatom, pat2);
		  rel->smmat = mmright;
		  brcurrent->relpar = rel;
		  strcpy(brcurrent->relop, relmatrix);
		  rel->built++;
		}
	      free(relnm);
	    }
	    break;  

	  default:
	    Die("Corrupted name %s on line %d", nm, linenumber);
	  }
	  if (++warn > 1)
	    Warn("Multiple positions for %s on line %d\n", nm, linenumber);
	}
      
    }
}

static void
validate_branches()
{
  Branch *brcurrent;		/* pointer to a Branch in the list */

#ifdef DEBUG
  printf("\nBranch construction completed:\n\n");
  dumpbranches(brlist);
#endif

  for (brcurrent = brlist; brcurrent != NULL; brcurrent = brcurrent->nxt)
    {
      if (brcurrent->name == NULL) 
	Die("internally corrupted structure - try a re-run");
      if ((!brcurrent->built) || (brcurrent->pseudoatom == NULL)) 
	Die("internal difficulties with %s", brcurrent->name);
    }
}


static void
grow_leaves()
{
  Branch *brcurrent;		/* pointer to a Branch in the list */
  Leaf   *leafp, *oldleaf;	/* working leaf pointers */
  int     n;			/* counter for measuring atom length */
  char   *atom;			/* parsed atom from pattern */
  char   *s, *s1;		/* tmp character pointers */
  struct parenttype *pa;	/* tmp Parent pointer */

  for (brcurrent = brlist; brcurrent != NULL; brcurrent = brcurrent->nxt)
    {				/* for each branch */
      brcurrent->leaflist = (Leaf *) malloc (sizeof(Leaf));
      leafp = brcurrent->leaflist;
      leafp->prv = NULL;
      s = brcurrent->pseudoatom;
      while (*s != '\0')
	{			/* until the pattern has been dissected */
	  leafp->node = (Patnode *) malloc (sizeof(Patnode));
	    
	  if (strchr(NUCLEOTIDES, *s) != NULL)
	    {			/* EXACTLY atom */
	      n = 0; 
	      s1 = s;
	      while ((*s1 != '\0') &&
		     (strchr(NUCLEOTIDES, *s1) != NULL))
		{
		  s1++;
		  n++;
		}
	      atom = (char *) malloc (n + 1);
	      strncpy(atom, s, n);
	      atom[n] = '\0';
	      s = s1;

	      leafp->node->opcode = EXACTLY;
	      leafp->node->satom  = (char *) malloc (strlen(atom)+1);
	      seqencode(leafp->node->satom, atom);
	      leafp->node->catom  = (char *) malloc (strlen(atom)+1);
	      strcpy(leafp->node->catom, leafp->node->satom);
	      leafp->node->fatom   = NULL;
	      leafp->node->relpar = NULL;
	      leafp->node->gapmax = 0;
	      leafp->node->clen   = strlen(leafp->node->satom);
	      leafp->node->smmat  = brcurrent->smmat;
	    }
	  else if (*s == GAPSYM)
	    {			/* GAP atom */
	      n = 0;
	      while (*s == GAPSYM)
		{
		  n++;
		  s++;
		}
	      
	      leafp->node->opcode = GAP;
	      leafp->node->satom  = (char *) malloc (n + 1);
	      leafp->node->catom  = (char *) malloc (n + 1);
	      leafp->node->fatom  = NULL;
	      leafp->node->clen   = n;
	      leafp->node->gapmax = n;
	      *(leafp->node->satom + n) = NTEND;
	      while (--n >= 0)
		*(leafp->node->satom + n) = NTN;
	      strcpy(leafp->node->catom, leafp->node->satom);
	      leafp->node->relpar = NULL;
	      leafp->node->smmat  = brcurrent->smmat;
	    }
	  else if (*s == OPEN_GAPSYM)
	    {
	      s++;
	      n = 0;
	      while (*s != CLOSE_GAPSYM)
		{
		  if (isdigit(*s))
		    n = n*10 + (*s - '0');
		  s++;
		}
	      s++;

	      leafp->node->opcode = GAP;
	      leafp->node->satom  = (char *) malloc (n + 1);
	      leafp->node->catom  = (char *) malloc (n + 1);
	      leafp->node->fatom  = NULL;
	      leafp->node->clen   = n;
	      leafp->node->gapmax = n;
	      *(leafp->node->satom + n) = NTEND;
	      while (--n >= 0)
		*(leafp->node->satom + n) = NTN;
	      strcpy(leafp->node->catom, leafp->node->satom);
	      leafp->node->relpar = NULL;
	      leafp->node->smmat  = brcurrent->smmat;


	    }
	  else
	    Die("Invalid character %c in pattern %s for %s",
		*s, brcurrent->pseudoatom, brcurrent->name);

	  
				/* all leaves on a branch share the same 
				 mismatch constraints. Go back and record 
				 all previous leaves on this branch as 
				 "match parents" */
	  leafp->node->matchpar = NULL;
	  for (oldleaf = leafp->prv; oldleaf != NULL; oldleaf = oldleaf->prv)
	    {
	      pa = leafp->node->matchpar;
	      leafp->node->matchpar = (struct parenttype *) 
		malloc (sizeof(struct parenttype));
	      leafp->node->matchpar->nextpar = pa;
	      leafp->node->matchpar->ptr = oldleaf->node;
	    }
	  
				/* all leaves on a branch inherit the 
				 relational matrix of the branch */
	  if (brcurrent->relpar != NULL)
	    strcpy(leafp->node->relop, brcurrent->relop);

	  leafp->nxt = (Leaf *) malloc (sizeof(Leaf));
	  oldleaf = leafp;
	  leafp = leafp->nxt;
	  leafp->prv = oldleaf;
	}
      free(oldleaf->nxt);
      oldleaf->nxt = NULL;
    }
  

#ifdef DEBUG
  printf("Leaf construction complete.\n\n");
  for (brcurrent = brlist; brcurrent != NULL; brcurrent = brcurrent->nxt)
    {
      printf("Dumping leaves from Branch %s\n", brcurrent->name);
      dumpleaves(brcurrent);
    }
#endif

}

static Seqexp *
connect_leaves()
{
  Branch *brcurrent;		/* pointer to a Branch in the list */
  Leaf   *fwdp, *bckp;		/* working pointers for leaves */
  Leaf   *leafp;		/* working pointer for a leaf list */
  Seqexp *sxp;			/* pointer to the start of the seqexp */
  Patnode *nodep;		/* tmp pointer to a pattern node */

				/* connect related leaves */
  for (brcurrent = brlist; brcurrent != NULL; brcurrent = brcurrent->nxt)
    {
      if (brcurrent->relpar == NULL)
	continue;
      
      for (bckp = brcurrent->leaflist; bckp->nxt != NULL; bckp = bckp->nxt)
	;
      fwdp = brcurrent->relpar->leaflist;

      while ((fwdp != NULL) && (bckp != NULL))
	{
	  bckp->node->relpar = (struct parenttype *) 
	    malloc (sizeof(struct parenttype));
	  bckp->node->relpar->ptr = fwdp->node;
	  bckp->node->relpar->nextpar = NULL;
	  strcpy(bckp->node->relop, brcurrent->relop);
	  fwdp->node->opcode = RELATION;
	  fwdp = fwdp->nxt;
	  bckp = bckp->prv;
	}

      if ((fwdp != NULL) || (bckp != NULL))
	Die("Pattern atom number mismatch between related strings");
    }

				/* relpars are all set */
				/* Next, rake the leaves together into
				   a single linear list */
  sxp = (Seqexp *) malloc (sizeof(Seqexp));
  sxp->program = brlist->leaflist->node;
  nodep = NULL;
  for (brcurrent = brlist; brcurrent != NULL; brcurrent = brcurrent->nxt)
    {
      for (leafp = brcurrent->leaflist; leafp != NULL; leafp = leafp->nxt)
	{
	  if (nodep != NULL)
	    nodep->next = leafp->node;
	  nodep = leafp->node;
	}
    }
				/* terminate the list */
  nodep->next = (Patnode *) malloc (sizeof(Patnode));
  nodep->next->opcode = END;
  nodep->next->next   = NULL;

#ifdef DEBUG
  printf("Leaf connection complete.\n\n");
  for (brcurrent = brlist; brcurrent != NULL; brcurrent = brcurrent->nxt)
    {
      printf("Dumping leaves from Branch %s\n", brcurrent->name);
      dumpleaves(brcurrent);
    }
#endif

 return(sxp);
}

static void 
free_branches()
{
  Branch *brcurrent;		/* pointer to a Branch in the list */
  Branch *oldbr;
  Leaf   *leafp;		/* tmp pointer to a leaf */
  Leaf   *oldleaf;

  brcurrent = brlist;
  while (brcurrent != NULL)
    {
      leafp = brcurrent->leaflist;
      while (leafp != NULL) {
	oldleaf = leafp;
	leafp = leafp->nxt;
	free(oldleaf);
      }

      oldbr = brcurrent;
      brcurrent = brcurrent->nxt;
      free(oldbr->name);
      free(oldbr->pseudoatom);
      free(oldbr);
    }
}

static void
add_optimization(Seqexp *sxp)
{
  Patnode    *node;
  char       *growprimary;
  char       *head_growprimary;	/* keep track of head of growprimary, for free'ing */
  int         growlength;
  char       *bestprimary;
  int         bestpos, pos;
  int         bestscore,score;
  int         bestlength;
  int         i;
  int         maxmindiff, bestmmdiff;

  growprimary = NULL;
  growlength  = 0;
  bestprimary = (char *) malloc (RK_HASHSIZE + 1);
  bestscore   = 0;
  bestpos     = 0;
  pos         = 0;
  maxmindiff  = 0;
  for (node = sxp->program; node != NULL; node = node->next)
    {
      if ((node->opcode == EXACTLY) &&
	  (node->smmat == 0))
	{
	  growlength += node->clen;
	  if (growprimary == NULL)
	    {
	      growprimary = (char *) malloc (growlength + 1);
	      *growprimary = NTEND;
	    }
	  else 
	    growprimary = (char *) realloc (growprimary, growlength + 1);
	  strcat(growprimary, node->satom);
	  pos += node->clen;
	}
      else 
	{
	  head_growprimary = growprimary;
	  if (growprimary != NULL)
	    {
	      while (growlength > 0)
		{
		  score = 0;
		  for (i = 0; ((i < RK_HASHSIZE) && (i < growlength)); i++)
		    if (*(growprimary + i) != NTN)
		      score++;
		  if (score > bestscore)
		    {
		      bestscore = score;
		      bestlength = (int)((RK_HASHSIZE <= growlength)? RK_HASHSIZE : growlength);
		      memcpy(bestprimary, growprimary, bestlength);
		      bestpos   = pos - growlength;
		      bestmmdiff= maxmindiff;
		    }
		  growprimary ++;
		  growlength--;
		}
	      free(head_growprimary);
	      growprimary = NULL;
	      growlength = 0;
	    }
	  maxmindiff += node->gapmax;
	  if (node->opcode != GAP)
	    pos += node->clen;
	  else
	    pos += node->gapmax;

	}
    }
	  
  if (bestscore >= RK_REQUIRE)
    {
      for (i = 0; i < bestlength; i++)
	{
	  sxp->seqmust <<= 4;
	  sxp->seqmust |=  *bestprimary;
	  bestprimary++;
	}
      while (bestlength < RK_HASHSIZE)
	{
	  sxp->seqmust <<= 4;
	  sxp->seqmust |=  NTN;
	  bestlength++;
	}
      sxp->offsmax = bestpos;
      sxp->offsmin = bestpos - bestmmdiff;
    }
  else
    sxp->seqmust = 0;

}



/* Function: getline1()
 * 
 * Purpose:  Get next non-blank, non-comment line and put it in s,
 *           which is pre-allocated. Ignore everything on a line 
 *           after a comment.
 *           
 */
static int
getline1(char *s,		/* allocated string memory */
	FILE *fp)		/* open file */
{
  char buffer[MAXLN];	        /* tmp storage for a line */
  char *sptr;			/* pointer to position in s */
  int   saw_something;

  while (1)
    {

      if (fgets(buffer,MAXLN,fp) == NULL) return 0;
      linenumber++;		/* external; debugging aid for user */
      saw_something = 0;
      for (sptr = buffer; *sptr; sptr++)
	{
	  if (islower(*sptr)) *sptr = toupper(*sptr);

	  if (*sptr == COMMENTSYM)
	    {
	      *sptr = '\0';
	      break;
	    }
	  
	  else if (! isspace(*sptr))
	    saw_something = 1;
	}

      if (saw_something)
	{
	  strcpy(s, buffer);
	  return 1;
	}


    }
  /*NOTREACHED*/
}

	    	    




/* 
 * seqexec and friends
 *
 * seqexec returns a Position of the first match found in the
 * sequence. The actual pattern which matched will be stored in
 * the Patnodes of the pattern program, and can be dug out by
 * the caller. The caller must re-call seqexec if it wants more
 * than the first match.
 */


				/* global work variables for seqexec */
static char     *seqinput;

				        /* function declarations */
static int       seqmatch(Patnode *pat);/* main matching switch block */
static int       dynamize(Patnode *pat);/* dynamic node constructor */

int
seqexec(Seqexp     *prog,
	char       *sequence)
{
  int ptr;
  int prime;
  int leftpos;
  int rightpos;
				/* be paranoid */
  if ((prog == NULL) || (sequence == NULL) || (prog->program == NULL)) 
    Die("NULL parameter");

				/* off we go, sweeping across the seq */
  ptr = 0;
  seqinput = sequence;
  if (prog->seqmust)		/* optimization ON */
    {
      do {
	if ((prime = (int) rkseq(prog->seqmust, seqinput)) == -1)
	  return(-1);
	leftpos = (((prime - prog->offsmax) < 0)? 0 :(prime - prog->offsmax));
	rightpos = (((prime - prog->offsmin) < 0)? 0 :(prime - prog->offsmin));
	ptr += leftpos;
	for (; ptr <= ptr + rightpos; ptr++)
	  {
	    if ((*(seqinput = sequence + ptr)) == NTEND)
	      return (-1);
	    if (seqmatch(prog->program))
	      return ptr; 
	  }
      } while (*(seqinput = sequence + (++ptr)) != NTEND);
    }
  else				/* hard case: no primary sequence constraint */
    {

      do {
	if (seqmatch(prog->program))
	  return ptr;		/* Success! */
      } while (*(seqinput = sequence + (++ptr)) != NTEND);
    }
  return(-1);			/* Failure. */
}


static int
seqmatch(Patnode *pat)
{
  Patnode *scan;
  int      cmismat, fmismat;	
  struct parenttype *par;
  
  scan = pat;
  while (scan != NULL)
    {
				/* count how many mismatches will be
				 allowed at this node */
      if (scan->opcode != END)
	{
	  cmismat = scan->smmat;
	  par = scan->matchpar;
	  while (par != NULL)
	    {
	      cmismat -= par->ptr->fmmat;
	      par = par->nextpar;
	    }
	}

				/* main matching switch block */
      switch (scan->opcode) {
      case EXACTLY: {
	 char *opnd;

	opnd = scan->catom;
	if ((cmismat == 0) &&	/* inline the first base if you're sure */
	    (!(ntmatch(*opnd, *seqinput))))
	  return(0);
	if (scan->clen > 1)
	  fmismat = seqncmp(opnd, seqinput, scan->clen, cmismat);
	else
	  fmismat = 0;
	if (fmismat > cmismat)
	  return(0);
	scan->fatom = seqinput;
	seqinput += scan->clen;
	scan->fmmat = fmismat;
	scan->flen  = scan->clen;
	if (scan->relpar != NULL)
	  dynamize(scan);
      }
	break;
      case GAP: {
	 char nextnt;
	 int no;
	char  *save;
				/* Lookahead to avoid useless match attempts
				   when we know what nuc comes next */
	if (scan->next->opcode == END)
	  return(1);
	else if ((scan->next->opcode == EXACTLY) &&
		 (scan->next->smmat == 0))
	  nextnt = *(scan->next->catom);
	else
	  nextnt = NTN;

	save = seqinput;
	no = 0;
	while (no <= scan->gapmax)
	  {
	    seqinput = save + no;
	    if (*seqinput == '\0') break; 
	    if (ntmatch(nextnt, *seqinput))
	      {
		scan->fatom = save;
		scan->flen = no;
		scan->fmmat = 0;
		if (scan->relpar != NULL)
		  dynamize(scan);
		if (seqmatch(scan->next))
		  return (1);
	      }
	    no++;
	  }
	seqinput = save;
	return(0);
      }
      case RELATION:
	Die("Reached an unconstructed node");
	return(0);
      case END:
	return(1);			/* Success! */
      default:
	Die("memory corruption");
	return(0);
      }
      scan = scan->next;
    }
				/* we only get here if there's trouble;
				 normally 'case END' is the terminating point*/
  Die("corrupted pointers");
  return(0);
}


static int 
dynamize(Patnode *node)			/*  construction of catom */
{
  Patnode    *target;
  char       *aphelix;
  char       *superced;
  char        relator;

  int     i;

  if ((node == NULL) || (node->fatom == NULL)) 
    Die("corrupted node passed to dynamize()");
    

  target = node->relpar->ptr;	/* there can be only one parent,
				 in this implementation */
  aphelix = target->catom;
				/* Write the node's catom. Important:
				 this is done in an ANTIPARALLEL fashion.
				 Most correlations are going to be anti-
				 parallel double helices. */
  if ((node->opcode == GAP) &&
      (node->flen == 0))
    {
      target->opcode = GAP;
      target->gapmax = 0;
      target->flen   = 0;
    }
  else
    {
      target->opcode = EXACTLY;
      target->clen   = node->flen;
      superced = target->satom;
      for (i = node->flen -1; i >= 0; i--) 
	{
	  switch (*((node->fatom)+i)) {
	  case NTA:
	    relator = node->relop[0];
	    break;
	  case NTC:
	    relator = node->relop[1];
	    break;
	  case NTG:
	    relator = node->relop[2];
	    break;
	  case NTT:
	    relator = node->relop[3];
	    break;
	  default:
	    relator = NTN;	/* behavior undefined. Attempt to continue. */
	    break;
	  }
	  if ((*aphelix = relator & *superced) == NTEND)
	    *aphelix = *superced;
	  aphelix++;
	  superced++;
	}
      *aphelix = NTEND;
    }

      

      

#ifdef DEBUG
  printf("looking for a constructed atom: ");
  puts(target->catom); 
#endif
  return(1);
}


#ifdef DEBUG
static void
dumpbranches(Branch *branchlist)
{
  Branch *brp;
  int n = 0;

  for (brp = branchlist; brp != NULL; brp = brp->nxt)
    {
      printf("Branch #%d\n", ++n);
      printf("\tname: %s\n", brp->name);
      printf("\tbuilt?: ");
      if (brp->built)
	printf("yes\n");
      else
	printf("NO\n");
      printf("\tpseudoatom: %s\n", brp->pseudoatom);
      if (brp->relpar != NULL)
	{
	  printf("\tRelated to %s\n", brp->relpar->name);
	  printf("\trelops: %s\n", brp->relop);
	}
      else
	printf("\tNot related to other sequence\n");
      printf("\tmismatches: %d\n", brp->smmat);
    }
}
    
static void
dumpleaves(Branch *branch)
{
  Leaf *leafp;
  int n = 0;

  for (leafp = branch->leaflist; leafp != NULL; leafp = leafp->nxt)
    {
      printf("\tLeaf #%d\n", ++n);
      dumpnode(leafp->node);
    }
}

static void
dumpnode(Patnode *node)
{
  printf("\topcode: ");
  switch (node->opcode) {
  case EXACTLY:
    printf("EXACTLY\n");
    break;
  case GAP:
    printf("GAP\n");
    break;
  case RELATION:
    printf("RELATION\n");
    break;
  case END:
    printf("END\n");
    return;
  default:
    printf("UNDEFINED\n");
  }
      
  printf("\tsatom: ");
  if (node->satom == NULL)
    printf(" not addressed\n");
  else if (strlen(node->satom) == 0)
    printf(" addressed but empty\n");
  else
    puts(node->satom);

  printf("\tcatom: ");
  if (node->catom == NULL)
    printf(" not addressed\n");
  else if (strlen(node->catom) == 0)
    printf(" addressed but empty\n");
  else
    puts(node->catom);

  printf("\tclen:   %d\n", node->clen);
  printf("\tgapmax: %d\n", node->gapmax);

  printf("\trelops: ");
  if (strlen(node->relop) == 0)
    printf("none\n");
  else
    puts(node->relop);

  if (node->relpar != NULL)
    {
      printf("\t this sequence is related to another node:  {\n");
      dumpnode(node->relpar->ptr);
      printf("\t}");
    }
	
  printf("\tmismatches %d\n", node->smmat);
}
#endif	/* DEBUG */


