# Changelog

## v2.6.0 (January 22, 2025)

* Add support for installing Ansible collections on IAG servers  https://github.com/itential/itential.deployer/pull/110
* Allow core to cleanup on systemctl stop  https://github.com/itential/itential.deployer/pull/113
* Create mongo-key for replication  https://github.com/itential/itential.deployer/pull/114
* Do not overwrite the Redis Sentinel service script when installing from Remi repo  https://github.com/itential/itential.deployer/pull/111
* Escape mongo password  https://github.com/itential/itential.deployer/pull/109
* Readme updates  https://github.com/itential/itential.deployer/pull/108
* Uninstall build packages after installation  https://github.com/itential/itential.deployer/pull/105
* Update ansible-lint.yml
* Update the mongo-key tasks change from single copy to slurp  https://github.com/itential/itential.deployer/pull/118

Full Changelog: https://github.com/itential/itential.deployer/compare/v2.5.0...v2.6.0 


## v2.5.0 (December 20, 2024)

* 23.2 RHEL and Rocky 8 now install node 20 instead of 18  https://github.com/itential/itential.deployer/pull/93
* Add tasks to open prometheus exporter ports in firewalld  https://github.com/itential/itential.deployer/pull/92
* Added customer engine name  https://github.com/itential/itential.deployer/pull/94
* Change Prometheus Redis exporter to use prometheus user  https://github.com/itential/itential.deployer/pull/102
* Consolidate Redis roles  https://github.com/itential/itential.deployer/pull/99
* Redefine logic that triggers tasks for the ASA architecture  https://github.com/itential/itential.deployer/pull/101
* Update Ansible requirements in readme  https://github.com/itential/itential.deployer/pull/96
* Update galaxy version and changelog for release 2.5.0 [skip ci]

Full Changelog: https://github.com/itential/itential.deployer/compare/v2.4.1...v2.5.0 


## v2.4.1 (October 25, 2024)

* Add README for grafana role  https://github.com/itential/itential.deployer/pull/91
* Update galaxy version and changelog for release 2.4.1 [skip ci]

Full Changelog: https://github.com/itential/itential.deployer/compare/v2.4.0...v2.4.1 


## v2.4.0 (October 25, 2024)

*  Support installation of Itential artifacts using repository URL  https://github.com/itential/itential.deployer/pull/87
* Added tuned to operational packages  https://github.com/itential/itential.deployer/pull/84
* Changlog link fix  https://github.com/itential/itential.deployer/pull/83
* Fix custom adapter symlinks when patching IAP  https://github.com/itential/itential.deployer/pull/85
* Restructure prometheus playbooks and roles  https://github.com/itential/itential.deployer/pull/86
* Separate out Grafana RabbitMQ dashboard definition  https://github.com/itential/itential.deployer/pull/89
* Support auth in MongoDB exporter  https://github.com/itential/itential.deployer/pull/88
* Update galaxy version and changelog for release 2.4.0 [skip ci]
* Use rabbitmq_default_mgt_console_port in prometheus role  https://github.com/itential/itential.deployer/pull/90
* Wrong mongo version  https://github.com/itential/itential.deployer/pull/82

Full Changelog: https://github.com/itential/itential.deployer/compare/v2.3.3...v2.4.0 


## v2.3.3 (September 27, 2024)

* Fix prometheus redis exporter when auth is enabled  https://github.com/itential/itential.deployer/pull/80
* Update galaxy version and changelog for release 2.3.3 [skip ci]

Full Changelog: https://github.com/itential/itential.deployer/compare/v2.3.2...v2.3.3 


## v2.3.2 (September 25, 2024)

* Change RabbitMQ cluster node names to short hostname  https://github.com/itential/itential.deployer/pull/43
* Fix RabbitMQ env config template
* Missing replset name  https://github.com/itential/itential.deployer/pull/71
* Update galaxy version and changelog for release 2.3.2 [skip ci]

Full Changelog: https://github.com/itential/itential.deployer/compare/v2.3.1...v2.3.2 


## v2.3.1 (September 21, 2024)

