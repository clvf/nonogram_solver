# Nonogram Solver

The program solves nonograms by performing logical elimination first and doing
guesswork/bifurcation if needed.

***
Bifurcation: at some puzzles the possibilities as to which cell mark as black or white
cannot be narrowed down further so one of the possibilities should be explored until a
discrepancy found or the puzzle is solved.

## Usage

```bash
$ nonogram --help
$ nonogram solve --help
$ nonogram print --help

$ nonogram solve examples/005-cat.nin

  XX
 XX
 X
 X
 X     XXX
XX    XXXXX
X    XXXXXXX   X   X
X    XXXXXXXX  XX XX
X   XXXXXXXXX  XXXXX
XX  XXXXXXXXXXXXXXXX
 X XXXXXXXXXXXXXXXXX
 XXXXXXX XXXXXXXXXXX
  XXXXX   XXXXX XXX
  XXXXX   XXXX
   XXX     XXX
   XX      XX
  XX        X
  X         X
  XX        XX
  XX        XX


$ nonogram solve examples/010-house.nin

  X
 XXX
XXXXX
X X X
X XXX

$ nonogram print examples/010-house.nin

   +---- (0<->4|len: 3)
   |+--- (0<->4|len: 2)
   ||+-- (0<->4|len: 5)
   |||+- (0<->4|len: 2); (0<->4|len: 1)
   ||||+ (0<->4|len: 3)
   01234
 0 ..... (0<->4|len: 1)
 1 ..... (0<->4|len: 3)
 2 ..... (0<->4|len: 5)
 3 ..... (0<->4|len: 1); (0<->4|len: 1); (0<->4|len: 1)
 4 ..... (0<->4|len: 1); (0<->4|len: 3)
```

If the program didn't find a solution then it's worth to pass the `--debug`
option on the command line so you can see how far it got.

```bash
$ nonogram --debug solve --nb examples/035-smiley.nin

   +---- (3<->4|len: 1)
   |+--- (1<->1|len: 1); (3<->4|len: 1)
   ||+-- (4<->4|len: 1)
   |||+- (1<->1|len: 1); (3<->4|len: 1)
   ||||+ (3<->4|len: 1)
   01234
 0       (0<->4|len: 0)
 1  X X  (1<->1|len: 1); (3<->3|len: 1)
 2       (0<->4|len: 0)
 3 .. .. (0<->1|len: 1); (3<->4|len: 1)
 4 ..X.. (0<->4|len: 3)
```

## Puzzle Input Format

Puzzle is defined as a text file with empty lines (containing only whitespace)
and lines starting with comment (#) ignored.

1. The first line defines the number of columns and rows in the puzzle in this
   order separated by a single space.
1. The subsequent lines define the length of blocks in the rows of the puzzle in
   left-to-right order.
   Each number should be separated by a single space.
1. The following lines define the length of blocks in the columns of the puzzle.
   The leftmost block is the top in the column and the rightmost block is at
   the bottom of the column.
   Each number should be separated by a single space.

###### Sample

This puzzle:
```
               2   
         3 2 5 1 3 
        +-+-+-+-+-+
      1 | | | | | |
        +-+-+-+-+-+
      3 | | | | | |
        +-+-+-+-+-+
      5 | | | | | |
        +-+-+-+-+-+
  1 1 1 | | | | | |
        +-+-+-+-+-+
    1 3 | | | | | |
        +-+-+-+-+-+
```

should be represented as follows:

```
# number of columns   number of rows
5 5

# rows:
1
3
5
1 1 1
1 3

# cols:
3
2
5
2 1
3
```

You can feed in puzzles from https://webpbn.com exported via
https://webpbn.com/export.cgi. Make sure you select ".NIN" (or ".MK") file
format at export.

## FAQ

* Is this solver fast?

  No. Speed was not a concern during the implementation. It solves a 100x100
  puzzle within 12 seconds on a @2.53GHz Inter i3 CPU.

* Where do I find other implementations?

  I suggest checking [Jan Wolter's page](https://webpbn.com/survey/). There are plenty
  of excellent solvers listed on the survey page and you can find a plethora of
  puzzles there as well. You can feed in nonograms from the page if you
  [export them](https://webpbn.com/export.cgi) in ".NIN" format and call
  `nonogram-solver.py --format-nin <puzzle.nin>`.

* What are the rules that you're referring to in the code?

  This program is an implementation of the logical rules published by
  Chiung-Hsueh Yu, Hui-Lung Lee and Ling-Hwei Chen at the paper titled 
  ["An efficient algorithm for solving nonograms"](https://link.springer.com/article/10.1007/s10489-009-0200-0).
