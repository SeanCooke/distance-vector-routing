# Distance Vector Routing

[Read me on GitHub!](https://github.com/SeanCooke/distance-vector-routing)

## Commands
BUILD COMMAND: `$ make all` RUN COMMAND: `$ ./dvr [location_of_data_file] [port_number]` CLEAN COMMAND: `$ make clean`

## About
`dvr` is an implementation of the Distance Vector Routing protocol.  All nodes in the network __must__ be started by entering the same `[port_number]`.

Every 10  seconds, each node running `dvr` sends its distance vector to all directly connected nodes.  Simultaneously, each node running `dvr` listens for incomming distance vectors.  If a better route to any node in a node's routing table can be found using this information, the routing table is updated respectively.

## Example
A graphical representation of the network created in the default data files `a.dat`, `b.dat`, and `c.dat` can be found [here](#)

## The Data File
The data file holds the number of nodes immediately connected nodes, the hostnames of the immediately connected nodes and the weights of the immediately connected vertices.  The first line __must__ contain the number of immediately connected nodes.  All subsequent lines __must__ be in the following format:

    [hostname] [weight_to_hostname]
    
An example data file can be seen below:

    3
    b 2.0
    c 5.0
    d 1.0
    
Plese note that only a single space is allowed between `[hostname]` and `[weight_to_hostname]`.

## References
* Base client/server code modified from chapter 2.7.1 of __Computer Networking: A Top-Down Approach (7th Edition)__ by Kurose and Ross.
* Modified code on multithreading found [here](http://www.tutorialspoint.com/python/python_multithreading.htm).
