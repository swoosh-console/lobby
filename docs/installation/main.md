# How to install the system
1. Install fresh Rocky 10 desktop.<br>
    a. Create an administrator account, and another user account called `swoosh`.
2. Install video drivers for the system's GPU.
3. Enable automatic login for `swoosh` user.<br>
    option a: via `System Settings`<br>
    option b: via `/etc/sddm.conf`<br>
4. Modify desktop to improve user experience.<br>
    a: Modify background color to black.<br>
    b: Hide/remove task bar/activity bar.<br>
    c: Hide/remove desktop icons.<br>
5. Install the required packages and flatpacks.<br>
    a. For Cemu, add `keys.txt` to `.var/app/info.cemu.Cemu/data/Cemu/`
6. Clone the repository [Swoosh Lobby](https://github.com/swoosh-console/lobby.git) to `/home/swoosh/swoosh`
7. Copy `.swoosh-config` to `/home/swoosh/.swoosh-config`.
8. Create the following directories:<br>
    a. `/home/swoosh/.swoosh-config.d`<br>
    b. `/home/swoosh/.swoosh-resources`<br>
    c. `/home/swoosh/.swoosh-upload`<br>
9. Copy `swoosh.service` to `.local/share/systemd/user/swoosh.service`
10. Run `systemctl --user enable swoosh.service`
11. Run `systemctl --user start swoosh.service`