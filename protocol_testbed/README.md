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

`analyse.py` can then process the data and display it visually.

Run each program with the `-h` or `--help` to see what arguments they accept.
