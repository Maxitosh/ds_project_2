# Group Project 2: Distributed File System

## Team
Kureikin Maks

##Project description
The Distributed File System (DFS) is a file system with data stored on a server. The data is accessed and processed as if it was stored on the local client machine. The DFS makes it convenient to share information and files among users on a network.

## Installation

Use the docker engine [docker](https://www.docker.com) and [docker hub](https://hub.docker.com/) to install DFS.

```bash
pip install docker
docker pull [OPTIONS] NAME[:TAG|@DIGEST]
docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
```

Naming and Storage servers should be launched on distinct machines and located in the subnet
for communication purposes.

## Usage
![Client Console](images/client_console.png)

Available commands in client console.  



## Structure of DFS
![DFS structure](images/dfs_structure.jpeg)

The idea of this DFS structure is to split the area between clients and DFS
system itself.  
Nodes of DFS are in private, isolated subnet so that provides
security measurements.  
Naming server is an entry point which controls incoming
requests and manipulates the recourses of DFS.

## DFS workflow
![DFS workflow](images/general_wf.jpeg)

When a client wishes to access a file, it first contacts the naming server to obtain information about the storage server hosting it.   
After that, it communicates directly with the storage server to complete the operation.

## Client workflow
![Client workflow](images/client_wf.jpeg)

Usage of client console allows user to manipulate over the DFS, using an interface
that makes the distributed nature of the system transparent to the user.

## Naming server workflow
![NS workflow](images/ns_wf.jpeg) 

The naming server tracks the file system directory tree, and associates each file in the file system to storage servers.  
When a client wishes to perform an operation on a file, it first contacts the naming server to obtain information about the storage server hosting the file, and then performs the operation on a storage server.  
Naming servers also provide a way for storage servers to register their presence.

The naming server can be thought of as an object containing a data structure which represents the current state of the file system directory tree, and providing several operations on it. 

## Storage server workflow
![SS workflow](images/ss_wf.jpeg) 

The primary function of storage servers is to provide clients with access to file data.  
Clients access storage servers in order to read and write files.  
Storage servers must respond to certain commands from the naming server.

