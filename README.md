# Task Allocation with Dockers
Trying something newer and simpler just using mqtt.  

## Branch information  
![Sequence diagram of branch]
(https://photos.google.com/share/AF1QipMoKL48FmlfDAFnA535b0jIzN6GpT6D0LoGGjDWXJZAYbyPMESlo0OVAZ1ZvgVhnw/photo/AF1QipOtvIpO-IOF3iROpfN41PARgKpztL3BYb3ArWg?key=djBZbnBneXhka0FJRzRIZEVMam93aUI0UU0yd0Vn)

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