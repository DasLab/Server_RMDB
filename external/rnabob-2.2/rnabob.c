/* rnabob.c
 * 
 * Driver for rnabob.
 * 
 * rnabob is a database searching program, whose strength is
 * searching for secondary structure motifs of undefined or
 * only partially defined primary sequence.
 * 
 * rnabob is inspired by Gautheret, Major, and Cedergren's "rnamot"
 * RNA motif searching program. rnabob uses essentially the same
 * motif descriptor syntax as rnamot, with a few changes (see
 * the doc's). rnabob uses a different search engine than rnamot
 * (rnabob's is based on UNIX Perl's regular expression searching
 * algorithm). 
 * 
 * See: Gautheret D, Major F, Cedergren R. Pattern searching/alignment
 * with RNA primary and secondary structures: an effective descriptor
 * for tRNA. CABIOS 6:325, 1990.
 */



#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include "squid.h"
#include "rnabob.h"

static void writematch(Seqexp *exp);
static int  matchlen(Seqexp *exp);

static struct opt_s OPTIONS[] = {
  { "-c", TRUE, sqdARG_NONE },
  { "-h", TRUE, sqdARG_NONE },
  { "-q", TRUE, sqdARG_NONE },
  { "-s", TRUE, sqdARG_NONE },
  { "-F", TRUE, sqdARG_NONE },
};
#define NOPTIONS (sizeof(OPTIONS) / sizeof(struct opt_s))

static char banner[] = "\
rnabob - fast RNA pattern searching";

static char usage[] = "\
Usage: rnabob [-options] <descriptor-file> <sequence-file>\n\
\n\
  Available options: \n\
     -c:    search both strands of database\n\
     -h:    print short help and usage info\n\
     -q:    quiet: suppress verbose banner and headers\n\
     -s:    skip mode: disallow overlapping matches\n\
     -F:    fancy: show full alignments to pattern\n\
";

