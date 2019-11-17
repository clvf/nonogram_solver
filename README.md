# Nonogram Solver

The program solves nonograms that doesn't require guessing or bifurcation
(chronological backtracking) ie. whose solution can be find by logical
elimination.

## Usage

```bash
$ nonogram_solver.py --help
$ nonogram_solver.py examples/house.txt

  X
 XXX
XXXXX
X X X
X XXX
```

Note that python 3.7 or later is required because of the use of
[dataclasses](https://docs.python.org/3/library/dataclasses.html).

If the program didn't find a solution then it's worth to pass the `--debug`
option on the command line so you can see how far it got:

```bash
$ nonogram_solver.py examples/smiley.txt --debug

Program couldn't find any solution.
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

BTW the puzzle above would require bifurcation for the solution because the
possibilities as to which cell mark as black or white cannot be narrowed down
further so one of the possibilities should be explored until a discrepancy
found or the puzzle is solved.

## Puzzle Input Format

## FAQ

* What kind of nonogram puzzles can this solver cope with?

The program deals with nonograms that can be solved by logical elimination and
that don't require bifurcation (depth first search based chronological
backtracking). These are the puzzles that humans can solve (I think) and that
you find in various online or printed newspapers.

* Is this solver fast?

No. Speed was not a concern during the implementation. It solves a 100x100
puzzle within 12 seconds on a @2.53GHz Inter i3 CPU.

* What if I need a solver that do bifurcation?

I suggest checking
[Dr. Steven Simpson's excellent nonogram solver](http://scc-forge.lancaster.ac.uk/open/simpsons/software/pkg-nonowimp.htmlz.en-GB). It's fast, portable and I assume that it can deal with all the solvable
puzzles.

* What are the rules that you're referring to in the code?

This program is an implementation of the logical rules published by
Chiung-Hsueh Yu, Hui-Lung Lee and Ling-Hwei Chen at the paper titled 
["An efficient algorithm for solving nonograms"](https://link.springer.com/article/10.1007/s10489-009-0200-0).

* What's the use of this?

This program has integral part of the soon-to-be world peace obviously.
