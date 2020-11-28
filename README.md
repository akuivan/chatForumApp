
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
  
  
#### 28.11 
All the features are now created and should be working. Now what needs to be done is:
- code refactoring
- modify appearance
- maybe some small tweaks to make the UI better
  
##### How to test [this app](https://tshoha-chatforumapp.herokuapp.com) on Heroku  
1. To test users, you can create your own account(s) or use Pekka (password: kissa123)
2. To test admin, you can log in with username "admin" and password "admin1"
- remember to also logout when testing different users/admin





