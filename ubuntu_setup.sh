#http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create_deploy_Python_django.html
function set1(){
  yum install -y python27 python27-devel
  yum install -y gcc mysql mysql-devel
  yum install -y python-devel
  yum install -y git
  easy_install pip
  pip install -r requirements.txt
}
function setup2(){
  #http://www.krishnasunuwar.com.np/2012/12/running-django-app-in-amazon-aws-ec2/
  sudo apt-get install mysql-server mysql-client
  sudo apt-get install apache2
  sudo apt-get install libapache2-mod-python
  #sudo apt-get install python-mysqldb
  sudo apt-get install libapache2-mod-wsgi
  sudo apt-get install git-core
  easy_install pip 
  sudo pip install virtualenv
  virtualenv ~/ENV; cd ~/ENV && source bin/activate && pip install -r requirements.txt
}
