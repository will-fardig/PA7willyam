# William Theory

## Question one

Okay if we are swapping with x=1 and y=2, the traced values are:

### pass by value
Enters with a record of a=Cell(1), b=Cell(2), private both.
t=1, then a=2, and b=1.
Callee ends with {a:2 b:1 t:1} but the callER still keeps x=1 y=2. Swap is only done on the copies cause that's what passing by value means.

### pass by REFERENCE !?!?
a goes to x cell, b goes to y cell. t is a private local var.
t=1, then a=b writes X's cell to become 2, and the calleer reads the x=2. Then b=t writes 1 into y cell, leaving us with x=2 and y=1. Passed by reference if you will.

### pass by value-result
a=Cell(1) and b=Cell(2) remain private, with the destinations recorded (I think represented as [a->x and b->y]?). The body runs showing the caler haing 1, 2 during the body. At the return, the variables are passed back, replacing them to become x=2 and y=1.

## question TWO!

### by Reference
x and y are the same cell (a). x=x+1 makes the cell become 11.
y= y+1 then writes 12 as it read 11.

### value result
x=Cell(10) and y=Cell(10) are two copies. x=11 and y=11 both occur completely separately with the n=n+1 since they're separate cells.

### Why?

Reference only stores one reference so it has to stack increments. Value Result has two cells that increment separately, without writing each other over. Swap(a, a) doesn't help us here because it only swaps copies.

## closures (q3)

Each closure returns 3.

This is because there's just one i cell in the environment. Each closure sets the status link as its defining environment when it's used. The lookup happens on call, so it follows the static link. Exits when i becomes 3 (failing to trip true as 3 !< 3) so they al come up 3.

You can fix it by altering the for loop so each iteration has a fresh environment instea dof the exact same one, avodiingthis kind of stacking. Copy the current alue at the start of each iteration in order to do this, don't just rely on the static link from the last.