/* ------------------------------------------------------------------------
   Rnamot.h
   --------

     Constant declarations, type definitions and prototypes of all functions
   used in the Rnamot software. */


#include <stdio.h>
#include <stdlib.h>

/* ------------------------------ Constants ------------------------------- */

#define	OK	1
#define	BUG	0
#define	TRUE	1
#define	FALSE	0

/* File Format */
#define NONE		0
#define FASTA           1
#define GENBANK         2

/* Possible modes of use for Rnamot */
#define	SEARCH		1
#define	ALIGNMENT	2

/* Default length of a sequence buffer */
#define	BUFFERLENGTH	50000

/* Default maximum number of wobbles allowed */
#define	MAXWOBBLES	1000000

/* Default maximum number of mismatchs allowed */
#define	MAXMISMATCHS	1000000

/* Initial score value for a grid */
#define	INITIALSCORE	10000.0

/* Score for a non restrictive pattern not found */
#define	PATNOTFOUND	100.0

/* Score for a SE having no restrictive pattern of for a non-restrictive
   pattern not found in the sequence */
#define	NULLPATSCORE	0.0

/* Base values (IUAC-IUB standard notation) */
#define	BASE_A	1
#define	BASE_C	2
#define	BASE_M	3
#define	BASE_G	4
#define	BASE_R	5
#define	BASE_S	6
#define	BASE_V	7
#define	BASE_U	8
#define	BASE_T	8
#define	BASE_W	9
#define	BASE_Y	10
#define	BASE_H	11
#define	BASE_K	12
#define	BASE_D	13
#define	BASE_B	14
#define	BASE_X	15
#define	BASE_N	15

/* Mask for a nucleotide in the sequence */
#define	NUCMASK	0x000f

/* Comparaison macros */
#define	min(a,b)	(a < b) ? a : b
#define	max(a,b)	(a > b) ? a : b

/* --------------------------- Type definitions --------------------------- */

/* A boolean value */
typedef unsigned char boolean;

/* A stem location */
typedef struct
{
  boolean firstseen;              /* The first stem has been seen? */
  int pos1;                       /* Position of first stem in template */
  int pos2;                       /* Position of second stem in template */
  long maxwidth;                  /* Maximal width of the helix */
} typStemLoc;

/* An interval */

typedef struct
{
  long min;
  long max;
} typInterval;

/* A structural element */
typedef struct
{
  char type;                      /* Type H (stem) or S (single-strand) */
  boolean described;              /* Has been described? */
  boolean strict;                 /* Contains a strict pattern? */
  boolean prioritymember;         /* Member of priority list? */
  char *pattern;                  /* Restrictive pattern */
  typInterval length;             /* Min and max length */
  int nb;                         /* Identificator for this SE */
  int secondstemnb;               /* Index of 2nd stem if type == H */
  int maxfaults;                  /* Maximum faults allowed */
  int patlength;                  /* Length of a restrictive pattern */
  float patprob;                  /* Probability to find a res. pattern */
  char probflag;                  /* Probability has been calculated? */
} typSE;

/* A motif */
typedef struct
{
  boolean countSEdone;            /* Count of SE has been made? */
  char *name;                     /* Name of the motif file */
  int nbS;                        /* Number of single-strands */
  int nbH;                        /* Number of stems */
  int nbSE;                       /* Total number of structural elements */
  int maxmismatchs;               /* Maximum number of mismatchs allowed */
  int maxwobbles;                 /* Maximum number of wobbles allowed */
  int nbpriority;                 /* Nb of elements in priority order array */
  int nbbestpriority;             /* Nb of elements in best priority array */
  int *priority;                  /* Priority order array */
  int *bestpriority;              /* Best priority order array */
  int maxmark;                    /* Maximum number of SE to mark */
  typInterval *disttab;           /* Array of distances between SE */
  typSE *template;                /* Array of structural elements */
  typStemLoc *stems;              /* Array of stem locations */
} typMotif;

/* A memory buffer (for dynamic sequence reading and allocation) */
typedef struct Buffer
{
  long length;                    /* Length of sequence in that buffer */
  char *sequence;                 /* Sequence */
  struct Buffer *next;            /* Next memory buffer */
} typBuffer;

