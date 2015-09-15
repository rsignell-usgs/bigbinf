# BigBInf - Access to Big Data in Bioinformatics

A Computer Science Honours project at the University of Cape Town in collaboration with the University of the Western Cape.

## Contributors
+ Brendan Ball
+ Andrew van Rooyen

## Supervisor
+ Michelle Kuttel (CS, UCT)

## External advisors
+ Antoine Bagula (CS,UWC)
+ Alan Christoffels (SANBI,UWC)
+ Peter van Heusden (SANBI,UWC)

# Description
Collaboration between bioinformatics organizations involves shared access to large datasets. This project investigates two avenues for tackling the collaborative analysis of "big data" in bioinformatics: efficient transport of large datasets across high speed WAN networks and implementation of "community clouds" that host and securely execute code close to the location where data is stored.

"Community clouds" are cloud computing services built on "micro clouds" hosted by collaborating organisations, as opposed to conventional "cloud computing" hosted by cloud vendors (such as Microsoft, Google and Amazon). Hosting "micro clouds" close to scientific data collections would facilitate scientific collaboration through moving code closer to data, rather than vice versa.

Historically, data has been exchanged using tools and protocols like SSH and FTP, but new protocols, such as GridFTP and HPN-SSH, offer more efficient use of high speed networks.

The first part of this project will compare and contrast the performance of GridFTP, HPN-SSH, FTP and SSH for transferring multi-gigabyte datasets. The comparison will examine throughput, delays, security and authentication features of these protocols and their implementations.

The second part of this project will survey existing cloud computing infrastructures towards their suitability for creating organisation-level "micro clouds". At least two "micro clouds" will be implemented in order to prototype a "community cloud" where code can be migrated between "micro cloud" installations. The prototype code will be a bioinformatics analysis code.
