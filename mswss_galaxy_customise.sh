#!/bin/bash
#
# MSWSS service - customisation script for Galaxy portal
#

GALAXY_EXPORT="/home/export" 
MSWSS_TOOLS="${GALAXY_EXPORT}/galaxy-central/tools_mswss"

echo; echo "*** Fetching MSWSS deployment files from Github ***"
if cd deployment; then
  git pull
else
  if ! git clone https://github.com/MSWSS-EOSC/deployment; then
    echo "Failed to get deployment files."
    exit 1
  fi
fi

cd

echo; echo "*** Customising Galaxy login page ***"
sudo cp deployment/files/welcome* $GALAXY_EXPORT/

echo; echo "*** Installing Epanet2 tool ***"
if ! wget https://github.com/USEPA/EPANET2.2/archive/refs/tags/2.2.0.tar.gz; then
  echo "Failed to get EPANET 2.2 sources."
  exit 1
fi

tar xzf 2.2.0.tar.gz

if ! gcc ./EPANET2.2-2.2.0/SRC_engines/*.c -o epanet2 -lm; then
  echo "Failed to build EPANET 2.2 binary."
  exit 1
fi

sudo mkdir -p ${MSWSS_TOOLS}/epanet2 
sudo cp epanet2 deployment/galaxy_tools/epanet2.xml ${MSWSS_TOOLS}/epanet2/
sudo chmod 755 ${MSWSS_TOOLS}/epanet2/epanet2
sudo chmod 644 ${MSWSS_TOOLS}/epanet2/epanet2.xml

echo; echo "*** Testing EPANET 2.2 ***"
${MSWSS_TOOLS}/epanet2/epanet2 ./EPANET2.2-2.2.0/User_Manual/docs/tutorial.inp test.rep

echo; echo "*** Copying file upload tool to MSWSS tools directory ***"
sudo mkdir -p ${MSWSS_TOOLS}/data_source/
sudo cp ${GALAXY_EXPORT}/galaxy-central/tools/data_source/upload* ${MSWSS_TOOLS}/data_source/

echo; echo "*** Installing tool_conf.xml file. ***"
sudo cp deployment/galaxy_tools/tool_conf.xml ${GALAXY_EXPORT}/galaxy-central/config/
sudo chmod 644 ${GALAXY_EXPORT}/galaxy-central/config/tool_conf.xml

echo; echo "*** Customising galaxy.xml config file ***"
if [ ! -f ${GALAXY_EXPORT}/galaxy-central/config/galaxy.yml ] ; then
  sudo docker exec galaxy bash -c "mv /etc/galaxy/galaxy.yml /export/galaxy-central/config/ ; ln -s /export/galaxy-central/config/galaxy.yml /etc/galaxy/galaxy.yml"
fi
sudo sed -i 's/#tool_config_file:.*/tool_config_file: tool_conf.xml/' ${GALAXY_EXPORT}/galaxy-central/config/galaxy.yml

echo; echo "*** Restarting galaxy docker container ***"
sudo docker restart galaxy

echo; echo "*** Activating auto-start of galaxy docker container at boot ***"
sudo docker update --restart unless-stopped galaxy



