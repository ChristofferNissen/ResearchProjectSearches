#!/bin/bash

# vagrant plugin install vagrant-scp
vagrant ssh scraperserver1 -c "docker cp scraper_container:/output/ /vagrant/docker-output/"
vagrant scp scraperserver1:/vagrant/docker-output/ vm-output/

# vagrant scp <some_local_file_or_dir> [vm_name]:<somewhere_on_the_vm>
# vagrant scp [vm1]:abc.txt destFile.txt
