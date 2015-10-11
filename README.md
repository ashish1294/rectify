Rectify, Engineer 2015, NITK
============================

This is a repo for the Rectify App that will be used in Engineer 2015.

Description
-----------
This is a mini codeforces-like online judge that was developed for the rectify event. Problems are shown to the users. They can submit the solution which is judged by the server. After the coding phase, users can view other's solutions and can hack it by providing an input data for which it may fail.

Features
--------
* Celery Task Broker for judging solutions along with Rabbit MQ as AMPQ
* Online Javascript based IDE for coding on prablem page ~ Ace9
* Javascript based syntax highlighter for diplaying code ! ~ highlightjs
* Material Design front end ~ using Materialize
* Parallax effect home page
* MySQL database as back-end data storage solution

Requirements
------------
* django >= 1.8 (pip install django)
* python-mysql (pip install mysql)
* celery (apt-get install celery)
* django-celery (pip install django-celery)
* rabbitmq (apt-get instal rabbitmq-server)
* mysql-server (apt-get install mysql-server)

Features to be added
--------------------
* Add a "Edit Solution" button on each solution view page so that user can edit the previously edited solutions directly (feedback from 2015)
* Make a special admin-only page to see all submission / hack / solution ~ very important
* Judge all solutions within a docker container that can enforce other restrictions on the solution !
* Add a rejudge task fro both solution and hack
* Check for empty input data before processing
* Commenting on each problem
* Chatbox with admin
* Admin account
* Support Other Languages apart from cpp. Just use different compiler for each language and use it during judging of tasks
* Make custom admin panel to add questions which compiles the problem setters code so that it is ensured that code is right
* Implement Memory Limit ~ It can cause system thrashing !!! ~ very important
* Write Load test for solution judging
* Write Django tests for all the functionalities
* Mechanism to delete a challenge / submission such that all it's effects are reverted correctly without any cosistency issues
* Make a new Challenge Result class ~ proposed (It will be helpful in case of any discrepency !)
* Use Marksown field for problem addition by problem setters
* Javascript based toggle between flow-text class in problem statement paragraph (It will decrease or increase size of text based on user's need)

Deployment Steps
----------------

* Install dependencies
* Use Apache (personal choice)/ Nginx for creating WSGI Daemon and serving django-app
* Run RabbitMQ AMPQ task broker
* Run celery worker nodes
* Run MySQL Server
* Change the MetaData with contest time in Django Admin Panel
* Start Server
* Run system test at the end of contest using custom command !!

Developer
---------

Ashish Kedia - IT Batch of 2016, NITK Surathkal