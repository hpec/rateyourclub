rateyourclub
============

    
production: safe-escarpment-9258 

<http://www.calbeat.com>

staging: peaceful-everglades-8311 

<http://staging.calbeat.com>

    
###Setup

    heroku git:remote -a staging peaceful-everglades-8311
    
    git remote rename heroku production
    

###Deploy on staging:

    git push staging feature_branch:master
    
###Deploy on production:

    git push production master:master
    
    
###Sync Database

    heroku addons:add pgbackups --remote staging
    heroku addons:add pgbackups --remote production
    heroku pgbackups:capture --remote production
    heroku pgbackups:restore DATABASE `heroku pgbackups:url --remote production` --remote staging