* Add mongo host to tasks, do not use default  https://github.com/itential/itential.deployer/pull/69
* Add task to stop rabbitmq service in rabbitmq role  https://github.com/itential/itential.deployer/pull/70
* Fix ansible lint issues in all roles and playbooks  https://github.com/itential/itential.deployer/pull/61
* Fixed RabbitMQ installation when using custom variables  https://github.com/itential/itential.deployer/pull/67
* Fixed redis installation when using custom variables  https://github.com/itential/itential.deployer/pull/66
* Missing SSO parameter in authenticationProps  https://github.com/itential/itential.deployer/pull/58
* Non standard dirs  https://github.com/itential/itential.deployer/pull/68
* Support non-standard mongo port  https://github.com/itential/itential.deployer/pull/65
* Update galaxy version and changelog for release 2.3.1 [skip ci]

Full Changelog: https://github.com/itential/itential.deployer/compare/v2.3.0...v2.3.1 


## v2.3.0 (September 06, 2024)

* Configure SELinux when using custom IAP installation directory  https://github.com/itential/itential.deployer/pull/39
* Gateway 23.3  https://github.com/itential/itential.deployer/pull/29
* IAG task fails when SELinux is disabled  https://github.com/itential/itential.deployer/pull/44
* Rename to yml  https://github.com/itential/itential.deployer/pull/28
* Update galaxy version and changelog for release 2.3.0 [skip ci]
* added redis_db_number  https://github.com/itential/itential.deployer/pull/40
* updated mongo for 2023.2 redhat/rocky 8 to version 7  https://github.com/itential/itential.deployer/pull/38

Full Changelog: https://github.com/itential/itential.deployer/compare/v2.2.0...v2.3.0 


## v2.2.0 (August 12, 2024)

* 232 rhel/rocky8 support for platform and mongo   https://github.com/itential/itential.deployer/pull/15
* Add Code of conduct and contributing guidelines  https://github.com/itential/itential.deployer/pull/5
* Add flag to disable installation of YUM repositories  https://github.com/itential/itential.deployer/pull/12
* Add jmespath requirement to docs
* Add license file  https://github.com/itential/itential.deployer/pull/4
* Add notes to docs about RabbitMQ not being required for IAP 2023.2 and newer
* Add processManagement section to mongod.conf template
* Add specs for control node to README  https://github.com/itential/itential.deployer/pull/19
* Add support for installing adapters from zip archive
* Add variables for http server threads (IAG) and IAG adapter token timeout (IAP)  https://github.com/itential/itential.deployer/pull/14
* Added conditional to prevent RabbitMQ install when iap_release is less than 2023.2
* Correct lint issues  https://github.com/itential/itential.deployer/pull/17
* Create ansible-lint.yml
* Create publish_ansible_collection.yml
* Create updateChangelog.yml
* Fix IAG adapter service config base_path
* Fix IAP Vault token location and permissions  https://github.com/itential/itential.deployer/pull/23
* Fix MongoDB tools package list for IAP v2021.1 installs
* Fix iag_http_server_threads syntax issue in IAG properties template  https://github.com/itential/itential.deployer/pull/27
* HAProxy timeout settings update  https://github.com/itential/itential.deployer/pull/7
* Hashicorp read only support  https://github.com/itential/itential.deployer/pull/11
* Improve logging  https://github.com/itential/itential.deployer/pull/10
* Lint issues  https://github.com/itential/itential.deployer/pull/18
* Lint issues  https://github.com/itential/itential.deployer/pull/20
* Lint issues  https://github.com/itential/itential.deployer/pull/22
* Prometheus  https://github.com/itential/itential.deployer/pull/24
* Re-factor Running the Deployer section of README
* Rename documents to docs  https://github.com/itential/itential.deployer/pull/6
* Support MongoDB installs on aarch64 servers
* Update CHANGELOG.md
* Update Ports and Networking section in README  https://github.com/itential/itential.deployer/pull/16
* Update README to remove instructions for installing from Itential Ansible Galaxy  https://github.com/itential/itential.deployer/pull/26
* Update galaxy version and changelog for release 2.2.0 [skip ci]
* Update publish_ansible_collection.yml
* addded support for 23.2 on RHEL 8 for Gateway install  https://github.com/itential/itential.deployer/pull/13
* added license to galaxy file  https://github.com/itential/itential.deployer/pull/8
* delete file
* moved vault_port to common_vars  https://github.com/itential/itential.deployer/pull/9
* removed Terraform
* update changelog script
* updated iag_guide.md

Full Changelog: https://github.com/itential/itential.deployer/compare/v2.1.2...v2.2.0 


## v2.1.2 (April 22, 2024)

* Create release v2.1.2
* Fix download adapters when custom adapters list is empty
* Readme updates
* Update CI build pipeline to fetch all tags
* Update links in mongodb role documentation

