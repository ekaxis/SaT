#!/usr/bin/env sh
#
# GNU General Public License v3.0
# Permissions of this strong copyleft license are conditioned on making available complete source code of licensed works and modifications, 
# which include larger works using a licensed work, under the same license.
# Copyright and license notices must be preserved. Contributors provide an express grant of patent rights.
#
# executar com:
#
# bash <(curl -Ss http://kickstart.sh)
#
# este escript vai:
#
# 1. download files from the repository on github
#
# 2. install dependencies
#
# 3. install tool on the system /etc/sat by default
#

# links externos
REPOSITORY="https://github.com/ekaxis/SaT.git"
INSTALL_PATH="/etc/sat"
# ------------------------------------------------------------------------------------------------
# identify package manager
package_manager=
if [ ! -z $(command -v apt-get 2> /dev/null) ]; then
    package_manager="apt-get"
    hidden_install="-qq"
elif [ ! -z $(command -v dnf 2> /dev/null) ]; then
    package_manager="dnf"
    hidden_install="-q"
elif [ ! -z $(command -v yum 2> /dev/null) ]; then
    hidden_install="-q"
fi
if [ -z $package_manager ]; then
    fatal "unsupported distribution"
fi
# ------------------------------------------------------------------------------------------------
# function for create temp directory for install depedencies
create_tmp_directory() {
    # Check if tmp is mounted as noexec
    if grep -Eq '^[^ ]+ /tmp [^ ]+ ([^ ]*,)?noexec[, ]' /proc/mounts > /dev/null 2>&1; then
        pattern="$(pwd)/SaT-XXXXXX"
    else
        pattern="/tmp/SaT-XXXXXX"
    fi

    mktemp -d $pattern
}
TMPDIR=$(create_tmp_directory)
cd "${TMPDIR}" || exit 1
# ------------------------------------------------------------------------------------------------
# library functions copied from packaging/installer/functions.sh
setup_terminal() {
	TPUT_RESET=""
	TPUT_YELLOW=""
	TPUT_WHITE=""
	TPUT_BGRED=""
	TPUT_BGGREEN=""
	TPUT_BOLD=""
	TPUT_DIM=""
	# is stderr on the terminal? If not, then fail
	test -t 2 || return 1

	if command -v tput > /dev/null 2>&1; then
		if [ $(($(tput colors 2> /dev/null))) -ge 8 ]; then
			# Enable colors
			TPUT_RESET="$(tput sgr 0)"
			TPUT_YELLOW="$(tput setaf 3)"
			TPUT_WHITE="$(tput setaf 7)"
			TPUT_BGRED="$(tput setab 1)"
			TPUT_BGGREEN="$(tput setab 2)"
			TPUT_BOLD="$(tput bold)"
			TPUT_DIM="$(tput dim)"
		fi
	fi
	return 0
}
# chamar função com variáveis de ambiente
setup_terminal || echo > /dev/null
# ------------------------------------------------------------------------------------------------
# váriaveis de ambiente
export VERSION="SaT tool [1.0.0v] by ekaxis"
# ------------------------------------------------------------------------------------------------
# informações do sistema
systeminfo() {
    export SYSTEM="$(uname -s 2> /dev/null || uname -v)"
    export OS="$(uname -o 2> /dev/null || uname -rs)"
    export MACHINE="$(uname -m 2> /dev/null)"

    echo "${TPUT_BOLD}${TPUT_WHITE}System            ${TPUT_RESET}: ${SYSTEM}"
    echo "${TPUT_BOLD}${TPUT_WHITE}Operating System  ${TPUT_RESET}: ${OS}"
    echo "${TPUT_BOLD}${TPUT_WHITE}Machine           ${TPUT_RESET}: ${MACHINE}"

	if [ "${OS}" != "GNU/Linux" ] && [ "${SYSTEM}" != "Linux" ]; then
    	warning "script version does not work well for your ${SYSTEM} - ${OS} system."
	fi
}
# chamar função
echo $VERSION
systeminfo
# ------------------------------------------------------------------------------------------------
# erro crítico
fatal() {
	printf >&2 "${TPUT_BGRED}${TPUT_WHITE}${TPUT_BOLD} ABORTED ${TPUT_RESET} ${*} \n\n"
	exit 1
}
# ------------------------------------------------------------------------------------------------
# operação bem sucedida
run_ok() {
	printf >&2 " ${TPUT_BGGREEN}${TPUT_WHITE}${TPUT_BOLD} OK ${TPUT_RESET} \n\n"
}
ok_dependencie() {
    printf >&2 "${TPUT_BGGREEN}${TPUT_WHITE}${TPUT_BOLD} OK ${TPUT_RESET} ${*}\n"
}
# ------------------------------------------------------------------------------------------------
# falha na operação
run_failed() {
  printf >&2 "${TPUT_BGRED}${TPUT_WHITE}${TPUT_BOLD} FAILED ${TPUT_RESET} \n\n"
}
# ------------------------------------------------------------------------------------------------
# função para exibir barra de progresso
progress() {
    echo >&2 " --- ${TPUT_DIM}${TPUT_BOLD}${*}${TPUT_RESET} --- "
}
# ------------------------------------------------------------------------------------------------
# função para executar comando na máquina
ESCAPED_PRINT_METHOD=
if printf "%q " test > /dev/null 2>&1; then
    ESCAPED_PRINT_METHOD="printfq"
