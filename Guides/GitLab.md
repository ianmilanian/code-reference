## GitLab Installation
Make sure the system meets the minimum [requirements](https://git.ucd.ie/help/install/requirements.md) to prevent weird errors.
```
sudo apt-get update
sudo apt-get install -y curl openssh-server ca-certificates
curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ee/script.deb.sh | sudo bash
sudo EXTERNAL_URL="http://localhost" apt-get install gitlab-ee
```
The GitLab server should now be running on **_localhost_** and can be accessed via the web interface. The first time the web interface is started the user will be prompted to set a password for the admin account (`root`). After logging in with the admin account, user accounts can be created through the `Admin Area` portal (wrench icon).
  
**Note: You Must Use Git Bash**
## GitLab Update
```
sudo apt-get update
sudo rm /boot/grub/menu.lst
sudo update-grub-legacy-ec2 -y
sudo apt-get dist-upgrade
sudo reboot
```
See [this post](https://serverfault.com/questions/662624/how-to-avoid-grub-errors-after-runing-apt-get-upgrade-ubunut) for why we need to modify grub when upgrading.
  
**Note: You Must Use Git Bash**
## GitLab Commands
| Desc. | Command |
| ----- | ------- |
| Start Server | `sudo gitlab-ctl start` |
| Stop Server | `sudo gitlab-ctl stop` |
| Debug Server | `sudo gitlab-ctl tail` |
| Debug Server | `sudo gitlab-rake gitlab:check` |
| Edit Configuration | `sudo nano /etc/gitlab/gitlab.rb`|
| Save Configuration | `sudo gitlab-ctl reconfigure` |

## Git Documentation
See [Git Documentation](https://git-scm.com/docs) for help.

## Git Authentication
An SSH token is required for a user to interact remotely with the GitLab server via [ssh-keygen](https://www.freebsd.org/cgi/man.cgi?query=ssh-keygen&sektion=1&manpath=OpenBSD). Make sure to set a passphrase when prompted.
```
cd ~/.ssh && ssh-keygen -t rsa -b 4096 -o -a 100
cat id_rsa.pub | clip
```
The token body should be copied to the clipboard. In a browser navigate to the GitLab server `http://[server]/profile/keys` and paste in the token.
  
**Note: You Must Use Git Bash**
## Git Configuration
Before executing git commands configure the local machine for a GitLab user.
```
git config --global user.name "bob"
git config --global user.email "bob@example.com"
```
List the current configuration for the local machine with `git config --list --show-origin`.
  
**Note: You Must Use Git Bash**
## Git Pull
```
cd /local-machine/project-dir
git init
git remote add [alias] [url]
git pull [alias] [branch]
```
```
cd ~/project
git init
git remote add origin git@ip_address:user/project.git
git pull origin master
```
Set the active working directory, initialize it, add the remote project url, and then pull your code from the repository.
  
**Note: You Must Use Git Bash**
## Git Push
Make changes to your local project, commit them, and then push to the remote repository.
```
cd ~/project
git commit -m "Added Folders"
git remote add origin git@ip_address:user/project.git
git push origin master
```
Before pushing to GitLab view merge changes with `git status`.
  
**Note: You Must Use Git Bash**
