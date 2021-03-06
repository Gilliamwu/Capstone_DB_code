# Capstone_DB_code
This repository is for Singapore University of Technology and Design Batch of 2018, team S05- Performance Rotors - AEOLUS

## Prerequisite:
### Linux supported only

### MySQL Server
Currently used: 5.6
Server configuration requirement:
Please enable binlog. 
You can update MySQL configuration file (my.ini or my.cnf)  by adding the following lines to the [mysqld] section (the Server Section).
```
log-bin=bin.log
log-bin-index=bin-log.index
max_binlog_size=100M
binlog_format=row
socket=mysql.sock
```

Then when you check mysql status from server by 
```
mysql>  select variable_value as "BINARY LOGGING STATUS (log_bin) :: " 
    from information_schema.global_variables where variable_name='log_bin';
+-------------------------------------+
| BINARY LOGGING STATUS (log_bin) ::  |
+-------------------------------------+
| ON                                  |
+-------------------------------------+
```
and 
```
mysql> select variable_value as "BINARY LOG FORMAT (binlog_format) :: " 
    from information_schema.global_variables where variable_name='binlog_format';
+---------------------------------------+
| BINARY LOG FORMAT (binlog_format) ::  |
+---------------------------------------+
| ROW                                   | # Very important because we want to see the update events of specific table
+---------------------------------------+
```
To know more about the binlog status, you could use following commands in server to know more 
```
mysql> show binary logs;
+------------+-----------+
| Log_name   | File_size |
+------------+-----------+
| bin.000001 |       144 |
| bin.000002 |       239 |
| bin.000003 |       319 |
| bin.000004 |       107 |
+------------+-----------+
```

Also, for the main server, make sure the main server id is 1. You can check server id by trying:
```
select @@server_id;
```
If it is not, you can change .cnf or .ini file, find the line with server-id and change to this:
```
server-id	= 1
```

### Python: currently used 3.6. Not supportive for python 3.2
packages required listed in requirements.txt:
```
Flask==1.0.2
Flask_API==1.0
Flask_SQLAlchemy==2.3.2
mysql_connector_repackaged==0.3.1
mysql_replication==0.18 # requires binlog enable
```

### GPU enabled:
The project requires:
* Linux GCC>=4.9
* GPU with CC >= 3.0:
* cuDNN v5-v7
* CUDA >= 7.5

## How to run
1. Set up the aeolus from end windows app
2. From this repository, edit settings.py, edit the location you want to put all the video received from front end; 
  file folder to save the sliced frames from video;
  the output from Machine Learning result;
  the MySQL connection details
3. Run ```make``` in terminal to compile the source code for darknet.
4. run main.py to start the backend machine learning processor, which will connect to MySQL databased and find all the newly added roles from the time you start server
4. run application.py to set up the flask server.

## Special notes
* binlog could grow very large, and then fetching binlog will take longer time for our ML backend. To save the time for the backend ML server, you could run following command to delete all the past binlog files (cache of update, delete, create events in server)
```
reset master;
```

* Machine learning is based on this model
"You Only Look Once: Unified, Real-Time Object Detection (versions 2 & 3)" (YOLO)
https://github.com/AlexeyAB/darknet

### other links:
Self labelled crack dataset: 
Yolo self-training repository: 

### Reference
Machine learning:
YOLO

Crack-forest: https://github.com/cuilimeng/CrackForest-dataset

Crack_Detection_Database https://www.irit.fr/~Sylvie.Chambon/Crack_Detection_Database.html


