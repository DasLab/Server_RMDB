/********************************************************************************/
/*      This routine reads in the sequence, ignoring non-base characters        */
/*	Random characters are inserted when ambiguous positions are encountered */
/********************************************************************************/

#include "externals.h"
#include <stdio.h>

int resolve_ambiguity(int c);
char **make_translation_table();  

#define DATABASE_TYPE GCG

#if DATABASE_TYPE == GCG
#define OFFSET ".offset"
                                /* file extension for index file                */
                                /* offset for GCG                               */
#define SEP_CHAR "_"
                                /* character that separates gb from extension   */
                                /* _ for GCG                                    */

#else
#define OFFSET ".idx"
                                /* file extension for index file                */
                                /* idx for EuGene                               */
#define SEP_CHAR ""
                                /* character that separates gb from extension   */
                                /* no char for EuGene                           */
#endif 


char *read_sequence_genbank(file_name,class_name,lower_bound,upper_bound)
char	file_name[100];
char	class_name[100];
long	upper_bound, lower_bound;
{

        extern char *GENBANK_PATH; 
        extern int  seq_length;

        char *sequence;
        char *full_sequence;
        char *offset_line;
        char **trans_table;

	FILE    *fp_index;              /*      pointer for index file          */
	FILE    *fp_search;             /*      pointer for sequence file       */
	char    search_file[100];
	char    index_file[100];
	long	i, j, k, c;
        char    character;
	short	fnff;			/*	file not found flag		*/
	char    seq_in[20];             /*      sequence fscanf'd               */
	char    class_in[4];            /*      class fscanf'd                  */
	long  entry_start;              /*      entry start byte                */
	long  seq_start;                /*      sequence start byte             */
        long  base_count;               /*      number of bases in whole seq    */
	long  seq_end;                  /*      sequence end byte               */
	long    foo;                    /*      unknown field in index          */
        int     code_type;              /*     3 = ASCII, 4 = 2BIT binary      */

        offset_line = malloc(sizeof(char)*80);

	/*	srandom(time());	*/

	fprintf(stderr, "read_sequence_genbank(%s, %s, %d, %d)\n", 
		file_name, class_name, lower_bound, upper_bound);
		

	strcpy(search_file, GENBANK_PATH);
	strcat(search_file, "gb");
        strcat(search_file, SEP_CHAR);
	strcat(search_file, class_name);
	strcpy(index_file, search_file);
	strcat(search_file, ".seq");
	strcat(index_file, OFFSET);

	if ((sequence = malloc(upper_bound - lower_bound + 5)) == NULL){
		fprintf(stderr, "\nerror allocating memory for sequence\n");
		exit(0);
	}


	if ((fp_index = fopen(index_file, "r")) == NULL) {
		fprintf(stderr,"\nerror opening file: %s\n", index_file);
		exit(0);
	}
#if DATABASE_TYPE != GCG 
        fprintf(stderr, "DATABASE_TYPE != GCG\n");
	while ((fnff = fscanf(fp_index, "%s %s %d %d %d %d",
	    seq_in, class_in, &entry_start, &seq_start, &seq_end, &foo)) != EOF) {
		if (!strcasecmp(file_name,seq_in)) {
			break;
		}
	}
#else 
        fprintf(stderr, "DATABASE_TYPE = GCG\n");
        character = '*';
        while ((fnff = fread(offset_line, (size_t)sizeof(char), (size_t)(70), fp_index)) != EOF) {
            strcpy(seq_in,offset_line);
            if (!strcasecmp(file_name,offset_line)) {
                    break;
            }
            while (character != '\n'){               /* read to end of line */
                fscanf (fp_index, "%c", &character);
            }
        }
        if (fnff == EOF) {
            fprintf(stderr, "Requested Sequence not found in  %s\n", index_file);
            exit(0);
        }

        offset_line += 21;                /* skip over first field containing nulls */

        sscanf(offset_line, "%5d%7d%8d%8d",  &code_type,&seq_start, &foo,&base_count);
        fprintf(stderr, "Parsed: %s %d %d %d\n", seq_in, code_type, seq_start, base_count); 

        if ((full_sequence = malloc(base_count)) == NULL){
                fprintf(stderr, "\nerror allocating memory for full_sequence\n");
                exit(0);
        }


#endif 
        if (fnff == EOF) {
            fprintf(stderr,"\nError: File '%s' ", index_file);
            fprintf(stderr,"does not contain sequence '%s'\n", file_name);
            exit(0);
	}

	if ((fp_search = fopen(search_file, "r")) == NULL) {
		fprintf(stderr,"error opening file: %s\n", search_file);
		exit(0);
	}

	i = 1;
	k = 0;
/*	fprintf(stderr,"upper/lower %d, %d \n", lower_bound, upper_bound);	*/
	fseek(fp_search, seq_start, SEEK_SET);
         
        while (getc(fp_search) != '\n') ;                     /* read two CR/LF       */
        while (getc(fp_search) != '\n') ;                     /* to get to seq        */

        if ( code_type == 3 ) {                               /* ASCII sequence       */
	    for(j = 1; j <= base_count; j++) {                /* read actual sequence */
                character = toupper(getc(fp_search));
                if ((j >= lower_bound) && (j <= upper_bound)){
                    sequence[i++] = resolve_ambiguity(character);
/*
                    fprintf(stderr, "%c", character);
*/
                }
            }	
             seq_length = i-1;
        }
        else if ( code_type == 4 ) {                          /* 2BIT code            */
            trans_table = make_translation_table();
            for (i = 0; i <  base_count/4 - 1; i++){
                character = getc(fp_search);
                strcat(full_sequence, trans_table[character]);
            }
            full_sequence--;                                  /* start at sequence[1] */
            strncpy(sequence, full_sequence += (lower_bound -1), upper_bound - lower_bound + 1);
#if 0
            fprintf(stderr, "full_sequence = %s\n", full_sequence);
            fprintf(stderr, "sequence: %s\n", sequence); 
#endif
            seq_length =  upper_bound - lower_bound + 1;
            fprintf(stderr, "seq_length: %d\n", seq_length);
        } 
        else {
            fprintf(stderr,"undefined code type\n");
            exit(0);
        }

	fclose(fp_search);
        if (verify_database) exit(0); 
        return(sequence);

}