/* A sequence */
typedef struct
{
  char *name;                     /* Name of the sequence file */
  char *commentary;               /* Information comment on a sequence */
  short int *sequence;            /* The sequence itself */
  FILE *fsequence;                /* Sequence file */
  long bufferlength;              /* Maximum length of a buffer */
  int nbsequences;                /* Total number of sequences read */
  int totnucleotides;             /* Total number of nucleotides scanned */
  int totmatches;                 /* Total number of matches (ALL seq.) */
  int nbbuffers;                  /* Number of buffers in list */
  boolean scanzoneok;             /* Interval of 1st SE to scan entered? */
  boolean complemented;           /* Sequence is complemented? */
  long scanfirst;                 /* First value of 1st SE's interval */
  long scanlength;                /* Length of interval scanned for 1st SE */
  long length;                    /* Length of the sequence */
  long lastout;                   /* Last position displayed */
  typBuffer *lastbuffer;          /* Last buffer in list */
  typBuffer *bufferlist;          /* List of buffers in sequence reading */
} typSequence;

/* A SE occurance in the sequence */
typedef struct
{
  long first;                     /* Starting position of the interval */
  long last;                      /* Ending position of the interval */
  long pos;                       /* Position of an helix for alignment */
  long pospat;                    /* Position of a restrictive pattern */
  long length;                    /* Length of the interval */
  long left;                      /* Index of left neighbour in the grid */
  long right;                     /* Index of right neighbour in the grid */
} typStrand;

/* A grid */
typedef struct
{
  int size;                       /* Number of elements */
  boolean saved;                  /* That grid has been saved? */
  boolean solution;               /* That grid is a solution? */
  float score;                    /* Score */
  int mismatchs;                  /* Total number of mismatchs */
  int wobbles;                    /* Total number of wobbles */
  typStrand *strands;             /* Interval elements */
} typGrid;

/* A list of grids */
typedef struct typGridList
{
  typGrid info;                   /* A grid */
  struct typGridList *next;       /* Next element in the list */
} typGridList;

/* A solution */
typedef struct
{
  FILE *fsol;                     /* Optimal solution file */
  FILE *falt;                     /* Alternative solutions file */
  int nbsols;                     /* Number of non-alternative solutions for
                                     one sequence */
  int nbalts;                     /* Number of alternative solutions for one
                                     sequence */
  int totsols;                    /* Total number of non-alt. matchs (ALL) */
  int totalts;                    /* Total number of alt. matchs (ALL seq.) */
  typGrid *bestgrid;              /* Best grid found */
  typGrid *bestfault;             /* Fault solution nearest to a good one */
  typGridList *gridlist;          /* List of grids in solution */
  char *solname;                  /* Name of optimal solution file */
  char *altname;                  /* Name of alternative solutions file */
} typSolution;

/* ------------------------------ Prototypes ------------------------------ */

/* Base.c */

int BaseToMask (int c);
char MaskToBase (char c);
int NbBases (char c);

/* Energy.c */
int Mismatch (int value);
int NbMismatchs (long first, long last, long length, typSequence *SequencePtr);
float PartialEnergy (unsigned char p1, unsigned char p2);
float SimpleEnergy (long first, long last, long length, typSequence *SequencePtr);

/* Grid.c */
void AdjustIntervals (typGrid *GridPtr, typMotif *MotifPtr,
                      int posgrid1, int posgrid2, int solution);
void CopyGrid (typGrid *GridSrc, typGrid *GridDst);
typGrid *CreateGrid (typMotif *MotifPtr);
void FillHoles (typGrid *GridTemp, typMotif *MotifPtr);
void FillStrands (typGrid *GridTemp, typMotif *MotifPtr);
void FreeGrid (typGrid *GridPtr);
int GridCmp (typMotif *MotifPtr, typGrid *GridA, typGrid *GridB);
void GridMismatchs (typGrid *GridTemp, typMotif *MotifPtr,
                    typSequence *SequencePtr);
float GridScore (typGrid *GridTemp, typMotif *MotifPtr,
                 typSequence *SequencePtr);
float HelixScore (int stem1, int stem2, typGrid *GridTemp, typMotif *MotifPtr,
                  typSequence *SequencePtr);
