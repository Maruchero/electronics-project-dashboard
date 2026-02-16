PROBLEMS:
[x] performance: it seems like the plotting can't keep up with all the data coming from the serial
[ ] rotation deadzone: need to implement a deadzone for rotation to avoid jitter
[x] need for a way to count how many loops are skipped due to lacking of data
[ ] need for a message frequency counter
[ ] gravity subtraction is not working well, leading to drift in position when the board is tilted (maybe it's due to rotation and acceleration desynchronization?)
[ ] need for a fixed dt
[ ] BUG axis object position is calculated always resetting the position, and then applying the transform, while it should be calculated as the previous position plus the transform