fi
# formatter output
escaped_print() {
    if [ "${ESCAPED_PRINT_METHOD}" = "printfq" ]; then
        printf "%q " "${@}"
    else
        printf "%s" "${*}"
    fi
    return 0
}
run_logfile="${TMPDIR}/run.log"
run() {
    local user="${USER--}" dir="${PWD}" info info_console
    if [ "${UID}" = "0" ]; then
        info="[root ${dir}]# "
        info_console="[${TPUT_DIM}${dir}${TPUT_RESET}]# "
    else
        info="[${user} ${dir}]$ "
        info_console="[${TPUT_DIM}${dir}${TPUT_RESET}]$ "
    fi

    {
        printf "\n${info}"
        escaped_print "${@}"
        printf " ... "
    } >> "${run_logfile}"

    printf >&2 "${info_console}${TPUT_BOLD}${TPUT_YELLOW}"
    escaped_print >&2 "${@}"
    printf >&2 "${TPUT_RESET}"

    "${@}"
    
    local ret=$?
    if [ ${ret} -ne 0 ]; then
        run_failed
        printf >> "${run_logfile}" "FAILED with exit code ${ret}\n"
    else
        run_ok
        printf >> "${run_logfile}" "OK\n"
    fi

    return ${ret}
}
# ------------------------------------------------------------------------------------------------
# message warning anda install pendencies
warning() {
	printf >&2 "${TPUT_BGRED}${TPUT_WHITE}${TPUT_BOLD} WARNING ${TPUT_RESET} ${*} \n\n"
	if [ "${INTERACTIVE}" = "0" ]; then
		fatal "Stopping due to non-interactive mode. Fix the issue or retry installation in an interactive mode."
	else
		read -r -p "Press ENTER to attempt installation > " CMD
        run $CMD
		progress "OK, let's give it a try..."
	fi
}
# ------------------------------------------------------------------------------------------------
# função para baixar arquivos
download() {
	progress "download public key"
	url="${1}"
	dest="${2}"
	if command -v curl > /dev/null 2>&1; then
		run curl -sSL --connect-timeout 10 --retry 3 "${url}" > "${dest}" || fatal "cannot download ${url}"
	elif command -v wget > /dev/null 2>&1; then
		run wget -T 15 -O - "${url}" > "${dest}" || fatal "cannot download ${url}"
	else
        warning "$package_manager -y install curl"
		## fatal "i need curl or wget to proceed, but neither is available on this system."
	fi
}
# ------------------------------------------------------------------------------------------------
# init configurations
# RUN pip3 --quiet install -r /var/www/warn/requirements.txt
progress "check system dependencies"
if [ -z $(command -v git --version 2> /dev/null) ]; then
    warning "${TPUT_BGGREEN}${TPUT_WHITE}${TPUT_BOLD} RUN ${TPUT_RESET} $package_manager install git -y $hidden_install"
else
    ok_dependencie "$(git --version)"
fi
if [ -z $(command -v python3 -V 2> /dev/null) ]; then
    warning "${TPUT_BGGREEN}${TPUT_WHITE}${TPUT_BOLD} RUN ${TPUT_RESET} $package_manager install python3 -y $hidden_install"
else
    ok_dependencie "$(python3 --version)"
fi
if [ -z $(command -v pip3 2> /dev/null) ]; then
    warning "${TPUT_BGGREEN}${TPUT_WHITE}${TPUT_BOLD} RUN ${TPUT_RESET} $package_manager install python3-pip -y $hidden_install"
else
    ok_dependencie "$(pip3 --version)"
fi
if [ -z $(command -v suricata 2> /dev/null) ]; then
    echo
	echo " [?] for more details check the documentation for your platform: https://suricata.readthedocs.io/en/suricata-5.0.3/install.html"
    echo " [!] if your distribution is RHEL/CentOS install before ${TPUT_BOLD}${TPUT_WHITE}epel-release ${TPUT_RESET}"
    echo
    warning "${TPUT_BGGREEN}${TPUT_WHITE}${TPUT_BOLD} RUN ${TPUT_RESET} $package_manager install suricata -y $hidden_install"
else
    ok_dependencie "$(suricata -V)"
fi

if [ ! -d "$INSTALL_PATH" ]; then
    run mkdir $INSTALL_PATH || exit 1
fi
progress "clone repository SaT tool"
run git clone $REPOSITORY || fatal "you have no communication with repo"
progress "install SaT to system"
cd "${TMPDIR}/SaT" || exit 1
run pip3 --quiet install -r requirements.txt
run cp alert.py bot.py config.py daemon.py model.py upload.py SaT.conf.example SaT.py $INSTALL_PATH
chmod 0744 $INSTALL_PATH/SaT.py
echo "[+] configure \"${INSTALL_PATH}/sat.conf\" to finish the installation"
printf >&2 "\n\t${TPUT_BGGREEN}${TPUT_WHITE}${TPUT_BOLD} successful tool installation ${TPUT_RESET}\n\n"
printf >&2 " [?] usage: ${INSTALL_PATH}/SaT.py start|status|stop|restart\n\n"