void PutStrand (typGrid *GridPtr, int posgrid, long posinf, long possup,
                int posupdate);
void SaveGrid (FILE *f, typGrid *GridTemp, typMotif *MotifPtr,
               typSequence *SequencePtr);
int StrandIsNull (typStrand Strand);
void TraceGrid (typGrid *GridPtr);
void TraceGrids (typSolution *SolutionPtr);
void UpdateLeft (typGrid *GridPtr, typMotif *MotifPtr, int posSE);
void UpdateRight (typGrid *GridPtr, typMotif *MotifPtr,
                  typSequence *SequencePtr, int posSE);

/* Motif.c */
void BestOrder (typMotif *MotifPtr);
void DistanceArray (typMotif *MotifPtr);
int FindSingleStrand (int SEnumber, typMotif *MotifPtr);
void FreeMotif (typMotif *MotifPtr);
int InitializeMotif (char *motifname, typMotif *MotifPtr);
void PatternProbs (typMotif *MotifPtr);
int ReadMotif (typMotif *MotifPtr);
int ReadSEPattern (typMotif *MotifPtr, FILE *fmotif, int pos1, int pos2);
int SkipCommentLines (FILE *f);
void TraceMotif (typMotif *MotifPtr);

/* Rnamot.c */
void Goodbye (int value);
int ParseArgs (int argc, char **argv);

/* Scan.c */
int Alignment (typMotif *MotifPtr, typSequence *SequencePtr,
               typSolution *SolutionPtr);
int Analyze (typMotif *MotifPtr, typSequence *SequencePtr,
              typSolution *SolutionPtr);
void FindMotif (typMotif *MotifPtr, typSequence *SequencePtr,
		typSolution *SolutionPtr, typGrid *GridPtr, int posSE);
void FindOneSS (typMotif *MotifPtr, typSequence *SequencePtr,
		typSolution *SolutionPtr, typGrid *GridPtr, int posSE);
void FindOneStem (typMotif *MotifPtr, typSequence *SequencePtr,
                  typSolution *SolutionPtr, typGrid *GridPtr, int posSE);
long NextPos (long PosFirst, long PosLast, typSE *SEPtr, typMotif *MotifPtr,
              typSequence *SequencePtr, int strictcheck, int posSE);
int PickSecondStem (typMotif *MotifPtr, typSequence *SequencePtr, int posgrid,
                    typGrid *GridPtr, long *pos1first, long *pos1last);
int PickStrand (typMotif *MotifPtr, typSequence *SequencePtr, int posgrid,
                typGrid *GridPtr, long *pos1first, long *pos1last);
long PrevPos (long PosFirst, long PosLast, typSE *SEPtr, typMotif *MotifPtr,
              typSequence *SequencePtr, int posSE);

/* Sequence.c */
void ComplementSequence (typSequence *SequencePtr);
void FreeSequence (typSequence *SequencePtr);
int InitializeSequence (char *name, typSequence *SequencePtr);
void MarkSequence (typMotif *MotifPtr, typSequence *SequencePtr);
void ReadEol (FILE *f, char *s);
int ReadSequence (typSequence *SequencePtr);
int SequenceFormat (typSequence *SequencePtr);
void TraceSequence (typSequence *SequencePtr);

/* Solution.c */
void AddSolution (typGrid *GridPtr, typMotif *MotifPtr,
                  typSequence *SequencePtr, typSolution *SolutionPtr);
int AlreadyFound (typSolution *SolutionPtr, typMotif *MotifPtr,
                  typGrid *GridPtr);
void ChangeLine (FILE *f, int *col);
void DisplayRunData (typSequence *SequencePtr, typSolution *SolutionPtr,
                     int ratio);
void FreeGridList (typSolution *SolutionPtr);
void FreeSolution (typSolution *SolutionPtr);
int InitializeSolution (char *solname, char *altname, typSolution *SolutionPtr);
int InsertGrid (typGrid *GridTemp, typSolution *SolutionPtr);
int SaveAlternatives (typMotif *MotifPtr, typSequence *SequencePtr,
                      typSolution *SolutionPtr);
int SaveSolutions (typMotif *MotifPtr, typSequence *SequencePtr,
                   typSolution *SolutionPtr);
