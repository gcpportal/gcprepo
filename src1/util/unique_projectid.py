
import random 
import string 
 
def getuniqueid(chars): 
    name= string.ascii_uppercase + string.digits
    return chars + ''.join(random.choice(name) for x in range(8))