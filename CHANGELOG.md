# Changelog

## v2.1.2 (April 22, 2024)

* Create release v2.1.2
* Fix download adapters when custom adapters list is empty
* Readme updates
* Update CI build pipeline to fetch all tags
* Update links in mongodb role documentation

Full Changelog: https://github.com/itential/nickAtest/compare/v2.1.1...v2.1.2 


## v2.1.1 (April 10, 2024)

* Add README documents for each component
* Add missing variables and examples to documentation
* Add script to create changelog when CI build pipeline is executed
* Create release v2.1.1
* Update docs with variables required for installing Redis from source
* Update example inventory hostnames in README
* Update selinux role to configure SELinux only if it is enabled

Full Changelog: https://github.com/itential/nickAtest/compare/v2.1.0...v2.1.1 


## v2.1.0 (March 26, 2024)

* Add support for installing Redis from source
* Create release 2.1.0
* Fix rabbitmq playbook when clustering/ssl is enabled
* Update README document
* Update Redis and RabbitMQ roles to use configurable usernames/passwords
* Update Redis settings to support IAP 23.2

Full Changelog: https://github.com/itential/nickAtest/compare/v2.0.2...v2.1.0 


## v2.0.2 (March 25, 2024)

* Rename patch IAP/IAG playbooks to support calling from collection

Full Changelog: https://github.com/itential/nickAtest/compare/v2.0.1...v2.0.2 


## v2.0.1 (March 21, 2024)

* Add offline install functionality
* Add support for IAG and IAP 2023.2
* Create release 2.0.0
* Create release 2.0.1
* Fix CI pipeline
* Fix profile name when using advanced config (HA/DR)
* Move playbooks to playbooks directory
* Update .gitlab-ci.yml file

Full Changelog: https://github.com/itential/nickAtest/compare/v1.5.0...v2.0.1 


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

Full Changelog: https://github.com/itential/nickAtest/compare/v1.4.0...v1.5.0 


## v1.4.0 (October 26, 2023)

* Bump galaxy collection version
* Bump redis version to 7.0.14
* Check for IAG adapter and do not add it if already present
* Fixed mongo backup issues, removing bin file from remote when finished
* Minor changes for rabbit
* Minor optimizations

Full Changelog: https://github.com/itential/nickAtest/compare/v1.3.0...v1.4.0 


## v1.3.0 (October 02, 2023)

* Add IAG HTTPS/SSL configuration
* Added missing LDAP and other properties
* Create release 1.3.0
* Fixed Mongo tools yum reference for rhel8
* Support mongodb replication with no arbiter

Full Changelog: https://github.com/itential/nickAtest/compare/v1.2.1...v1.3.0 


## v1.2.1 (September 22, 2023)

* Add ansible-pylibssh to pip install for IAG 2023.1

Full Changelog: https://github.com/itential/nickAtest/compare/v1.2.0...v1.2.1 


## v1.2.0 (September 22, 2023)

* Add flag for determining whether to use rsync for artifact uploads

Full Changelog: https://github.com/itential/nickAtest/compare/v1.1.0...v1.2.0 


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

Full Changelog: https://github.com/itential/nickAtest/compare/v1.0.0...v1.1.0 


## v1.0.0 (August 21, 2023)

* Change pip install to use builtin module
* Changed default iap log dir to match already established docs and practices
* Fix restart mongo task in mongo auth
* Fixed syntax error
* Initial commit
* Initial version

