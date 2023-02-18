# expurgar

![](https://github.com/martibarri/expurgar/blob/main/expurgar.png?raw=true)

Simple script that helps removing junk bytes included in malware binaries.
It's a well-known technique used to avoid ending up in a sandbox analysis.

```bash
usage: expurgar.py [-h] -f FILE [-c CHAIN]
```

`[-c CHAIN]` is the minimmum number of identical bytes to trigger a _chain_ ( `default=80` )


## test example

![](https://github.com/martibarri/expurgar/blob/main/example_test.png?raw=true)

## malware example

Real malware sample with different bundled files and with multiple layers of obfuscation.

![](https://github.com/martibarri/expurgar/blob/main/example_malware.png?raw=true)
