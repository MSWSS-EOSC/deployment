Deployment instructions for MSWSS service
=========================================

MSWSS service is a customised version of [Galaxy project](https://galaxyproject.org/) portal deployed in EOSC cloud compute infrastructure through the [Infrastructure Manager (IM)](https://github.com/grycap/im) using either [EC3 tool](https://github.com/grycap/ec3) (for elastic computing back-end) or [IM client](https://imdocs.readthedocs.io/en/latest/client.html) (for static computing back-end). For both approaches, the deployed infrastructure consits of a front-end node with Galaxy portal, [Slurm](http://slurm.schedmd.com/) batch system, [OpenVPN](https://openvpn.net/) and [Network File System (NFS)](https://en.wikipedia.org/wiki/Network_File_System) for file sharing and a set of worker nodes (in the case of static infrastructure). EC3 tool in addition deploys a CLUES service for managing the elastic computing back-end. Generic architecture of the EC3 clusters can be found in the [EC3 documentation](https://ec3.readthedocs.io/en/latest/arch.html#general-architecture). The EC3 and IM client tools deploy the infrastructure based on the description in [RADL](https://imdocs.readthedocs.io/en/devel/radl.html) language. The RADL file describes what virtual machines will be deployed with the recipes for their contextualisation. EC3 tool comes with a set of templates which can be customised by user needs.

Prerequisities
--------------

The deployment of the MSWSS service requires the access to the Infrastructure Manager service, either the [public instance at UPV](https://imdocs.readthedocs.io/en/latest/endpoints.html) can be used or the IM service can be [deployed using Docker container](https://imdocs.readthedocs.io/en/latest/manual.html#).

It's also necessary to install [IM client](https://imdocs.readthedocs.io/en/devel/client.html) and [EC3 CLI tool](https://ec3.readthedocs.io/en/latest/intro.html#installation). 

Preparing auth.dat file
-----------------------

aut.dat file contains credential information both for access to the Infrastructure Manager service and for the access to the Cloud sites. Depending on the IM service used, either user/password or OIDC access token can be used. OIDC access tokens have limited lifetime, thus they need to be refreshed periodically (see [fedcloud client ec3 option](https://fedcloudclient.fedcloud.eu/usage.html#fedcloud-ec3-commands) for refreshing the tokens in auth.dat file). The default location of the auth.dat file is /usr/local/ec3/auth.dat.

Customising the RADL files
--------------------------

The RADL files for [static infrastructure](https://github.com/MSWSS-EOSC/deployment/tree/main/IM) and [dynamic infrastructure](https://github.com/MSWSS-EOSC/deployment/tree/main/EC3/templates) contain the recipes and settings for the testing deployment of the infrastructures for MSWSS service. The main Ansible roles used are: [grycap.galaxy](https://galaxy.ansible.com/grycap/galaxy), [grycap.slurm](https://galaxy.ansible.com/grycap/slurm), [grycap.openvpn](https://galaxy.ansible.com/grycap/openvpn) and [grycap.nfs](https://galaxy.ansible.com/grycap/nfs).

From security reasons it's recommended to customise Galaxy docker variables: GALAXY_USER_PASSWORD, GALAXY_CONFIG_ADMIN_USERS, galaxy_admin, galaxy_admin_api_key and galaxy_admin_password.

To change the number of worker nodes in the computing backend, it's necessary to modify variable NNODES and in 'deploy wn' line for static infrastructure and the variable ec3_max_instances for dynamic infrastructure.

Launching the infrastructure
----------------------------

For the static infrastructure, IM client needs to be run with the create command:

    $ im_client.py create mswss-infrastructure-static.radl

which returns the infrastructure ID. The progess of the deployment can be followed using commands:

    $ im_client.py getstate infID
    
and

    $ im_client.py getcontmsg infID

For an exhaustive list of commands and options of the IM client tools see [its documentation](https://imdocs.readthedocs.io/en/devel/client.html#invocation).

For the dynamic infrastructure, the customised mswss-infrastructure-dynamic.radl file needs to be added into ~/.ec3/templates/ directory and ec3 lauch command needs to be run.

    $ ec3 launch cluste_name mswss-infrastructure-dynamic
    
(note missing .radl suffix). The command will contact Infrastreucture Manager service and will wait until the infrastructure is deployed. EC3 deploys dedicated IM instance on front-end node and in the end it transfers the infrastructure to the newly created IM instance.

Customising the Galaxy portal
-----------------------------

When the infrastructure is running, the [customisation scripts](https://github.com/MSWSS-EOSC/deployment/tree/main/scripts) can be used to modify default Galaxy portal. IM uses for contextualisation 'cloudadm' account, which can be accessed by sshvm command:
    
    $ im_client.py sshvm infID 0
    
then the deployment files can be downloaded from github:

    $ git clone https://github.com/MSWSS-EOSC/deployment

and the scripts can be run:

    $ bash deployment/scripts/mswss_galaxy_customise.sh
 
Accessing the MSWSS instance
----------------------------

Public IP address of the newly deployed MSWSS instance can be obtained from IM using *im_client getinfo* command:

    $ im_client.py getinfo infID net_interface.1.ip
    
or it the case of dynamic infrastructure the public IP address can be obtained using *ec3 list* command:

    $ ec3 list
    
The deployed MSWSS instance is now listening on URL https://front_end_IP_address:8443 By default a self signed certificate is generated, it's recommended to switch it to a certificate provided by recognised Certification Authority for production use.

Administration of the MSWSS instance
------------------------------------

The Galaxy Docker container deployed by gycap/galaxy ansible role is based on Björn Grüning's [Galaxy Docker Image](https://github.com/bgruening/docker-galaxy-stable) so most of the admninistaration procedures documented there are valid also for MSWSS service. In addition, [Galaxy Project documentation] (https://docs.galaxyproject.org/en/master/admin/index.html) has a lot of infomration that can be useful.


