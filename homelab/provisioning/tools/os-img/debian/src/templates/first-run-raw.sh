#!/bin/bash

#
# https://github.com/raspberrypi/rpi-imager/blob/qml/src/OptionsPopup.qml#L600
#
# TODO: sanitize strings


# if (chkHostname.checked && fieldHostname.length)
CURRENT_HOSTNAME=`cat /etc/hostname | tr -d \" \\t\\n\\r\"`

echo "+fieldHostname.text+" >/etc/hostname
sed -i \"s/127.0.1.1.*$CURRENT_HOSTNAME/127.0.1.1\\t"+fieldHostname.text+"/g\" /etc/hosts


# if (chkSSH.checked || chkSetUser.checked)
FIRSTUSER=`getent passwd 1000 | cut -d: -f1`
FIRSTUSERHOME=`getent passwd 1000 | cut -d: -f6`

# if (chkSSH.checked || chkSetUser.checked)  && (chkSSH.checked && radioPubKeyAuthentication.checked)
install -o \"$FIRSTUSER\" -m 700 -d \"$FIRSTUSERHOME/.ssh\"
install -o \"$FIRSTUSER\" -m 600 <(printf \""+pubkey.replace(/\n/g, "\\n")+"\") \"$FIRSTUSERHOME/.ssh/authorized_keys\"
echo 'PasswordAuthentication no' >>/etc/ssh/sshd_config
systemctl enable ssh


# if (chkSSH.checked || chkSetUser.checked) && (chkSSH.checked && radioPasswordAuthentication.checked)
systemctl enable ssh


# if (chkSSH.checked || chkSetUser.checked) && (chkSetUser.checked)
echo \"$FIRSTUSER:\""+escapeshellarg(cryptedPassword)+" | chpasswd -e
if [ \"$FIRSTUSER\" != \""+fieldUserName.text+"\" ]; then
   usermod -l \""+fieldUserName.text+"\" \"$FIRSTUSER\"
   usermod -m -d \"/home/"+fieldUserName.text+"\" \""+fieldUserName.text+"\"
   groupmod -n \""+fieldUserName.text+"\" \"$FIRSTUSER\"
   if grep -q \"^autologin-user=\" /etc/lightdm/lightdm.conf ; then
      sed /etc/lightdm/lightdm.conf -i -e \"s/^autologin-user=.*/autologin-user="+fieldUserName.text+"/\"
   fi
   if [ -f /etc/systemd/system/getty@tty1.service.d/autologin.conf ]; then
      sed /etc/systemd/system/getty@tty1.service.d/autologin.conf -i -e \"s/$FIRSTUSER/"+fieldUserName.text+"/\"
   fi
   if [ -f /etc/sudoers.d/010_pi-nopasswd ]; then
      sed -i \"s/^$FIRSTUSER /"+fieldUserName.text+" /\" /etc/sudoers.d/010_pi-nopasswd
   fi
fi


# if (chkWifi.checked)
cat >/etc/wpa_supplicant/wpa_supplicant.conf <<'WPAEOF'
(wpaconfig)
WPAEOF
chmod 600 /etc/wpa_supplicant/wpa_supplicant.conf
rfkill unblock wifi
for filename in /var/lib/systemd/rfkill/*:wlan ; do
      echo 0 > $filename
done


# if (chkLocale.checked)
rm -f /etc/localtime
echo \""+fieldTimezone.editText+"\" >/etc/timezone
dpkg-reconfigure -f noninteractive tzdata
cat >/etc/default/keyboard <<'KBEOF'
(kbdconfig)
KBEOF
dpkg-reconfigure -f noninteractive keyboard-configuration


rm -f /boot/firstrun.sh
sed -i 's| systemd.run.*||g' /boot/cmdline.txt
exit 0