int
main(int argc, char **argv)
{
  char       *dbfile;		/* name of sequence file to search           */
  char       *descfile;		/* name of file containing descriptor        */
  SQFILE     *dbfp;		/* ptr to dbfile, opened for sequential read */
  FILE       *descfp;		/* ptr to descfile, opened for read          */
  int         fmt;		/* format of dbfile (kEMBL, kPearson, etc.)  */
  char       *seq;              /* sequence to search                        */
  SQINFO      sqinfo;		/* optional info about seq                   */
  Seqexp     *probe;		/* compiled search descriptor                */
  char       *testseq;          /* binary-encoded seq                        */
  char       *compseq;		/* binary-encoded complement of seq          */
  char       *curptr;		/* ptr into testseq or compseq               */
  int         pos, endpos;
  int         result;
  int         totscan;		/* total number of bases scanned             */
  int         skipforward;

  int skipmult;		/* OPTION: True to filter out overlapping hits   */
  int searchcomp;	/* OPTION: Search complementary strand as well   */
  int be_quiet;		/* OPTION: TRUE to silence verbosity             */
  int fancy;		/* OPTION: TRUE to show full alignments          */
  
  char *optname;
  char *optarg;
  int   optind;

#ifdef MEMDEBUG
  unsigned long histid1, histid2, orig_size, current_size;
  orig_size = malloc_size(&histid1);
#endif

  /*********************************************** 
   * Parse command line
   ***********************************************/
  
  skipmult   = FALSE;
  searchcomp = FALSE;
  be_quiet   = FALSE;
  fancy      = FALSE;
  
  while (Getopt(argc, argv, OPTIONS, NOPTIONS, usage, 
		&optind, &optname, &optarg))
    {
      if      (strcmp(optname, "-c") == 0) { searchcomp = TRUE; }
      else if (strcmp(optname, "-q") == 0) { be_quiet   = TRUE; } 
      else if (strcmp(optname, "-s") == 0) { skipmult   = TRUE; }
      else if (strcmp(optname, "-F") == 0) { fancy      = TRUE; }
      else if (strcmp(optname, "-h") == 0) {
	puts(banner);
        printf("    version %s (%s), using squid %s (%s)\n",
	       RELEASE, RELEASEDATE, squid_version, squid_date);
	puts(usage);
        exit(EXIT_SUCCESS);
      }
    }

  if (argc - optind != 2) Die("Incorrect number of arguments\n%s", usage);

  descfile = argv[optind++];
  dbfile   = argv[optind++];

  /*********************************************** 
   * Initialize sequence file, read descriptor
   ***********************************************/

  if (! SeqfileFormat(dbfile, &fmt, "BLASTDB"))
    switch (squid_errno) {
    case SQERR_NOFILE: 
      Die("Sequence file %s could not be opened for reading", dbfile); break;
    case SQERR_FORMAT: 
    default:           
      Die("Failed to determine format of sequence file %s", dbfile);
    }
  if ((dbfp = SeqfileOpen(dbfile, fmt, "BLASTDB")) == NULL)
    Die("Failed to open sequence file %s for reading", dbfile);


  if ((descfp = fopen(descfile, "r")) == NULL) 
    Die("Failed to open descriptor file %s for reading", descfile);
  if ((probe = seqcomp(descfp)) == NULL)
    Die("Failed to compile pattern from descriptor %s", descfile);
  fclose(descfp);

  /*********************************************** 
   * Print banner and do the search
   ***********************************************/
  if (! be_quiet)
    {
      printf("Waking up rnabob: version %s, %s\n", RELEASE, RELEASEDATE);
      puts  ("---------------------------------------------------");
      printf("Database file:                 %s\n", dbfile);
      printf("Descriptor file:               %s\n", descfile);
      printf("Complementary strand searched: %s\n", searchcomp? "yes":"no");
      printf("Filter out overlapping hits:   %s\n", skipmult? "yes":"no");
      puts  ("---------------------------------------------------");
  
      puts("");
      printf(" seq-f  seq-t     name     description\n");
      printf("------ ------ ------------ -----------\n");
    }

  totscan = 0;
  while (ReadSeq(dbfp, fmt, &seq, &sqinfo))
    {
      s2upper(seq);

      totscan += sqinfo.len;

      testseq = (char *) MallocOrDie ((sqinfo.len + 1) * sizeof(char));
      if (! seqencode(testseq, seq))
	Die("failed to encode the sense strand of %s", sqinfo.name);

      curptr  = testseq;
      pos     = 0;
      while ((result = seqexec(probe, curptr)) != -1)
	{
	  pos += result + 1;
	  curptr += result + 1;

	  skipforward = matchlen(probe);
	  endpos = pos + skipforward - 1;
	  printf("%6d %6d %12s %s\n", pos, endpos, sqinfo.name, 
		 sqinfo.flags & SQINFO_DESC ? sqinfo.desc : "");
	  if (fancy) writematch(probe);

	  if (skipmult)
	    {
	      curptr += skipforward -1;
	      pos    += skipforward -1;
	    }
	 }
      if (searchcomp)
	{
	  totscan += sqinfo.len;

	  compseq = (char *) MallocOrDie ((sqinfo.len + 1) * sizeof(char));
	  if (! coded_revcomp(compseq, testseq))
	    Die("coded_revcomp failed");

	  curptr  = compseq;
	  pos     = sqinfo.len + 1;
	  while ((result = seqexec(probe, curptr)) != -1)
	    {
	      pos -= result+1;
	      curptr += result+1;

	      skipforward = matchlen(probe);
	      endpos = pos - skipforward + 1;
	      printf("%6d %6d %12s %s\n", pos,endpos,sqinfo.name,
		     sqinfo.flags & SQINFO_DESC ? sqinfo.desc : "");
	      if (fancy) writematch(probe);

	      if (skipmult)
		{
		  curptr += skipforward -1;
		  pos    -= skipforward -1;
		}
	    }
	  free(compseq);
	}
      free(seq);
      free(testseq);
    }

  if (! be_quiet)
    {
      printf("\nrnabob run completed.\n");
      printf("Total number of bases scanned: %d\n", totscan);
    }

  SeqfileClose(dbfp);

#ifdef MEMDEBUG
  current_size = malloc_size(&histid2);
  if (current_size != orig_size)
    malloc_list(2, histid1, histid2);
  else
    fprintf(stderr, "[No memory leaks]\n");
#endif

  return 0;
}

/* Function: matchlen()
 * 
 * Purpose:  Return the length of a match, given a fully
 *           matched Seqexp.
 */
static int
matchlen(Seqexp *exp)
{
   Patnode *nodep;
   int      bases = 0;

   for (nodep = exp->program; nodep->opcode != END; nodep = nodep->next)
    bases += (int) nodep->flen;
   return bases;
}

/* Function: writematch()
 * 
 * Purpose:  Fancy "alignment" output of a match.
 */
static void
writematch(Seqexp  *exp)
{
  Patnode *nodep;
  char    *outs;
  int      bases = 0;

  for (nodep = exp->program; nodep->opcode != END; nodep = nodep->next)
    {
      if (nodep->matchpar == NULL)
	printf("|");
      bases += (int) nodep->flen;
      outs = (char *) malloc (nodep->flen + 1);
      seqndecode(outs, nodep->fatom, nodep->flen);
      printf("%s", outs);
      free(outs);
    }
  printf("|\n");
}

