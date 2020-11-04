#!/bin/bash

# vagrant plugin install vagrant-scp
vagrant ssh scraperserver1 -c "docker cp scraper_container:/output/ /vagrant/docker-output/"
vagrant scp scraperserver1:/vagrant/docker-output/ vm-output/
