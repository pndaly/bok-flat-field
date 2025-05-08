# bok-flat-field

## Requirement(s)

 - Ubuntu 22.04 LTS (or later)

 - Python3 (3.6 or later)

## Set Up

```bash
 % cd /home/primefocus/bok-flat-field
 % python3 -m pip install -r requirements.txt
 % source bff_etc/bok-flat-field.sh `pwd` prod
 % cd ${BFF_SRC}
 % nohup python3 bok-flat-field.py >> ${BFF_LOG}/bok-flat-field.log 2>&1 &
```

## Quick Test(s) (At Bok)


```bash
 % ping 10.30.3.41
```


```bash
 % echo BOK90 FLATFIELD 123 COMMAND UBAND ON    | nc -w 5  10.30.3.41 5750

 BOK90 FLATFIELD 123 OK

 % echo BOK90 FLATFIELD 123 COMMAND UBAND OFF   | nc -w 5  10.30.3.41 5750

 BOK90 FLATFIELD 123 OK

 % echo BOK90 FLATFIELD 123 COMMAND HALOGEN ON  | nc -w 5  10.30.3.41 5750

 BOK90 FLATFIELD 123 OK

 % echo BOK90 FLATFIELD 123 COMMAND HALOGEN OFF | nc -w 5  10.30.3.41 5750

 BOK90 FLATFIELD 123 OK

 % echo BOK90 FLATFIELD 123 COMMAND ALL ON      | nc -w 5  10.30.3.41 5750

 BOK90 FLATFIELD 123 OK

 % echo BOK90 FLATFIELD 123 COMMAND ALL OFF     | nc -w 5  10.30.3.41 5750

 BOK90 FLATFIELD 123 OK

 % echo BOK90 FLATFIELD 123 REQUEST ALL         | nc -w 5  10.30.3.41 5750

 BOK90 BFF 123 0 0
```

In the latter case, the first 0 is the uband lamp and the second is the halogen lamp.

Log files are written to $BFF\_LOG.

## Status

 - 20250327
```bash
    - Initial release
```

--------------------------------------

Last Modified: 20250327

Last Author: Phil Daly (pndaly@arizona.edu)
