# Task Allocation with Dockers
Trying something newer and simpler just using mqtt.  

## Branch information  
![Sequence diagram of branch]
(https://lh3.googleusercontent.com/b-DJzvYIJCo1XE1GMxJR3lmQmaVAQSy1_Psl4prRiSxTSEsI4wchMI3Dhwrs2BIt63iDDEhAcPQoDf0KMG6HoTvrbwFxW_Pe-1aM76TeI4F_2WJFpaU6-AVjhSS-CmuPdPS2koi3tAoH3SQplnhkULBEVXt2ZGOCMLPyOsuGRVD7Lydxi8PAFx9KvQAPxtQQktekNxTyJrS8Y99PibkkY5BDrJuey_dxZ-9VitRhYJn8Yp_4VBB8C2siOouG_H3F3pAR1vodVcyJC9ng54ZD2ghf-8sCwyUKkLGAJjgxDHC6Vig3xLadr2A5FylIMntCW-kqppHr-wvg5w5AfOty43xMpMuBrCTBrI_7skM1mLNSGsEgi7A_SY1-tgERus7myKjpuIhIMxC9yes64n03V17m8FK3t9c9pb5lsV1s4I7W8m8cWV2KHwLHot4p-qtCdJI5JCMTJTVmQZf4PGNLRIpRv-070g9frv2t5f81oCyCIixus8YmdW-KT0kad5188TI7NjMpGbMWxUMKyumCy_RTQwqbOC-Wpxx64VW7VqjbA8NVkF2T0VM6PHClfh1H7l6XXUqVfKBy2klVm-L5BKvYmInmo1KNgt6xS4FJbZeLFD9-9lqC5rZFxKwMEXBECwHR3IJPm7BGpMwnDYVKJW5VjTT0RHfTuj8Uo-eavglfOdHBtTpt4tbnHbKdPRzwXkDxyHOHJtHO1dq-Qfqzlcp0x3uobr-wFR64XgMw4qE=w779-h835-no)

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