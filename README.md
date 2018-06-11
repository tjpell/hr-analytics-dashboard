# Employee Churn Prediction Dashboard
#### Taylor Pellerin  

----------
  
  
### Hosted Python Model for HR Partner: Employee Churn
The purpose of this application is to spin up a light weight Flask 
application, allowing the user to intuitively interact and predict 
whether or not a particular employee will churn, based on their 
existing, or fabricated, feature vector. This module also allows 
for the user to retrain an xgb classifier, for the event that we
get enough new data and want a new model.

Observations can be sourced from one of two places:
1. Input patient number from the HR_sqlite.db database
2. Create patient record in form on a web interface  
  
  
### Install and Launch Instructions:
For the first time running on a machine:
1. `$ cd EmployeeChurn`
2. `$ bash cold_deploy.sh`
3. Pop open your browser to http://0.0.0.0:8080 and enjoy

Note: If you are having trouble, just run each line of cold_deploy.sh separately
in the terminal.

For any subsequent times, just run:  
`$ bash deploy.sh`


### To close app:
1. press `ctrl + C`
2. `$ source deactivate emp_churn`


### To destroy application and environment:
`$ bash makeclean.sh`


### Repository structure
Repositories  
`templates/` and `static/` contain all front end resources  
`encodings/` and `models/` contains the model binaries  
`data/` contains the raw csvs, used for training initial model - note that the data is not here as of now, you'll need to download it  
`predictions/` contains test predictions (not essential)  
`scripts/` contains all `.sh` (shell) scripts used for launching and destroying the application  

Other files  
`index.py` and `wsgi.py` serve the application in testing and production, respectively.  
`sqlite_*.py` and `database_operations.py` contain the database interactions  
`forms.py` serves web forms  
`HRmodel.py` handles model interactions  
`HR_sqlite.db` is the sqlite database, containing the full dataset. Not currently in repo, but instructions and script to create will be coming soon  

### Data
All data provided on kaggle. To doenload, run or visit the following:  
! kaggle competitions download -c employee-churn-prediction  
https://www.kaggle.com/c/employee-churn-prediction/data  
## EDIT: Dataset is no longer public. I will look into this, and likely replace with a new and publicly available dataset  

### Technical Choices
1. A Flask app was preferred as it provides a quick to prototype and 
otherwise straightforward to use API.  
2. Flask WTF was used to handle input forms, due to integrability with base Flask.  
3. SQLAlchemy was used to handle database interactions, as it operationalizes
a process that would otherwise require writing string queries.  
4. An HTML template was used for generating the web page, creating a friendly
and nicer looking user experience, without inhibiting functionality.  

## Todo:
### Testing and Logging
1. Unit testing was done in order to capture cases where an employee did not exist
or a field was left empty when trying to generate a prediction.  
    - If these occur, a redirect is incurred and a banner message appears.  
    - This process should generalize well regardless of updates to the model  
2. When the user provides slightly incorrect inputs to some of the forms (in the 
form of empty fields), the module incurs a redirect and flash message.  
    - We also use fuzzy matching in some of these cases, to allow for 
    a smoother user experience and less redirects.  
3. As of now, there is no logging of app interaction.  
    - We ought to keep track of use of the application.    
        - Perhaps we require a login page so that we can track who is actually 
        using the application.   
        - Of course we anticipate that not all employees 
        should have access to this app, so this is a good next step.  
        - Further, a login page prevents external people from using the app, in the
        event that it is ever launched on a server rather than local computer, which
        is a potential security concern.  
        
        
### Tracking model performance
- We want to track the model parameters and performance over time.  
- A database may not make sense, for the event of tweaking a new parameter
or considering a new loss function, or some other as of yet unforeseen change  
- Currently, we can just binarize and pickle model objects, named for the time 
and day that they are trained so that we can recover most recent model.  


### Features to Add Given More Time
1. Cleaner UI with more compact web forms  
2. Write crontab or other scheduler for cycling model in the back end.  
3. Track model performance and parameters, such as the seed used for 
sampling the data, data size, and other factors to make retraining the 
model as reproducible as possible.  
4. We should explicitly warn the user when fuzzy matching is happening, 
anticipating an unlucky typo when inputting data.  
5. A page that that reports model performance over time.  
6. Rather than reload model each time we predict, persist the object in 
the back end.  
7. Ensure that directories exist prior to writing files to them.  

