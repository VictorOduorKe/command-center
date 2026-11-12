# Victor Command Center - Cyberpunk Shell Environment
# Terminal prompt & developer enhancements for Victor Oduor

# Enable prompt substitution and colors
setopt prompt_subst
autoload -Uz colors && colors
autoload -Uz vcs_info

# Configure fast Git branch detection
zstyle ':vcs_info:*' enable git
zstyle ':vcs_info:git:*' check-for-changes false
zstyle ':vcs_info:git:*' formats ' %F{51}[%f%F{46}git:%b%f%F{51}]%f'
zstyle ':vcs_info:git:*' actionformats ' %F{51}[%f%F{46}git:%b%f|%F{197}%a%f%F{51}]%f'

# Precmd hook to refresh vcs_info
vcc_precmd() {
    vcs_info
}
autoload -Uz add-zsh-hook
add-zsh-hook precmd vcc_precmd

# Futuristic Cyberpunk Prompt
# Top line: [VICTOR@KALI-SEC]──[DIR] [GIT]
# Prompt line: ⚡❯ (Green on success, Neon Red on error)
PROMPT=$'%F{238}┌─%f%F{51}[%f%F{46}victor%f%F{242}@%f%F{51}kali-command%f%F{51}]%f%F{238}──%f%F{51}[%f%F{51}%~%f%F{51}]%f${vcs_info_msg_0_}\n%F{238}└─%f%(?.%F{46}⚡❯%f.%F{197}⚡❯%f) '

# Right Prompt: System Time in subtle cyan
RPROMPT=$'%F{242}%*%f'

# Useful Developer & Cybersecurity Shortcuts
alias vcc='python3 /home/alpha/victor-command-center/src/main.py'
alias vcc-hud='python3 /home/alpha/victor-command-center/src/hud.py'
alias vcc-restore='python3 /home/alpha/victor-command-center/src/restore.py'

# Quick system and network inspection
alias myip='ip -br -c a'
alias ports='ss -tulanp'
alias sysinfo='echo -e "\033[1;32m[CPU]\033[0m $(grep "model name" /proc/cpuinfo | head -n1 | cut -d: -f2 | xargs)\n\033[1;36m[MEM]\033[0m $(free -h | awk "/Mem:/{print \$3 \" used / \" \$2 \" total\"}")\n\033[1;35m[UPTIME]\033[0m $(uptime -p)"'

# Cyberpunk Terminal Banner function
vcc_banner() {
    echo -e "\033[38;5;46m  ⚡ VICTOR'S CYBERPUNK COMMAND CENTER ⚡\033[0m"
    echo -e "\033[38;5;51m  Developer: Victor Oduor | Kali Rolling Workstation\033[0m"
    echo -e "\033[38;5;242m  Type 'vcc' to launch Command Center GUI | 'sysinfo' for stats\033[0m\n"
}

