A simple blockchain
====================

An implementation of a blockchain.

Initial compilation
--------------------

You need cmake, make and a C++ compiler to compile the computation module.
Run the following commands at the directory where the source code is located:

```
mkdir build
cd build
cmake ..
make
cd ..
```

Usage
------

Python 3 is needed to run the program. Create a configuration file, and run the program with the path of the configuration file as an argument given to the program.

An example:

```
python main.py config.cfg
```

Config file format
------------------

Here is an example configuration file:

```
[overall-config]
difficulty = 0.1
contentFilePath = .\article.txt
[local-config]
ipAddr = 127.0.0.1
port = 23333
id = void
RTO = 0.1
[peer-config]
node0 = 127.0.0.1:23333
node1 = 127.0.0.1:23334
node2 = 127.0.0.1:23335
```

A configuration file has three sections: overall-config, local-config and 
peer-config. Each section should start with a line containing the section 
name surrounded by square brackets.

In each section, you should provide a parameter in the following format:
```
parameterName = parameterValue
```

The parameters to provide in the overall-config section is listed in the 
following table:

|Name           |Explanation                 |
|---------------|----------------------------|
|difficulty     |Controls the hash threshold |
|contentFilePath|Path of the input file      |

The parameter difficulty should be a floating-point number between 0.0 and 
1.0. Note that a larger value of difficulty results in a more inclusive 
standard of block validity, making block generation easier, rather than 
harder.

The parameters to provide in the local-config section is listed in the
following table:

|Name    |Explanation                                                  |
|--------|-------------------------------------------------------------|
|ipAddr  |The local IP address                                         |
|port    |The local UDP port to use                                    |
|id      |Peer identifier for local machine, not exceeding 4 characters|
|RTO     |Timeout window for recovery mode, measured in seconds        |

In the peer-config section, you should provide the IP address and UDP port 
number of all the peers. You should number all the peers starting from 0, 
and use "node"+peer numbering as the parameter name. For example, the IP 
address of a peer numbered 3 should be provided in a parameter called 
"node3". At least three network participants are required for the program to 
work properly.
