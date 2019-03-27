'''
Created on Feb 1, 2019

@author: deepashree.kurnad
'''

from random import randint

def getProjectId(projectName):
    suffix="-infosys-"
    pName=projectName.split(" ")
    newName=""
    for i in pName:
        newName+=i
    newName = newName.lower()
    rand_hex_digits=randint(100000, 999999)
    rand_hex_digits=str(rand_hex_digits) 
    projectId=newName+suffix+rand_hex_digits
    print(projectId)
    return projectId