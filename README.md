# Distance Vector Routing

[Read me on GitHub!](https://github.com/SeanCooke/distance-vector-routing)

## Commands
BUILD COMMAND: `$ make all`

RUN COMMAND: `$ ./dvr [location_of_data_file] [port_number]`

CLEAN COMMAND: `$ make clean`

## About
`dvr` is an implementation of the Distance Vector Routing protocol.  All hosts in the network __must__ be started by entering the same `[port_number]`.

Every 10  seconds, each host running `dvr` sends its distance vector to all directly connected nodes.  Simultaneously, each host running `dvr` listens for incomming distance vectors.  If a better route to any node in a host's routing table can be found, the host's routing table is updated accordingly.

## Example
A graphical representation of the network created in the default data files `a.dat`, `b.dat`, and `c.dat` can be found in [abc-network-diagram.png](https://github.com/SeanCooke/distance-vector-routing/blob/master/abc-network-diagram.png).

Initially, `a` thinks its shortest route to `b` is its direct link, though after running `dvr` on all hosts in the network, `a` realizes its shortest route to `b` is through `c` as seen below:

    $ make clean; make all; ./dvr a.dat [port_number]
    
    ## 1
    shortest path to node c: the next hop is c and the cost is 0.5
    shortest path to node b: the next hop is b and the cost is 2.0
    
    ## 2
    shortest path to node c: the next hop is c and the cost is 0.5
    shortest path to node b: the next hop is b and the cost is 1.0

Similarly, on node `b`:

    $ make clean; make all; ./dvr b.dat [port_number]
    
    ## 1
    shortest path to node c: the next hop is c and the cost is 0.5
    shortest path to node a: the next hop is a and the cost is 10.0

    ## 2
    shortest path to node c: the next hop is c and the cost is 0.5
    shortest path to node a: the next hop is c and the cost is 1.0

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