# First steps on how to use the scripts

This is a quick tutorial on how to use GLOBAL VARIABLES to set up all you need
in order to use the scripts of this repo.

## Quick Start

### 1. Create your configuration file

Create `~/.work_config` with your personal settings:

```bash
cat > ~/.work_config << 'EOF'
# Personal Information
MAIL="your.email@example.com"
USER="your_username"

# Conda Environments
ENV1="envname1"
ENV2="envname2"

# Project Directories
PATHPROJ1="project-code"
NAMEPROJ1="project-name"
PATHPROJ2="project-code"
NAMEPROJ2="project-name"
PATHPROJ3="project-code"
NAMEPROJ3="project-name"
PATHPROJ4="project-code"
NAMEPROJ4="project-name"
EOF
```

Set secure permissions (optional, but recomended):
```bash
chmod 600 ~/.work_config
```

### 2. Add to your `.bashrc`

Add this line to your `~/.bashrc` to load the config automatically:

```bash
source ~/.work_config
```

Reload your bash configuration:
```bash
source ~/.bashrc
```

If you do not have a `.bashrc` configuration, neither a `.bash_profile`, take a look at [Levante Documentation](https://docs.dkrz.de/blog/2017/how-to-write-a-shell-alias-or-function-for-quick-login-to-a-node-managed-by-slurm.html).

### 3. Use the scripts

Clone this repository:
```bash
git clone https://github.com/GheodeAI/dkrz_utils.git
cd dkrz_utils
```

Make scripts executable:
```bash
chmod +x cd_work.sh submit_job.sh
```

## Script Documentation

### `cd_work.sh`

Navigate to common work directories with automatic module loading.

Usage:
```bash
./cd_work.sh [project_name]
```

Examples:
```bash
./cd_work.sh                # Goes to default project 
./cd_work.sh example-name   # Goes to example-name project
./cd_work.sh --help         # Shows help message
```

### `submit_job.sh`

Submit SLURM jobs with your standard configuration.

Usage:
```bash
sbatch submit_job.sh
```

## Configuration Reference

| Variable     | Description                          | Example Value        |
|--------------|--------------------------------------|----------------------|
| `MAIL`       | Your email for job notifications     | `user@example.com`   |
| `USER`       | Your DKRZ username                   | `b000000`            |
| `ENV1`       | Primary conda environment            | `flow`               |
| `PATHPROJ1`  | First project's path component       | `aa0000`             |
| `NAMEPROJ1`  | First project's nickname             | `name`               |

## Best Practices

1. **Keep sensitive data secure**:
   - Never commit your actual `.work_config` to git.
   - Use `chmod 600` for configuration files.

2. **Customize for your workflow**:
   - Add more projects as needed. Theese scripts are prepared for, at most, 4 projects,
     but fill free to modify it to yours needs.
   - Extend with additional environment variables.
   - If you do not have your own conda environment follow this [tutorial](https://docs.dkrz.de/doc/levante/code-development/python.html#set-up-conda-for-individual-environments).

3. **Test your configuration**:
   ```bash
   echo $NAMEPROJ1  # Should output your default project name
   ```
