:: An extremely simple wrapper to allow calling G95 in F mode as "F <files>"
@echo off
g95 -std=F %*
