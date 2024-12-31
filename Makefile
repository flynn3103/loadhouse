SHELL := /bin/bash -euxo pipefail

container_cli := docker
image_name := lakehouse-engine
deploy_env := dev
project_version := $(shell cat cicd/.bumpversion.cfg | grep "current_version =" | cut -f 3 -d " ")
version := $(project_version)
# Gets system information in upper case
system_information := $(shell uname -mvp | tr a-z A-Z)
meta_conf_file := cicd/meta.yaml
meta_os_conf_file := cicd/meta_os.yaml
group_id := $(shell id -g ${USER})
engine_conf_file := lakehouse_engine/configs/engine.yaml
engine_os_conf_file := lakehouse_engine/configs/engine_os.yaml
remove_files_from_os := $(engine_conf_file) $(meta_conf_file) CODEOWNERS sonar-project.properties CONTRIBUTING.md CHANGELOG.md assets/img/os_strategy.png
last_commit_msg := "$(shell git log -1 --pretty=%B)"
git_tag := $(shell git describe --tags --abbrev=0)
commits_url := $(shell cat $(meta_conf_file) | grep commits_url | cut -f 2 -d " ")

ifneq ($(project_version), $(version))
wheel_version := $(project_version)+$(subst _,.,$(subst -,.,$(version)))
project_name := lakehouse-engine-experimental
else
wheel_version := $(version)
project_name := lakehouse-engine
endif

# Add \ to make reg safe comparisons (e.g. in the perl commands)
wheel_version_reg_safe := $(subst +,\+,$(subst .,\.,$(wheel_version)))
project_version_reg_safe := $(subst .,\.,$(project_version))

# Condition to define the Python image to be built based on the machine CPU architecture.
# The base Python image only changes if the identified CPU architecture is ARM.
ifneq (,$(findstring ARM,$(system_information)))
python_image := $(shell cat $(meta_conf_file) | grep arm_python_image | cut -f 2 -d " ")
cpu_architecture := arm64
else
python_image := $(shell cat $(meta_conf_file) | grep amd_python_image | cut -f 2 -d " ")
cpu_architecture := amd64
endif

# Condition to define the spark driver memory limit to be used in the tests
# In order to change this limit you can use the spark_driver_memory parameter
# Example: make test spark_driver_memory=3g
#
# WARNING: When the tests are being run 2 spark nodes are created, so despite
# the default value being 2g, your configured docker environment should have
# extra memory for communication and overhead.
ifndef $(spark_driver_memory)
	spark_driver_memory := "2g"
endif

# A requirements_full.lock file is created based on all the requirements of the project (core, dq, os, azure, sftp and cicd).
# The requirements_full.lock file is then used as a constraints file to build the other lock files so that we ensure dependencies are consistent and compatible
# with each other, otherwise, the the installations would likely fail.
# Moreover, the requirement_full.lock file is also used in the dockerfile to install all project dependencies.
full_requirements := -o requirements_full.lock requirements.txt requirements_os.txt requirements_dq.txt requirements_azure.txt requirements_sftp.txt requirements_cicd.txt
requirements := -o requirements.lock requirements.txt -c requirements_full.lock
os_requirements := -o requirements_os.lock requirements_os.txt -c requirements_full.lock
dq_requirements = -o requirements_dq.lock requirements_dq.txt -c requirements_full.lock
azure_requirements = -o requirements_azure.lock requirements_azure.txt -c requirements_full.lock
sftp_requirements = -o requirements_sftp.lock requirements_sftp.txt -c requirements_full.lock
os_deployment := False
container_user_dir := /home/appuser
trust_git_host := ssh -oStrictHostKeyChecking=no -i $(container_user_dir)/.ssh/id_rsa git@github.com
ifeq ($(os_deployment), True)
build_src_dir := tmp_os/lakehouse-engine
else
build_src_dir := .
endif

build-image:
	$(container_cli) build \
		--build-arg USER_ID=$(shell id -u ${USER}) \
		--build-arg GROUP_ID=$(group_id)  \
		--build-arg PYTHON_IMAGE=$(python_image) \
		--build-arg CPU_ARCHITECTURE=$(cpu_architecture) \
		-t $(image_name):$(version) . -f cicd/Dockerfile

build-image-windows:
	$(container_cli) build \
		--build-arg PYTHON_IMAGE=$(python_image) \
        --build-arg CPU_ARCHITECTURE=$(cpu_architecture) \
        -t $(image_name):$(version) . -f cicd/Dockerfile

terminal:
	$(container_cli) run \
		-it \
		--rm \
	  	-w /app \
		-v "$$PWD":/app \
		$(image_name):$(version) \
		/bin/bash


#####################################
##### Dependency Management Targets #####
#####################################

audit-dep-safety:
	$(container_cli) run --rm \
		-w /app \
        -v "$$PWD":/app \
		$(image_name):$(version) \
		/bin/bash -c 'pip-audit -r cicd/requirements_full.lock --desc on -f json --fix --dry-run -o artefacts/safety_analysis.json'

# This target will build the lock files to be used for building the wheel and delivering it.
build-lock-files:
	$(container_cli) run --rm \
	    -w /app \
	    -v "$$PWD":/app \
	    $(image_name):$(version) \
	    /bin/bash -c 'cd cicd && pip-compile --resolver=backtracking $(full_requirements) && \
	    pip-compile --resolver=backtracking $(requirements) && \
	    pip-compile --resolver=backtracking $(os_requirements) && \
	    pip-compile --resolver=backtracking $(dq_requirements) && \
		pip-compile --resolver=backtracking $(azure_requirements) && \
		pip-compile --resolver=backtracking $(sftp_requirements)'

# We test the dependencies to check if they need to be updated because requirements.txt files have changed.
# On top of that, we also test if we will be able to install the base and the extra packages together, 
# as their lock files are built separately and therefore dependency constraints might be too restricted. 
# If that happens, pip install will fail because it cannot solve the dependency resolution process, and therefore
# we need to pin those conflict dependencies in the requirements.txt files to a version that fits both the base and 
# extra packages.
test-deps:
	@GIT_STATUS="$$(git status --porcelain --ignore-submodules cicd/)"; \
	if [ ! "x$$GIT_STATUS" = "x"  ]; then \
	    echo "!!! Requirements lists has been updated but lock file was not rebuilt !!!"; \
	    echo "!!! Run make build-lock-files !!!"; \
	    echo -e "$${GIT_STATUS}"; \
	    git diff cicd/; \
	    exit 1; \
	fi
	$(container_cli) run --rm \
		-w /app \
        -v "$$PWD":/app \
		$(image_name):$(version) \
		/bin/bash -c 'pip install -e .[azure,dq,sftp,os] --dry-run --ignore-installed'

# This will update the transitive dependencies even if there were no changes in the requirements files.
# This should be a recurrent activity to make sure transitive dependencies are kept up to date.
upgrade-lock-files:
	$(container_cli) run --rm \
	    -w /app \
	    -v "$$PWD":/app \
	    $(image_name):$(version) \
	    /bin/bash -c 'cd cicd && pip-compile --resolver=backtracking --upgrade $(full_requirements) && \
	    pip-compile --resolver=backtracking --upgrade $(requirements) && \
	    pip-compile --resolver=backtracking --upgrade $(os_requirements) && \
	    pip-compile --resolver=backtracking --upgrade $(dq_requirements) && \
		pip-compile --resolver=backtracking --upgrade $(azure_requirements) && \
		pip-compile --resolver=backtracking --upgrade $(sftp_requirements)'
