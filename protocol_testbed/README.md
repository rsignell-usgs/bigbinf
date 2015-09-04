# Protocol testbed

## Setup
Make sure you have working binaries for
+ scp (openssh)
+ scp (openssh-portable with HPN patches)
+ sftp (openssh)
+ gridftp (Globus)

Then, check that the paths are correct in `args.json`. The `%s` placeholders in order are: remote user and host, remote path, local path.

## Usage
Run `test.py` to generate dumps containing information about the transfer(s). These are stored in `packet_dumps/`.
```
python test.py [-h] -i INTERFACE -H HOST -r PATH -l PATH

optional arguments:
  -h, --help            show this help message and exit
  -i INTERFACE, --interface INTERFACE
                        The interface to capture packets on
  -H HOST, --host HOST  The host which has the file to be copied
  -r PATH, --remote-path PATH
                        The path of the file to be copied
  -l PATH, --local-path PATH
                        The path where the file shold be copied to
```

Once there is at least 1 packet dump, you can view the information using `analyse.py`.
```
python analyse.py [-h] [-p PROTOCOL [PROTOCOL ...]] [-n NUMBER] [-s SIZE]

optional arguments:
  -h, --help            show this help message and exit
  -p PROTOCOL [PROTOCOL ...], --protocols PROTOCOL [PROTOCOL ...]
                        Can be any combination of ftp, hpn-scp, gridftp, scp
  -n NUMBER, --number NUMBER
                        The number of dumps to evaluate, starting with the
                        most recent. Defaults to 'all'
  -s SIZE, --test-filesize SIZE
                        The size of the file used for testing, in bytes
```
