#### Netconenct Ansible 
Use the [netconnect](https://github.com/bobthebutcher/netconnect) library with ansible.  

Currently the ansible network modules use the paramiko ssh library.  
This does not work well with the way we access the network devices via jump hosts.  

The netconnect library spawns ssh sessions using the native ssh client. Therefore will 
use openssh and our ssh config file to navigate the jump host maze.  

