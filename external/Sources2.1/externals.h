/*
 *  This file contains all external variables shared amongst the various
 *  components of fmat.c
 */


/*
 *  Functions
 */

#include "defines.h"

void    read_parameters();
void    codon_bias();
void    read_codon_table();
void    codon_parse_sequence();
void    splice_score_sequence(char *sequence, float **tvec);
void    read_weight_matrix();
float   matrix_score();
void    make_lcc_table(int ktuple);
void    score_lcc();
float   max();
void    autocor_parse_sequence();
void    autocor_score_sequence();
void    autocor_read_vectors(); 
void    show_predicted_classes();
void    read_class_tables();
void    show_real_classes();
void    read_class_tables();
void    flag_correct_predictions();  
void    graphics_setup();
void    make_color_map();
void    show_predicted_classes();


float   **ifktuple_parse_sequence(char *sequence);  
                                           /* returns pointer to array of kt values    */

void    score_ifktuple(float **bias4ktuple, float **tvec, int position);             

                                       /* scores ifkt given array and position     */

char    *read_sequence_genbank();     /* reads sequence and returns pointer to it */

float   *lcc_parse_sequence(int ktuple, char *sequence);        
                                      /* returns lcc table                        */



/*
 *  Headers
 */

#include "flags.h"  
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <malloc.h>

#if TIME
#include <sys/times.h>
#include <sys/param.h>
#endif

#if GRAPHICS
#include <gl/gl.h>
#include <gl/device.h>
#endif

#if SUB_OPTIMAL
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#endif


#include "defines.h"
#include "score_periodicity.h"

/*
 *  External Variables
 */ 

extern  char    file_name[100];                  /*      File name of sequence                   */
extern  char    class_name[10];                 /*      Genbank class name (catagory)           */
extern  int     seq_length;                     /*      Length of sequence to be analysed       */
extern  int     upper_bound, lower_bound;       /*      boundries in sequence                   */
extern  int     first_actual_base;              /*      first defined base in actual seq        */
extern  int     last_actual_base;               /*      last defined base in actual seq         */

extern  int     diag_void[PSEQ_TYPES];          /*      shortest sequences considered           */
extern  int     max_length[PSEQ_TYPES];         /*      longest sequence considered             */


extern  int     seq_class[2][2][MAX_CLASSES];   /*      intron/exon beginning - end             */
extern  int     seq_real[2][2][MAX_CLASSES];    /*      actual intron/exon beginning - end      */
                                                /*      [intron/exon][beginning/end][number]    */
extern  int     seq_class_stat[2][MAX_CLASSES]; /*      status of predicted seqs                */
extern  int     seq_real_stat[2][MAX_CLASSES];  /*      status of actual seqs                   */
                                                /*      0 = WRONG; 1 = RIGHT                    */
extern  int     exon_num, intron_num;           /*      index and number of predictions         */
extern  int     aseqs[ASEQ_TYPES];              /*      count of sequences of given type, actual*/
extern  int     pseqs[PSEQ_TYPES];              /*      count of sequences of given type, pred  */
extern  int     real_pseqs[PSEQ_TYPES];         /*      count of true predictions               */     
extern  int     real_exon_num, real_intron_num; /*      index and number of actuals             */
extern  int     real_exon_count;                /*      total number of intron/exons in interval */
extern  int     real_intron_count;
extern  int     max_frame;                      /*      external for max to indicate who is max  */

extern  int     real_exon_num;
extern  int     real_intron_num;
extern  int     seg_count;                       /*      index for segments stored when          */
                                                 /*      calculating dvec                        */

extern  int     parray_number;                   /*      frame number for parray                 */
extern  int     display_parameter;               /*      display parameter input                 */
extern  int     parray_count;                    /*      number of parray to store               */ 
extern  int     ppseq;                           /*      number of packed predicted sequences    */


extern  int     ktuple;                 /*      ktuple length                           */
extern  float   A_co, D_co;             /*      acceptor and donor cutoff values        */

extern  float   cut_off_intron;         /*      Cut-off applied to llmat introns        */
extern  float   cut_off_exon;           /*      Cut-off applied to llmat exons          */
extern  float   temp_var;               /*      temp variable for DP                    */
extern  int     max_length_input;       /*      max length of predicted sequence        */

extern  int     graphics;
extern  int     dp_score;
extern  int     override;
extern  int     reverse;
extern  int     plot_svector;
extern  int     verify_database;
extern  char    dump_file[80];
extern  int     print_neatly; 

/*
 *  This file contains declarations for parameters used for fmat.  
 *  The values are read into these variables in read_parameters.c 
 */


typedef struct actual_subsequences {
        int     start;                  /* start of sequence                */
        int     end;                    /* end of sequence                  */
        float   tvs[PVC];               /* raw classification scores        */
                                        /* tvs[0]  acceptor site            */
                                        /* tvs[1]  donor site               */
                                        /* tvs[2]  codon usage              */
                                        /* tvs[3]  LCC                      */
                                        /* tvs[4]  BLAST                    */
                                        /* tvs[5]  length distribution      */
                                        /* tvs[6]  k-tuple frequency        */
        float   lvs;                    /* corresponding L-Matrix element   */
        int     ps;                     /* prediction status                */
        int     frame;
        int     xfield[2];              /* additional type-specific fields  */
}  struct_ASEQ;


