
## Chat forum app for TSOHA

In this app discussions are divided into categories that contain threads. These threads contain messages that users and admins can search by keyword.  

Users can 
-  create an account
-  send messages, modify and delete them
-  create new threads
  - when creating a new thread, the user can choose whether the thread is public or private. If the user chooses the private option, they can then select specific usernames, who will be able to see the thread besides admins. 

Admins can 
- modify threads and messages and delete them.


#### 15.11 
Due to some problems with files being public while they shouldn't have been and git history, this new repository had to be created. Therefore some of the commits that showed gradual progress are now missing from this repository.

Currently this app has features where:
- users can
  - create an account
  - login and logout
  - create new threads and choose the thread to be private or public. If the user chooses private option, they can select specific usernames, who will be able to see the thread
  - view public threads and also private, if they have permission for it. Without permission, the user will be redirected to forum index while trying to access private thread.
  
Features yet to be created:
- when creating account, username must be unique
- users can 
  - write, modify and delete messages
- instruction on how to add the specific usernames when creating a private thread
- admins can 
  - modify threads and messages and delete them.
  
##### How to test this app on Heroku
1. create two (or more if you'd like) accounts with unique usernames.
2. login and click on a category where you want to add a new thread
3. click "Luo uusi viestiketju"
4. write a title for your thread
  - if you want to create a **public thread**, go straight to step 5
  - if you want to create a **private thread** , check the box next to the words "Yksityinen". Then write usernames into the textbox (remember to be exact!) and separate them by comma *if you wrote multiple usernames*. For example, if you want multiple users: "maija, Miia, Pekka". Or if you want only one specific user to see your thread, then write that username only. For example, "maija" (even "maija," would work though). Then go to step 5
5. click "Luo uusi keskustelu"
6. now you can check if you can open your thread on your current user and then logout and check if you can open the thread on your other user(s)
