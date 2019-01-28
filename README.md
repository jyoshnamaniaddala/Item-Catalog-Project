# Item-Catlog-Project #
## Project Overview ##
This is Item Catlog project which is devoloped using flask frame work,and CRUD operations are performed on the database,in this project authentication is provided using Google API's.Authenticated users can only edit,delete and update their own items.
## Why This Project? ##
Modern web applications perform a variety of functions and provide amazing features and utilities to their users; but deep down, it’s really all just creating, reading, updating and deleting data. In this project, you’ll combine your knowledge of building dynamic websites with persistent data storage to create a web application that provides a compelling service to your users.
## To Run Project ##
### PreRequisites: ###

   * [Python3]
   * [Vagrant]
   * [VirtualBox]
### To Setup Project : ###
 1.Download [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1).
 
 2.Download or Clone [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm) repository.
 
 3.If you don't have latest version of python,download and install it.

 4.Vagrant and our project should be present in the same folder

 5.To bring virtual machine online `vagrant up`.
 
 6.To login `vagrant ssh`.
 
 7.After login, move to vagrant folder `cd vagrant`
 
 8.Now,You need to install some softwares to execute the project which are,
      
   install pip
         
	 `sudo apt-get install python-pip`
        
   install flask
         
	 `pip install flask --user`
       
   install sqlalchemy
	      
	 `pip install sqlalchemy --user`
  	   
   install oauth
         
	 `pip install oauth --user`
  	   
   install oauth2client  
        
	 `pip install oauth2client --user`
       
   install requests
  	 
	 `pip install requests --user`
 
 9.After Succesfully installation of all of them,run python files.
 
 10.Run `database_setup.py` to initialise the database.
 
 11.Run `menuitems.py` to send sample data to database.
 
 12.Run `project.py` to launch application.
 
 13.open any browser and visit [http://localhost:5000](http://localhost:5000)
 
 14.Now you can access web application.
 
## JSON endpoints ##
    
    `'/state/<int:state_id>/JSON'`
    
   which is shown as,
    
 ![screenshot 183](https://user-images.githubusercontent.com/45555841/51852358-f6b3ab00-234b-11e9-8828-a7737290893e.png)
 

    `/state/<int:state_id>/menu/<int:menu_id>/JSON`
    
   which is shown as,
   
  ![screenshot 182](https://user-images.githubusercontent.com/45555841/51852636-8194a580-234c-11e9-810a-eb351b3fea83.png)
  
  
