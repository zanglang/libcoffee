from datetime import datetime

def now(request):
	return {'now': datetime.now()}