int resolve_ambiguity(c)
int c;
{
        switch(c){
	case 'A':
			return(c);
	case 'C':
			return(c);
	case 'G':
			return(c);
	case 'T':
			return(c);
	case 'N':
			switch((random()&3)){
			case 0:
				return('A');
			case 1:
				return('C');
			case 2:
				return('G');
			case 3:
				return('T');
			default:
				fprintf(stderr,"Error in resolving 'N' base\n");
				break;
			}
	case 'R':
			switch(random()&1){
			case 0:
				return('A');
			case 1:
				return('G');
			default:
				fprintf(stderr,"Error in resolving 'R' base\n");
				break;
			}
	case 'Y':
			switch(random()&1){
			case 0:
				return('C');
			case 1:
				return('T');
			default:
				fprintf(stderr,"Error in resolving 'Y' base\n");
                        }
        }
}


char **make_translation_table()
{
    int i, j, k, l, m, n;
    char **trans_table;
    static char bases[] = {'C', 'T', 'A', 'G'}; 

    fprintf(stderr, "char **make_translation_table()\n");
    fprintf(stderr, "bases = %s\n", bases);

    trans_table = calloc(BASES*BASES*BASES*BASES, sizeof(char *));
    for(i = 0; i < BASES*BASES*BASES*BASES; i++){
        if((trans_table[i] = (char *)calloc(BASES+1, sizeof(char))) == NULL){
            fprintf(stderr, "\nerror allocating memory for trans_table\n");
            exit(0);
        }
    }
    m = 0;
    for(i = 0; i < BASES; i++){
      for(j = 0; j < BASES; j++){
        for(k = 0; k < BASES; k++){
          for(l = 0; l < BASES; l++){
              trans_table[m][3] = bases[l];
              trans_table[m][2] = bases[k];
              trans_table[m][1] = bases[j];
              trans_table[m][0] = bases[i];  
              trans_table[m][4] = '\0';
#if 0
              fprintf(stderr, "trans_table[%3d]  %x = %s \n", m,m, trans_table[m]);
#endif
              m++;
          }
        }
      }
    }
    return (trans_table);
}

