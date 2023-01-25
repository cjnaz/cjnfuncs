


# # ===== Tests for snd_notif and snd_email =====
# # Set debug LogLevel in testcfg.cfg
# # cfg['DontEmail'] = True     # Comment these in/out here or in the testcfg.cfg
# # cfg['DontNotif'] = True
# snd_email (subj="body to EmailTo", body="To be, or not to be...", to="EmailTo", log=True)
# snd_email (subj="body to EmailTo - not logged", body="To be, or not to be...", to="EmailTo")
# snd_email (subj="filename to EmailTo - not logged", filename="textfile.txt", to="EmailTo")
# snd_email (subj="htmlfile to EmailTo", htmlfile="testfile.html", to="EmailTo", log=True)
# snd_email (subj="body to EmailToMulti", body="To be, or not to be...", to="EmailToMulti", log=True)
# try:
#     snd_email (subj="No such file nofile.txt", filename="nofile.txt", to="EmailTo", log=True)
# except SndEmailError as e:
#     print (f"snd_email failed:  {e}")
# try:
#     snd_email (subj="No to=", body="Hello")
# except SndEmailError as e:
#     print (f"snd_email failed:  {e}")
# try:
#     snd_email (subj="Invalid to=", body="Hello", to="me@example.com, junkAtexample.com", log=True)
# except SndEmailError as e:
#     print (f"snd_email failed:  {e}")
# snd_notif (subj="This is a test subject - not logged", msg='This is the message body')       # to defaults to cfg["NotifList"]
# snd_notif (subj="This is another test subject", msg='This is another message body', log=True)


# # ===== Tests for lock files =====
# stat = requestlock ("try1")
# print (f"got back from 1st requestLock.  stat = {stat}")
# stat = requestlock ("try2")
# print (f"got back from 2nd requestLock.  stat = {stat}")
# stat = releaselock ()
# print (f"got back from 1st releaseLock.  stat = {stat}")
# stat = releaselock ()
# print (f"got back from 2nd releaseLock.  stat = {stat}")