# custom patches
import os
def getuid_fake():
    return 0
# Fix docutils in AppEngine
os.getuid = getuid_fake