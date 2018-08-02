# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "operator/django-heroku"
  config.vm.box_version = "1.0"

  config.vm.network "forwarded_port", host_ip: "127.0.0.1", guest: 8085, host: 8085

  config.vm.provider "virtualbox" do |v|
    v.memory = 4048
    v.cpus = 2
  end

  config.vm.provision "shell", inline: <<-SHELL
    # Update and upgrade the server packages.
    sudo apt-get update
    sudo apt-get -y upgrade
    # Set Ubuntu Language
    sudo locale-gen en_GB.UTF-8
    # Install Python, SQLite and pip
    sudo apt-get install -y python3-dev sqlite python-pip
    # Upgrade pip to the latest version.
    sudo pip install --upgrade pip
    # Install and configure python virtualenvwrapper.
    sudo pip install virtualenvwrapper
	# Install Curl and PostgreSQL
	sudo apt-get install -y curl postgresql-common postgresql libpq-dev
	sudo su postgres -c "createuser vagrant -s"
	# Install python tools
	sudo apt-get -y install python3-setuptools
	sudo easy_install3 pip
	sudo apt-get -y install python3-dev
	sudo apt-get -y install python-django
	#install Git
	sudo apt-get -y install git
	#Install all pip packages
	sudo -H pip install Django==1.8.4
	sudo -H pip install dj-database-url==0.3.0
	sudo -H pip install dj-static==0.0.6
	sudo -H pip install django-postgrespool==0.3.0 
	sudo -H pip install gunicorn==19.3.0
	sudo -H pip install SQLAlchemy==1.0.8
	sudo -H pip install whitenoise==2.0.3
	sudo -H pip install django-toolbelt==0.0.1
	sudo -H pip install static3==0.6.0
	sudo -H pip install newrelic==2.54.0.41
	#install Heroku toolbelt. The ubuntu package doesn't work, so im running the Standalone version which requires aliases and manual update
	wget -O- https://toolbelt.heroku.com/install.sh | sh
	echo 'alias heroku=/usr/local/heroku/bin/heroku' >> ~/.bashrc
	echo 'alias heroku=/usr/local/heroku/bin/heroku' >> ~/.profile
	#Updated the heroku toolbelt to V4.
	/usr/local/heroku/bin/heroku plugins:install
	# Last row gives:
	# $ ���    Missing argument: NAME
	# $ !    error installing plugin
	# It installs all required plugins except forego
	# Running [$ heroku local] will install the last plugin
	
    if ! grep -q VIRTUALENV_ALREADY_ADDED /home/vagrant/.bashrc; then
        echo "# VIRTUALENV_ALREADY_ADDED" >> /home/vagrant/.bashrc
        echo "WORKON_HOME=~/.virtualenvs" >> /home/vagrant/.bashrc
        echo "PROJECT_HOME=/vagrant" >> /home/vagrant/.bashrc
        echo "source /usr/local/bin/virtualenvwrapper.sh" >> /home/vagrant/.bashrc
    fi
  SHELL
end