typedef struct predicted_subsequences {
        int     start;                  /* start of sequence                */
        int     end;                    /* end of sequence                  */
        float   tvs[PVC];               /* raw classification scores        */
                                        /* tvs[0]  acceptor site            */
                                        /* tvs[1]  donor site               */
                                        /* tvs[2]  codon usage              */
                                        /* tvs[3]  LCC                      */
                                        /* tvs[4]  distance analysis        */
                                        /* tvs[5]  length distribution      */
                                        /* tvs[6]  k-tuple frequency        */
        float   lvs;                    /* corresponding L-Matrix element   */
        float   dvs;                    /* dvector element                  */
        int     ps;                     /* prediction status                */
        int     frame;                  /* frame of exon, %3 intron length  */
        int     xfield[2];              /* additional type-specific fields  */
        int     type;                   /* PIE or PII (kinda redundant)     */
        struct predicted_subsequences  
               *next_PSEQ;              /* pointer to next predicted 
                                                               seq after DP */
    }  struct_PSEQ;

struct_PSEQ *trace_back();
struct_PSEQ *trace_forward();

void make_dvector(int position, float **lvec, float **tvec, 
                  struct_PSEQ **PSEQ);

typedef struct ifktuple_table {
        char   ktuple[7];              /*      Array of ktuple names                    */
        float  frequency;              /*      Array of ktuple biases                   */
} struct_ifkt_table; 

typedef struct ktuple_struct {
        char   ktuple[10];
        float  log_freq[PSEQ_TYPES];
} struct_ktt;

float **ktuple_parse_sequence(char *sequence, struct_ktt *p_ktt);
struct_ktt *read_ktuple_table();

typedef struct blast_table_struct {
        float   msp_score;                    /* maximum segment pair score     */
        int     segment_start;                /* start of segment interval      */
        int     segment_end;                  /* end of segment interval        */
} struct_blast;

struct_blast *read_blast_table();
float        *blast_parse_sequence(char *sequence, struct_blast *p_bt_exon);



typedef struct length_distribution_tables {
        int     length;                       /* maximum length of subsequence */
        float   length_score;                 /* score for corresponding length */
} struct_ldt;

struct_ldt **read_length_distribution();


typedef struct s_vector {
        float dvec;                     /* copy of D-vector                          */
        int   start;                
        float reverse_dvec;             /* copy of reverse D-vector                  */
        int   reverse_start;
        float svec;                     /* donor and acceptor sum vector             */
        int   hit_me;                   /* has element been hit by descent_solution? */
        struct s_vector *next_SVEC[2];  /* [0]traceforward, [1]traceback             */
} struct_SVEC;

struct_SVEC **make_svector(struct_PSEQ **PSEQ, struct_PSEQ **rPSEQ);

float display_svector(struct_SVEC **s_vector);







void       score_length(struct_ldt **LDT, float **tvec, int position);

void    dp_main(  struct_PSEQ **PSEQ, 
                  struct_ASEQ **ASEQ,
                  float **lvec, 
                  float **tvec, 
                  float **p_ifkt,
                  float **p_ktv, 
                  struct_ldt **p_ldt, 
                  float *p_lcc,
                  float *p_bv,
                  struct_blast *p_bt,
                  int **p_fv,
                  int ***p_av);

void    reverse_dp_main(struct_PSEQ **PSEQ, struct_ASEQ **rASEQ,
                float **lvec, float **tvec, float **p_ifkt,
                float **p_ktv, struct_ldt **p_ldt, float *p_lcc,
                float *p_bv, struct_blast *p_bt,int **p_fv, int ***p_av);

int calculate_offset(char *ktuple_name, int ktuple_length);
void invert_blast_table(struct_blast *);

void show_predicted_classes_neatly(struct_PSEQ *PSEQ_head, int direction);


extern  char *aseq_name[ASEQ_TYPES];         /*       names for the actual sequences types    */
extern  char *pseq_name[PSEQ_TYPES];         /*       names for the predicted seq types       */

extern  char *PARAMETER_FILE;
extern  char *CODON_TABLE;
extern  char *START_MATRIX;
extern  char *DONOR_MATRIX;
extern  char *ACCEPTOR_MATRIX;
extern  char *AUTOCOR_EXON_MATRIX;
extern  char *AUTOCOR_INTRON_MATRIX;
extern  char *LENGTH_TABLE_EXON;
extern  char *LENGTH_TABLE_INTRON;
extern  char *INTERNAL_EXONS;
extern  char *FIRST_EXONS;
extern  char *LAST_EXONS;
extern  char *ALL_EXONS;
extern  char *DUMP_FILE_NAME;
extern  char *COLOR_MAP;
extern  char *KTUPLE_LENGTH;
extern  char *IFKTUPLE_TABLE;
extern  char *WEIGHT_NETWORK_EXON;
extern  char *WEIGHT_NETWORK_INTRON;
extern  char *KTUPLE_EXON;
extern  char *KTUPLE_INTRON;
extern  char *KTUPLE_TABLE;
extern  char *MAX_PIE_LENGTH;
extern  char *MAX_PII_LENGTH;
extern  char *MAX_PFE_LENGTH;
extern  char *MAX_PLE_LENGTH;
extern  char *ACCEPTOR_CUTOFF;
extern  char *DONOR_CUTOFF;
extern  char *PIE_DIAG_VOID;
extern  char *PII_DIAG_VOID;
extern  char *BLAST_TABLE;


extern  char *WEIGHT_MATRIX_PATH;
extern  char *WEIGHT_NETWORK_PATH;
extern  char *GENBANK_PATH;
extern  char *CLASS_TABLES_PATH;
extern  char *CODON_TABLE_PATH;
extern  char *SEQ_PATH;
extern  char *AUTOCOR_MATRIX_PATH;
extern  char *COLOR_MAP_PATH;
extern  char *QUICKPROP_PATH;
extern  char *KTUPLE_PATH;
extern  char *BLAST_PATH;


