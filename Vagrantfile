Vagrant.configure("2") do |config|
    config.vm.box = 'digital_ocean'
    config.vm.box_url = "https://github.com/devopsgroup-io/vagrant-digitalocean/raw/master/box/digital_ocean.box"

    (1..1).each do |machine| 
      config.vm.define "scraperserver#{machine}", primary: true do |server|
        server.vm.provider :digital_ocean do |provider,  override|
          override.ssh.private_key_path = '~/.ssh/id_rsa'
          provider.ssh_key_name = 'id_rsa'
          provider.token = ENV['DIGITALOCEAN_TOKEN']
          provider.image = 'docker-18-04'
          provider.region = 'fra1'
          provider.size = '2gb'
          provider.private_networking = true
          provider.monitoring = true
        end

        server.vm.synced_folder ".", "/vagrant", type: "rsync"
        server.vm.hostname = "scraperserver"
        server.vm.provision "shell", inline: <<-SHELL

          # set timezone correctly
          unlink /etc/localtime
          ln -s /usr/share/zoneinfo/Europe/Copenhagen /etc/localtime

          # system update
          apt-get update
          apt-get upgrade -y

          echo -e "\nVerifying that docker works ...\n"
          docker run --rm hello-world
          docker rmi hello-world

          echo -e "\nOpening ports ...\n"
          ufw allow 9050 # tor
          ufw allow 9051 # tor-mangement

          echo -e "\nStarting docker-compose ...\n"
          cd /vagrant
          docker-compose pull
          docker-compose up -d

          echo -e "\nVagrant setup done ..."
          # echo -e "coffee_server dashboard should be accessible at http://$(hostname -I | awk '{print $1}'):3000"

        SHELL
      end
    end
  end