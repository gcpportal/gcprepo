'''
Created on Dec 12, 2018

@author: deepashree.kurnad
'''

import webapp2
from models import GCPRequest, BillingAccounts
from models import Creds
import json
import httplib2
from config import settings
from googleapiclient import discovery
from util import project_name
from util import project_id
from util import unique_projectid
from send_mail import create_message
from send_mail import send_message 
from send_mail import sendmailSMTP
from google.appengine.ext import ndb


class HelloWebapp2(webapp2.RequestHandler):
    def get(self):
        self.response.write("server running.......")
        

class RestHandler(webapp2.RequestHandler):
    def options(self, *args, **kwargs):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept, Authorization'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT, DELETE'   

        
             
    def google_authenticate(self): 
        print(1)
        auth_code= self.request.GET.get('code')
        redirect_uri = "http://localhost:4200/login"
        from oauth2 import client
        credentials = client.credentials_from_clientsecrets_and_code(settings.CLIENT_SECRETS_FILE,['profile', 'email'], auth_code, redirect_uri=redirect_uri)
        http_auth = credentials.authorize(httplib2.Http())
        user_service = discovery.build('oauth2', 'v2', http=http_auth)
        userinfo = user_service.userinfo().get().execute()
        credentials_json = json.loads(credentials.to_json())
        print(credentials_json)
        print(credentials_json["id_token"]["email"])
        if(credentials.access_token!=None):
            request_object = Creds(access_token = credentials.access_token,
                                   userId = credentials_json["id_token"]["email"],userName=credentials_json["id_token"]["name"])
            request_key = request_object.put()
            print(request_key)
            return credentials
#             print(credentials_json)
#             print(credentials.access_token)


 
    def createProject(self,req,requester):
        print(requester+" ---------")
        print("Inside createProject")
        print(req)
        from pprint import pprint
        from oauth2client.client import GoogleCredentials
        credentials = GoogleCredentials.get_application_default()
        service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
        name=project_name.getProjectName(req.applicationName) 
        id=project_id.getProjectId(req.applicationName)
        project_body = {
            'name': name,
            'projectId': id 
        }
        print(project_body)
        print(req.client)
        try:
            request = service.projects().create(body=project_body)
            response = request.execute()
            pprint(response)
            self.updateBillingAccount(credentials,id,req.client)
            sub= "Project ID approved and created"
            msg= 'Hi '+req.requesterName+' ,'+'\n\n'+req.approverName+' has approved the project and '+ id +' has been created in GCP portal. Please visit https://console.cloud.google.com for more details. '+'\n\n'+'P.s: This is auto generated email. Please do not reply to this ID.'+'\n\n'+'Regards,'+'\n'+'Admin@gcp.request.portal.com'
            sendmailSMTP(msg,requester,sub)
            msg= 'Hi '+req.approverName+','+'\n\n'+req.approverName+' has approved the project and '+id+' has been created in GCP portal. Please visit https://console.cloud.google.com for more details. '+'\n\n'+'P.s: This is auto generated email. Please do not reply to this ID.'+'\n\n'+'Regards,'+'\n'+'Admin@gcp.request.portal.com'
            sendmailSMTP(msg,requester,sub)
            return "200"
        except Exception as e:
            return e  

            
    def updateBillingAccount(self,credentials,id,client):
            # Get billing Info of selected project
            print("***********************************************")
            query = BillingAccounts.query(BillingAccounts.accountName == client)
            result=query.fetch()
            accountName = "billingAccounts/"+str(result[0].accountID)
            service = discovery.build('cloudbilling', 'v1', credentials=credentials, cache_discovery=False)
            name = 'projects/' + id
#           Code To update the billing account to a particular project
            body={
                  'name': "projects/"+id+"/billingInfo",
                  'projectId': id,
                  'billingAccountName': accountName,
                  'billingEnabled': True
                }
            billing_request = service.projects().updateBillingInfo(name=name,body=body)

