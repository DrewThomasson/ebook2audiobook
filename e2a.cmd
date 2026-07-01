@echo off
rem Thin launcher: forwards every argument to ebook2audiobook.cmd.
rem A symlink drops %* when a .cmd is executed through it; this wrapper does not.
"%~dp0ebook2audiobook.cmd" %*
