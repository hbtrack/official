  File "C:\HB TRACK\scripts\audit\verify_hb_cli_evidence.py", line 157
    codeblock(md, f"$ {stdlib_probe['cmd']}\nRC={stdlib_probe['returncode']}\n\n{stdlib_probe['stdout']}\n{('[STDERR]\\n'+stdlib_probe['stderr']) if stdlib_probe['stderr'] else ''}")
                                                                                                                                                                                     ^
SyntaxError: f-string expression part cannot include a backslash
