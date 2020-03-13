# Task Allocation with Dockers
Trying something newer and simpler just using mqtt.  

## Branch information  
+-------+                  +---------+                    +-------+                      +-------+                       
| User  |                  | Broker  |                    | RSU1  |                      | RSU2  |                       
+-------+                  +---------+                    +-------+                      +-------+                       
    |                           |                             |                              |                           
    | Send query (s, d, t)      |                             |                              |                           
    |-------------------------->|                             |                              |                           
    |                           |                             |                              |                           
    |                           | Prepare query sub-tasks     |                              |                           
    |                           |------------------------     |                              |                           
    |                           |                       |     |                              |                           
    |                           |<-----------------------     |                              |                           
    |                           |                             |                              |                           
    |                           | Prepare allocation          |                              |                           
    |                           |-------------------          |                              |                           
    |                           |                  |          |                              |                           
    |                           |<------------------          |                              |                           
    |                           |                             |                              |                           
    |                           | Send sub-task 1             |                              |                           
    |                           |---------------------------->|                              |                           
    |                           |                             |                              |                           
    |                           | Send sub-task 2             |                              |                           
    |                           |----------------------------------------------------------->|                           
    |                           |                             |                              |                           
    |                           |                             | Find route of sub-task 1     |                           
    |                           |                             |-------------------------     |                           
    |                           |                             |                        |     |                           
    |                           |                             |<------------------------     |                           
    |                           |                             |                              |                           
    |                           |                             | Send next node               |                           
    |                           |                             |----------------------------->|                           
    |                           |                             |                              |                           
    |                           |                  Send route |                              |                           
    |                           |<----------------------------|                              |                           
    |                           |                             |                              |                           
    |                           |                             |                              | Find route of sub-task 2  
    |                           |                             |                              |-------------------------  
    |                           |                             |                              |                        |  
    |                           |                             |                              |<------------------------  
    |                           |                             |                              |                           
    |                           |                             |                   Send route |                           
    |                           |<-----------------------------------------------------------|                           
    |                           |                             |                              |                           
    |                           | Collect route               |                              |                           
    |                           |--------------               |                              |                           
    |                           |             |               |                              |                           
    |                           |<-------------               |                              |                           
    |                           |                             |                              |                           
    |              Return route |                             |                              |                           
    |<--------------------------|                             |                              |                           
    |                           |                             |                              |                           

## MongoDB and MQTT broker  
1. Open a separate terminal.  
2. touch mongodb/mongod.log  
3. touch mqtt/mosquitto/log/mosquitto.log  
4. docker-compose -f docker-compose-mongo.yml  
  
## RSUs and Broker  
1. docker-compose up  
** However needs the following files in the following directories: **  
* These are based on the x, y division you use for your target area
* broker/data/X-Y-G.pkl:  Divided network graph of the target area by (x, y)
* broker/data/X-Y-rsu_arr.pkl: Generated on first run of rsu.  
* rsu/data/avg_speeds/[RSU]-avg_speeds.pkl: Historical/averaged data based on the tmc_id.  
* rsu/data/speeds/[RSU]-speeds.pkl: Actual dataframe data based on the tmc_id.  
* rsu/data/sub_graphs/XXXX-[RSU].pkl: Sub-graphs of to be distributed to each RSU, based on the total network graph.  
* rsu/data/X-Y-G.pkl: Total network graph of the target area.  
  
** Edit common/conf/GLOBAL_VARS.py **
* For the timeout duration, queue limit and neighbor levels.  
  
## Task Generation python  
* Though i changed it substatinally, so might not need to do the conda environment.  
1. conda env create -f environment.yml  
2. python -O query.py XXX  

# References  
* https://hub.docker.com/repository/docker/linusmotu/rsu-base  