rateyourclub
============

    
production: safe-escarpment-9258
staging: peaceful-everglades-8311

    heroku git:remote -a staging peaceful-everglades-8311
    
    git remote rename heroku production
    

Deploy on staging:

    git push staging feature_branch:master
    
Deploy on production:

    git push production master:master
    
    
Sync Database
<http://stackoverflow.com/questions/6930624/how-can-i-make-my-staging-and-production-have-the-same-data-heroku>

    heroku addons:add pgbackups --remote staging
    heroku addons:add pgbackups --remote production
    heroku pgbackups:capture --remote production
    heroku pgbackups:restore DATABASE `heroku pgbackups:url --remote production` --remote staging

