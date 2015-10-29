# Protocol testbed

## Setup
Make sure you have working binaries for whichever protocols you want to test.

Then, check that the paths are correct in `args.json`. The `%s` placeholders in order are: remote user and host, remote path, local path.

## Usage
Run `test.py` to generate dumps containing information about the transfer(s). These are stored in `packet_dumps/`.

```
usage: test.py [-h] -i INTERFACE -H HOST -r PATH -l PATH [--store-packets]
               [--delete-files]

optional arguments:
  -h, --help            show this help message and exit
  -i INTERFACE, --interface INTERFACE
                        The interface to capture packets on
  -H HOST, --host HOST  The host which has the file to be copied. Include
                        usernames if necessary (e.g. 'user@host').
  -r PATH, --remote-path PATH
                        The path of the file to be copied
  -l PATH, --local-path PATH
                        The path where the file shold be copied to. Please use
                        full paths with a trailing slash.
  --store-packets       With this enabled, information is stored about each
                        packet. This results in much larger log files. When
                        not enabled, only aggregated data is stored
  --delete-files        Remove the transferred file after it is finished
                        copying
```

You may want to automate this with something like `cron`. A script like the following may be useful.

```bash
#!/bin/bash
SIZES=5M 0_5G 1G 1_5G 2G 2_5G
cd path_to_protocol_testbed/
for i in {0..4}
do
	for size in SIZES
	do
		python test.py -i eth1 -H user@remote.host -r path_on_remote/$size -l path_on_local --delete-files
	done
done
```

# Analysis
Run `analysis.ipynb` using IPython Notebook or Jupyter. This assumes that dumps are stored in the `packet_dumps/` directory, which is on the same level as the notebook file.
