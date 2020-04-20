# Task Allocation with Dockers
This code is a meant to demonstrate the middleware IFoT. The service we implemented is a decentralized route planning.  
This includes a task allocation algorithm which we developed and presented for ICFC 2020.  See the reference below.  
  
Right now this application is limited to x86 devices. Raspberry Pi or ARM builds to follow soon.  

# Decentralized Route Planning  
1. Utilizes real world data from a mid-level U.S. city.
2. Needs the following docker containers to function:  
    * [MongoDB](https://hub.docker.com/_/mongo)  
    * [MQTT](https://hub.docker.com/_/eclipse-mosquitto) Broker  
    * RSUs  
    * Broker  
3. Download the data from this link: https://drive.google.com/drive/folders/1njQ55vqPLOETDq5yGi7O16-mIau7iqIj?usp=sharing  
  
* Read our paper in the reference for more information.

# Installation  
1. git clone https://github.com/linusmotu/mqtt-dist-routing.git  
2. git branch other_host_rsu_to_rsu  
3. download the data: https://drive.google.com/drive/folders/1njQ55vqPLOETDq5yGi7O16-mIau7iqIj?usp=sharing  
4. extract the downloaded folder and place the following files into the corresponding folders:  
    * broker_data/*.pkl into mqtt-dist-routing/broker/data  
    * rsu_data/* into mqtt-dist-routing/rsu/data  

## Setting up and running MongoDB and MQTT broker  
1. Open a separate terminal.  
2. cd mqtt-dist-routing  
3. touch mongodb/mongod.log  
4. touch mqtt/mosquitto/log/mosquitto.log  
5. docker-compose -f docker-compose-mongo.yml  
  
## Setting up RSUs and Broker  
* Note, some information will differ depending on whether all containers (including mqtt and mongoDB) in a the same host.

### All in same host
1. docker-compose up  
** Again, it needs the following files in the following directories: **  
* These are based on the x, y division you use for your target area
* broker/data/X-Y-G.pkl:  Divided network graph of the target area by (x, y)
* broker/data/X-Y-rsu_arr.pkl: Generated on first run of rsu.  
* rsu/data/avg_speeds/[RSU]-avg_speeds.pkl: Historical/averaged data based on the tmc_id.  
* rsu/data/speeds/[RSU]-speeds.pkl: Actual dataframe data based on the tmc_id.  
* rsu/data/sub_graphs/XXXX-[RSU].pkl: Sub-graphs of to be distributed to each RSU, based on the total network graph.  
* rsu/data/X-Y-G.pkl: Total network graph of the target area.  
  
** Edit common/conf/GLOBAL_VARS.py **
* For the timeout duration, queue limit and neighbor levels.  

***

### Different hosts  
1. Edit broker/broker.py and rsu/rsu.py and edit the Mqtt and MongoDB addresses.  
2. Edit docker-compose.yml and at the bottom make the following changes  
* Remove external: true and replace it with driver: bridge  
* This allows your containers to share the same connection as the host machine allowing it to receive packets.  
```
networks: 
  network_test_bed:
    name: network_test_bed
    - external: true 
    + driver: bridge 
```

## Task Generation python  
* Though i changed it substatinally, so might not need to do the conda environment.  
* `conda env create -f environment.yml`  

### If want to test only on a single query  
* Run the code without any changes an it will send a query with parameters (992, 1295, 2).  
* `python -O query.py`  

### If want to test multiple queries sent concurrently  
* Comment out: send_single_query(992, 1295, 2)  
* Uncomment the following block of code:  

```
    # parser = argparse.ArgumentParser()
    # parser.add_argument("a")
    # args = parser.parse_args()
    # x, y = 5, 5
    # try:
    #     number_of_queries = int(args.a)
    #     mqttc = MyMQTTClass()
    #     mqttc.connect()
    #     mqttc.open()
    #     print("Query sent: {}".format(datetime.now().strftime("%d %b %Y %H:%M:%S.%f")))
    #     payload = {'x': x, 'y': y, 'number_of_queries': number_of_queries}
    #     print(payload)
        
    #     data = json.dumps(payload)
    #     mqttc.send(GLOBAL_VARS.SIMULATED_QUERY_TO_BROKER, data)
    #     mqttc.close()
    # except ValueError:
    #     print("Enter an integer for number of queries.")
```
* `python -O query.py XXX`  
* Where X is the number of queries you wish to send  

## Viewing results  
* For this implementation, no results will be sent, but successful results can be viewed using mongo express  
1. http://localhost:8081/db/admin/queries  
* Here you can view all the queries  
3. http://localhost:8081/db/admin/tasks  
* Here you can view all the sub-tasks which are derived from the queries  
* Change localhost to your IP

## Actual testing with iOS application  
* This is purely for evaluating the response time per individual queries.  
* <ENTER app github here>

# References  
* [rsu-base docker image](https://hub.docker.com/repository/docker/linusmotu/rsu-base)  
* This is the docker image that will be used by both RSU and Broker. It contains route planning packages as well as a modified version of networkx and osmnx.  
* Please see the link for more information.  

> J. P. Talusan, M. Wilbur, A. Dubey, and K. Yasumoto.  
> On decentralized route planning using the road side units as computing resources.  
> In 2020IEEE International Conference on Fog Computing (ICFC), 2020 (Accepted)  

# Information  
For more information, kindly send an email to <jptalusan@gmail.com>