Full Changelog: https://github.com/itential/itential.deployer/compare/v2.1.1...v2.1.2 


## v2.1.1 (April 10, 2024)

* Add README documents for each component
* Add missing variables and examples to documentation
* Add script to create changelog when CI build pipeline is executed
* Create release v2.1.1
* Update docs with variables required for installing Redis from source
* Update example inventory hostnames in README
* Update selinux role to configure SELinux only if it is enabled

Full Changelog: https://github.com/itential/itential.deployer/compare/v2.1.0...v2.1.1 


## v2.1.0 (March 26, 2024)

* Add support for installing Redis from source
* Create release 2.1.0
* Fix rabbitmq playbook when clustering/ssl is enabled
* Update README document
* Update Redis and RabbitMQ roles to use configurable usernames/passwords
* Update Redis settings to support IAP 23.2

Full Changelog: https://github.com/itential/itential.deployer/compare/v2.0.2...v2.1.0 


## v2.0.2 (March 25, 2024)

* Rename patch IAP/IAG playbooks to support calling from collection

Full Changelog: https://github.com/itential/itential.deployer/compare/v2.0.1...v2.0.2 


## v2.0.1 (March 21, 2024)

* Add offline install functionality
* Add support for IAG and IAP 2023.2
* Create release 2.0.0
* Create release 2.0.1
* Fix CI pipeline
* Fix profile name when using advanced config (HA/DR)
* Move playbooks to playbooks directory
* Update .gitlab-ci.yml file

Full Changelog: https://github.com/itential/itential.deployer/compare/v1.5.0...v2.0.1 


## v1.5.0 (December 15, 2023)

* Add Gateway task to add HTTP port to SELinux
* Add Vault task to configure ports in firewalld
* Add redis_tls common default var
* Add support for installing IAP from tar file
* Added files to install redis from repo
* Change patch playbooks to include common vars via role
* Changes to support bring-your-own-dependency
* Create release 1.5.0
* Move dup vars to common_vars redis
* Remove dup RabbitMQ vars
* Remove duplicate IAP vars
* Remove duplicate MongoDB variables
* Remove duplicate Vault vars
* Update IAG module and collection paths
* Update SELinux configurations for IAP/Redis/MongoDB
* Vars cleanup

Full Changelog: https://github.com/itential/itential.deployer/compare/v1.4.0...v1.5.0 


## v1.4.0 (October 26, 2023)

* Bump galaxy collection version
* Bump redis version to 7.0.14
* Check for IAG adapter and do not add it if already present
* Fixed mongo backup issues, removing bin file from remote when finished
* Minor changes for rabbit
* Minor optimizations

Full Changelog: https://github.com/itential/itential.deployer/compare/v1.3.0...v1.4.0 


## v1.3.0 (October 02, 2023)

* Add IAG HTTPS/SSL configuration
* Added missing LDAP and other properties
* Create release 1.3.0
* Fixed Mongo tools yum reference for rhel8
* Support mongodb replication with no arbiter

Full Changelog: https://github.com/itential/itential.deployer/compare/v1.2.1...v1.3.0 


## v1.2.1 (September 22, 2023)

* Add ansible-pylibssh to pip install for IAG 2023.1

Full Changelog: https://github.com/itential/itential.deployer/compare/v1.2.0...v1.2.1 


## v1.2.0 (September 22, 2023)

* Add flag for determining whether to use rsync for artifact uploads

Full Changelog: https://github.com/itential/itential.deployer/compare/v1.1.0...v1.2.0 


## v1.1.0 (September 19, 2023)

* Add flag to disable binding to v6 interfaces (rabbitmq/redis)
* Add initial version of CI pipeline
* Add tls options to mongo connection string
* Added HA policy to iap vhost, other best practices in rabbit conf
* Added correct redis ACL
* Added new role that can upgrade IAG
* Added tasks to downgrade markupsafe after jinja install
* Changed and added some best practice rabbit settings
* Corrected ACL list
* IAG adapters will be built based on gateway group members
* Modifying rabbit HA policy to match ISD standards
* Release v1.1.0
* Remove mongo init
* Removed mongodb_init role, tasks moved to mongo and platform roles

Full Changelog: https://github.com/itential/itential.deployer/compare/v1.0.0...v1.1.0 


## v1.0.0 (August 21, 2023)

* Change pip install to use builtin module
* Changed default iap log dir to match already established docs and practices
* Fix restart mongo task in mongo auth
* Fixed syntax error
* Initial commit
* Initial version