#             billing_request = service.projects().getBillingInfo(name=name) #to get billing info
            billing_response = billing_request.execute()
            data = billing_response
            print(json.dumps(data))
            if data['name']:
                print(data)
        
            
    def setIAMPolicy(self,projectId,member,memberList,owner):
        from pprint import pprint

        from googleapiclient import discovery
        from oauth2client.client import GoogleCredentials
        
        credentials = GoogleCredentials.get_application_default()
        
        service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
        resource = projectId  
        role= "roles/"+member
        print(memberList)
        members=[]
        for user in memberList:
            userNew = "user:"+user
            print(userNew)
            members+=[userNew]

        request_body = {
            "role": role,
            "members": members
            }

        request = service.projects().getIamPolicy(resource=resource)
        response = request.execute()
        print("------------------------------------")
        print(response)
        print("------------------------------------")

        binding_old=response["bindings"]
        binding_update = binding_old + [request_body]
        response["bindings"] = binding_update
        print(binding_update)
        print("------------------------------------")

        print(response)
        print("------------------------------------")
        set_iam_policy_request_body = {
            "policy" : response
        }
        request = service.projects().setIamPolicy(resource=resource, body=set_iam_policy_request_body)
        response = request.execute()
        pprint(response)       
    def newRequestProcess(self):
        current_user = self.request.GET.get('requester')
        query = Creds.query(Creds.userId==current_user)
        result=query.fetch()
        print(result)
        print(" ------------")
        requesterName = result[0].userName
        request_json=json.loads(self.request.body)
        status=self.getUserInfo(request_json["approver"],current_user)
        if(status!="400"):
            approverName=status
            request_object = GCPRequest(applicationName = request_json["applicationName"],
                                            projectCode = request_json["projectCode"],
                                            environment = request_json["environment"],
                                            requestOwner = request_json["requestOwner"],
                                            risk = request_json["risk"],
                                            partner = request_json["partner"],
                                            services = request_json["services"],
                                            status="In Progress",
                                            approver=request_json["approver"],
                                            approverName=approverName,
                                            requester=current_user,
                                            requesterName=requesterName,
                                            client=request_json["client"],
)
            request_key = request_object.put()
            print(request_key)
            if(request_key):
                sub="Submission of new project creation request"
                message= 'Hi '+requesterName+','+'\n\n'+'Your request for new project creation in GCP Portal ('+request_json["projectCode"]+') is submitted successfully with Project Name - "'+request_json["applicationName"]+'"'+'\n'+'Project would be created once the request is been approved by the approver.'+'\n\n'+'P.s: This is auto generated email. Please do not reply to this ID.'+'\n\n'+'Regards,'+'\n'+'Admin@gcp.request.portal.com'
                sendmailSMTP(message,current_user,sub)
                sub="Approval for New Project creation request"
                message= 'Hi '+approverName+','+'\n\n'+requesterName+' has submitted request for creating new project '+request_json["projectCode"]+' in GCP portal. Kindly review and take necessary action.'+'\n\n'+'P.s: This is auto generated email. Please do not reply to this ID.'+'\n\n'+'Regards,'+'\n'+'Admin@gcp.request.portal.com'
                sendmailSMTP(message,request_json["approver"],sub)
                return request_key
        else:
            return "405"
        
        
    def getUserInfo(self,test_user,current_user):
#         session= sessions.Session() 
        query = Creds.query(Creds.userId==current_user)
        result=query.fetch()
        print(result)
        print(" ------------")
        accessToken = result[0].access_token
        print(accessToken)   
        parser = httplib2.Http()
        
        val="Bearer"+" "+accessToken
        print(val)
        user_request_uri = "https://www.googleapis.com/admin/directory/v1/users/"+test_user+"?viewType=domain_public"
        headers={'content-type':'application/json',
                 'Authorization':val}

        content = parser.request(user_request_uri, method = 'GET', headers = headers)
        print(content[0]["status"])
        status= content[0]["status"]
        #this gets the google profile!!
        if(status=="200"):
            content_json = json.loads(content[1])
            print(content_json["name"]["fullName"])
            return content_json["name"]["fullName"]
        else:
            return "400"
    
    
    def obtainRequests(self):
        
        query = GCPRequest.query()
        result=query.fetch()
        userName= self.request.GET.get('userName')
        response_list=[]
        for i in result:
            if i.approver==userName:
                requests_pending_dict = {}
                requests_pending_dict.update( {"pkey_projectId":i.key.urlsafe()} )
                requests_pending_dict.update( {"applicationName":i.applicationName} )
                requests_pending_dict.update( {"environment":i.environment} )
                requests_pending_dict.update( {"partner":i.partner} )
                requests_pending_dict.update( {"projectCode":i.projectCode} )
                requests_pending_dict.update( {"requestOwner":i.requestOwner} )
                requests_pending_dict.update( {"risk":i.risk} )
                requests_pending_dict.update( {"services":i.services} )
                requests_pending_dict.update( {"status":i.status} )
                requests_pending_dict.update( {"requester":i.requester} )
                requests_pending_dict.update( {"approver":i.approver} )
                requests_pending_dict.update( {"approverName":i.approverName} )
                requests_pending_dict.update( {"requesterName":i.requesterName} )
                requests_pending_dict.update( {"client":i.client} )
                response_list.append(requests_pending_dict)
        return response_list
    
    def updateRequest(self):
        req_json=json.loads(self.request.body)
        gcp_request_obj = ndb.Key(urlsafe = req_json["pkey_projectId"]).get()
        print(gcp_request_obj)
        if req_json["Status"] == "Approved":
            result=self.createProject(gcp_request_obj,gcp_request_obj.requester)
            if(result=="200"):
                gcp_request_obj.status = req_json["Status"]
                gcp_request_obj.put()
                return "project created successfully"
            else:
                return result
        elif req_json["Status"] == "Reject":
            sub="Project is rejected by approver"
            message= 'Hi '+req_json["requesterName"]+','+'\n\n'+req_json["approverName"]+' has rejected the project ('+req_json["projectCode"]+').  Please contact '+req_json["approver"]+'\n'+' for more details.'+'\n\n'+'P.s: This is auto generated email. Please do not reply to this ID.'+'\n\n'+'Regards,'+'\n'+'Admin@gcp.request.portal.com'
            sendmailSMTP(message,req_json["requester"],sub)
            result = "Request For the project has been rejected"
            gcp_request_obj.status = req_json["Status"]
            gcp_request_obj.put()
            return result
