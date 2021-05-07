import os, sys, re


# fdOut = os.open("p0-output.txt", os.O_CREAT | os.O_WRONLY)
# fdIn = os.open("p0-io.py", os.O_RDONLY)

fd = os.read(0,1000)

#   PS1 Checker
## check for PS1 in user's invirmoent variable decitionary
##  in 'os.environ'.  Else, show '$'.
if 'PS1' in os.environ:
    os.write(1, (os.environ['PS1']).encode())
else:
    os.environ['PS1'] = '$ '
    os.write(1, (os.environ['PS1']).encode())



while True:

    args = os.read(0, 1000) #this reads 1000 bytes of input

    if len(args) > 0:
        args = args.decode().splitlines()
        
        #splits input into diferent tokens
        for token in args:  
            pass
    else: pass