#! make
#
# Makefile (GenMake 1.0)
#

#
# Program definitions and options.
#

SHELL	=	/bin/sh
CC	=	cc -D__STDC__

OPT	=       -O
CFLAGS	=	$(OPT)
C++FLAGS	=	$(CFLAGS)
FFLAGS	=	$(OPT)
LIBS	=	-lm -ldl

PROGRAMS	=	rnamot

#
# Make ALL programs...
#

all: $(PROGRAMS)

#
# rnamot
#

RNAMOT_SRCS	=	rnamot.c	base.c	energy.c	grid.c \
		motif.c	scan.c	sequence.c	solution.c
RNAMOT_HDRS	=	rnamot.h
RNAMOT_OBJS	=	rnamot.o	base.o	energy.o	grid.o \
		motif.o	scan.o	sequence.o	solution.o

rnamot:	$(RNAMOT_OBJS)
	$(CC) $(OPT) $(RNAMOT_OBJS) -o rnamot $(LIBS)

$(RNAMOT_OBJS):	$(RNAMOT_HDRS)

