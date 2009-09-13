import threading

def async_send_mail(subject, message, sender, recipients):
	from django.core.mail import send_mail
	# create thread
	t = threading.Thread(target = send_mail,
						args = [subject, message, sender, recipients],
						kwargs = {'fail_silently':True})
	t.setDaemon(True)
	t.start()
	return True