#             sub="Project "+req_json["projectCode"]+" is rejected by approver"
#             message= "Hi "+req_json["requester"]+','+'\n\n'+req_json["approver"]+" has rejected the project"+req_json["projectCode"]+" request. Please contact "+req_json["approver"]+" for more details."+'\n\n'+"P.s: This is auto generated email. Please do not reply to this ID."+'\n\n'+"Regards,"+'\n'+"Admin@gcp.request.portal.com"
#             sendmailSMTP(message,req_json["requester"],sub)
    
    def billingAccountDetails(self):
        request_object = BillingAccounts(accountName = "Account1",
                                         accountID = "018F0E-C6E961-C341FE")
        
        request_key = request_object.put()
        print(request_key)
        request_object = BillingAccounts(accountName = "Account2",
                                         accountID = "018F0E-C6E961-C341FE")
        
        request_key = request_object.put()
        print(request_key)

 
class AddMember(RestHandler):
    def post(self):
        self.options()
        request_json=json.loads(self.request.body)
        user=self.request.GET.get('userName')
        memberList = request_json["memberID"].split(",")
        for emailID in memberList:
            status=self.getUserInfo(emailID,user)
            if(status=="400"):
                break
            self.response.headers['Content-Type'] = 'application/json'
        if(status!='400'):
            try:
                self.setIAMPolicy(request_json["projectID"],request_json["member"],memberList,user)  
                self.response.write("Successfully updated the role")
            except Exception as e:
                self.response.write(e)
                
        else:
            self.response.write("Failed to update. Enter a valid Email ID")
                 
class updateReq(RestHandler):
    
    def post(self):
        self.options()
        result=self.updateRequest()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(result)
            
class getReqlist(RestHandler):
    
    def get(self):
        self.options()
        res=self.obtainRequests()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(res))
#         self.response.headers.add_header("Access-Control-Allow-Origin","http://localhost:4200") # This is to avoid CORS error thrown by browser
           
    
class NewRequest(RestHandler):
    
    def post(self):
        self.options()
        result=self.newRequestProcess()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(result)
        
        
class EndSession(RestHandler):
    
    def get(self):
        user=self.request.GET.get('userName')
        gprofiles=Creds.query(Creds.userId==user)
        for g in gprofiles:
            g.key.delete()
            self.response.out.write("Profile is deleted")

       
#         self.response.headers.add_header("Access-Control-Allow-Origin", "*")
class Request(RestHandler):
    
    def get(self):
        self.options()
        if(self.request.GET.get('code')!="undefined"):
            credentials=self.google_authenticate()
        # code to get the billing account
            http_auth = credentials.authorize(httplib2.Http())
            self.response.headers['Content-Type'] = 'application/json'
            credentials_json = json.loads(credentials.to_json())
            id_json=json.dumps(credentials_json["id_token"])
            toaddress = credentials_json["id_token"]["email"]
            self.response.write(id_json)
         

         
app = webapp2.WSGIApplication([
    ('/', HelloWebapp2),
     ('/newRequestResponse', NewRequest),
     ('/request',Request),
     ('/obtainRequests',getReqlist),
     ('/updateRequest',updateReq),
     ('/addMember',AddMember),
     ('/endSession',EndSession)
], debug=True)


def main():
    from paste import httpserver 
    httpserver.serve(app, host='127.0.0.1', port='8080')

if __name__ == '__main__':
    main()
    
