#! /usr/bin/env python3

import os, sys, re

def execute(args):
    #if empty then return
    if len(args) == 0:
        return

    #exit command
    elif args[0].lower() == "exit":
        sys.exit(0)

    #cd changing directory command
    elif args[0].lower() == "cd":
        try:
            #cd ..
            if len(args) == 1:
                os.chdir("..")
            else: #other directory
                os.chdir(args[1])
        except: #file directory does not exist
            os.write(1, ("cd %s: Directory does not exists") %args[1].encode())
            pass
    #piping
    elif "|" in args:
        pipe(args)
    else:
        rc = os.fork()
        background = True
        #if & in args, then its in background
        if "&" in args:
            args.remove("&")
            background = False
        elif rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)
        elif rc == 0:
            #execute specified program
            if "/" in args[0]:
                program = args[0]
                try:
                    os.execve(program, args, os.environ)
                except FileNotFoundError:
                    pass
            #Redirect happens
            elif ">" in args or "<" in args:
                redirect(args)
            #No specifications, just execute program
            else:
                #trying each directory in path
                for dir in re.split(":", os.environ['PATH']):
                    program = "%s/%s" % (dir, args[0])
                    try:
                        os.execve(program, args, os.environ) #trying to execute
                    except FileNotFoundError:
                        pass

            #could not execute
            os.write(2, ("Could not execute %s\n" %args[0]).encode())
            sys.exit(1) #terminate with error

        else:
            #if parent running in background we wait for child
            if background == True:
                os.wait()

#redirect
def redirect(args):
    #fd 1
    if '>' in args:
        #redirect child's stdout
        os.close(1)
        os.open(args[args.index('>')+1], os.O_CREAT | os.O_WRONLY)
        os.set_inheritable(1,True)
        #remove '>' symbol from input
        args.remove(args[args.index('>') +1]) #space after '>'
        args.remove('>')
    #fd 0
    if '<' in args:
        #redirect child's stdin
        os.close(0)
        os.open(args[args.index('<') +1], os.O_RDONLY)
        os.set_inheritable(0,True)
        #remove '<' symbol from input
        args.remove(args[args.index('<') +1]) #space after '<'
        args.remove('<')

    #trying each directory in Path
    for dir in re.split(":", os.environ['PATH']):
        program = "%s/%s" % (dir,args[0])
        try:
            os.execve(program,args,os.environ)
        except FileNotFoundError:
            pass
    os.write(2, ("Could not execute %s\n" % args[0]).encode())
    sys.exit(1)

#pipe
def pipe(args):
    pr, pw = os.pipe()
    #left side of pipe
    left = args[0:args.index("|")]
    right = args[args.index("|") +1:] #everything afte '|'

    #forking
    rc = os.fork()

    if rc < 0:
        os.write(2, ("Fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    #child
    elif rc == 0:
        os.close(1) #redirect child's stdout
        os.dup(pw)
        os.set_inheritable(1, True)
        for fd in (pr, pw):
            os.close(fd)
        command(left)
        os.write(2, ("Could not execute %s\n" %left).encode())
        sys.exit(1)
    else:
        os.close(0)
        os.dup(pr)
        os.set_inheritable(0, True)
        for fd in (pr, pw):
            os.close(fd)
        if "|" in right: #recursion in case of a | b | c | d | ...
            pipe(right)
        command(right)
        os.write(2, ("Could not execute %s\n" %right).encode())
        sys.exit(1)

#command
def command(args):
    if "/" in args[0]:
        program = args[0]
        try:
            os.execve(program, args, os.environ)
        except FileNotFoundError:
            pass

    #if redirection happens
    elif ">" in args or "<" in args:
        redirect(args)
    else:
        for dir in re.split(":", os.environ['PATH']):
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ)
            except FileNotFoundError:
                pass
    os.write(2, ("Could not execute %s\n" % args[0]).encode())
    sys.exit(1)

#main shell
while True:
    #   PS1 Checker
    ## check for PS1 in user's invirmoent variable decitionary
    ##  in 'os.environ'.  Else, show '$'.
    if 'PS1' in os.environ:
        os.write(1, (os.environ['PS1']).encode())
    else:
        os.environ['PS1'] = '$ '
        os.write(1, (os.environ['PS1']).encode())
    args = os.read(0, 1000) #this reads 1000 bytes of input fd from keyboard
    #No input
    if len(args) == 0:
        break
    args = args.decode().splitlines()
    #splits line into tokens
    for token in args:  
        execute(token.split())
