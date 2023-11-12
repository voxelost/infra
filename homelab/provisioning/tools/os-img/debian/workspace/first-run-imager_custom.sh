#!/bin/bash


#
# https://github.com/raspberrypi/rpi-imager/blob/qml/src/OptionsPopup.qml#L600
#

# if (chkHostname.checked && fieldHostname.length)
CURRENT_HOSTNAME=`cat /etc/hostname | tr -d \" \\t\\n\\r\"`
/usr/lib/raspberrypi-sys-mods/imager_custom set_hostname "+fieldHostname.tex

# if (chkSSH.checked || chkSetUser.checked)
FIRSTUSER=`getent passwd 1000 | cut -d: -f1`"
FIRSTUSERHOME=`getent passwd 1000 | cut -d: -f6`

# if (chkSSH.checked || chkSetUser.checked)  && (chkSSH.checked && radioPubKeyAuthentication.checked)
/usr/lib/raspberrypi-sys-mods/imager_custom enable_ssh -k"+pubkeySpaceSe

# if (chkSSH.checked || chkSetUser.checked) && (chkSSH.checked && radioPasswordAuthentication.checked)
/usr/lib/raspberrypi-sys-mods/imager_custom enable_ssh

# if (chkSSH.checked || chkSetUser.checked) && (chkSetUser.checked)
/usr/lib/userconf-pi/userconf "+escapeshellarg(fieldUserName.text)+" "+escapeshellarg(cryptedPassword

# if (chkWifi.checked)
/usr/lib/raspberrypi-sys-mods/imager_custom set_wlan
         +(chkWifiSSIDHidden.checked ? " -h " : "")
         +escapeshellarg(fieldWifiSSID.text)+" "+escapeshellarg(cryptedPsk)+" "+escapeshellarg(fieldWifiCountry.editText))

# if (chkLocale.checked)
/usr/lib/raspberrypi-sys-mods/imager_custom set_keymap "+escapeshellarg(fieldKeyboardLayout.editText
/usr/lib/raspberrypi-sys-mods/imager_custom set_timezone "+escapeshellarg(fieldTimezone.editText

# if (firstrun.length)
rm -f /boot/firstrun.sh
sed -i 's| systemd.run.*||g' /boot/cmdline.txt
exit 0
