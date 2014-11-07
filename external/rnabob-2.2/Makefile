# Distribution Makefile for the rnabob pattern searcher
# RNABOB - grep-like pattern searching for RNA structure descriptors
# Wed Aug 25 10:37:18 1993
#
# See "INSTALL" for installation instructions.
# This code is distributed under terms of the GNU General Public License.
# See "README", "COPYING", and "GNULICENSE" for details.
#

RELEASE     = 2.2
RELEASEDATE = "March 1999"
RFLAGS      = -DRELEASE=$(RELEASE) -DRELEASEDATE=$(RELEASEDATE)

# Where everything gets installed.
# You might change this to /usr/local/bin and /usr/local/man or some such.
#
BINDIR 		= $(HOME)/bin
MANDIR          = $(HOME)/man

# Compilation flags. Set your compiler and any necessary global
# switches here. Use an ANSI-compliant C compiler.
#
CC		= gcc 
CFLAGS   	= -O3 

# Machine-specific definitions. You shouldn't need any.
#
MDEFS =	

#######
## should not need to modify below this line
#######
SHELL  = /bin/sh

PROGS=     rnabob

EXAMPLES=  r17.des pseudoknot.des trna.des

OBJS=   patsearch.o rnabob.o \
	alignio.o file.o hsregex.o interleaved.o msf.o selex.o seqencode.o\
	sqerror.o sqio.o getopt.o iupac.o revcomp.o rk.o\
	sre_ctype.o sre_math.o sre_string.o types.o

SQUIDSRC=  alignio.c file.c getopt.c hsregex.c interleaved.c\
	sqerror.c sqio.c iupac.c msf.c revcomp.c\
	rk.c seqencode.c selex.c sre_ctype.c sre_math.c sre_string.c\
	types.c

SQUIDHDRS= squid.h sqfuncs.h rk.h 

SRC=       patsearch.c rnabob.c $(SQUIDSRC)

HDRS=      rnabob.h seqpattern.h sequence.h


all:  $(OBJS) 
	$(CC) $(CFLAGS) $(RFLAGS) -o rnabob $(OBJS) -lm

install: $(PROGS)
	cp $(PROGS)   $(BINDIR)/
	cp rnabob.man $(MANDIR)/man1/rnabob.1

clean:
	-rm -f *.o *~ *.aux *.dvi *.log core TAGS $(PROGS)

.c.o:
	$(CC) $(CFLAGS) $(MDEFS) -c $<


