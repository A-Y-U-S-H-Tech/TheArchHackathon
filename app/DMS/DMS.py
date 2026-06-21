from DMS.types import * 
from itertools import islice
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from supabase import create_client
from supabase import PostgrestAPIError
import os
import re,sys
import json
load_dotenv()

class DMS:
    def __init__(self):
        self.users = {}
        self.products = {}
        self.complaints = {}
        self.tickets = {}
        self.KDocuments = {}
        self.RContent = {}
        self.counter_CID = 0 
        self.couter_TicketID =0
        self.counter_DID = 0
        self.counter_RID = 0
        self.counter_PID = 0
        self.client = create_client(os.environ.get("SUPABASE_BASE_URL"),os.environ.get("SUPABASE_KEY")) #type:ignore
        self.url: str = os.environ.get("SUPABASE_URL") #type:ignore
        self.key: str = os.environ.get("SUPABASE_KEY") #type:ignore
        self.supabase: Client = create_client(self.url, self.key)

    def Create_User(self,NAM,PAS,EMA,ROL):
        try:
            self.client.table("User").insert(
                {
                    "NAM":NAM,
                    "PAS":PAS,
                    "EMA":EMA,
                    "ROL":ROL
                }
            ).execute()
            return True
        except PostgrestAPIError as e:
            return False
        # if NAM not in self.users.keys():
        #     self.users[NAM] = USER(NAM,PAS,EMA,ROL)
        #     return True
        # else:
        #     return False
    def Delete_User(self,NAM):
        try:
            self.client.table("User").delete(
            ).eq("NAM",NAM).execute()
            return True
        except PostgrestAPIError as e:
            return False 
        # if NAM in self.users.keys():
        #     self.users.pop(NAM)
        #     return True
        # return False
    def Update_User (self,NAM,PAS=None,EMA=None,ROL=None):
        _query = {}
        try:
            if(PAS != None):
                _query["PAS"] = PAS
            if(EMA != None):
               _query["EMA"] = EMA
            if(ROL != None):
                _query["ROL"] = ROL
            self.client.table("User").update(
                _query
            ).eq("NAM",NAM).execute()
            return True
        except PostgrestAPIError as e:
            return False 
        # if NAM in self.users.keys():
        #     if(PAS != None):
        #         self.users[NAM].PAS = PAS
        #     if(EMA != None):
        #         self.users[NAM].EMA = EMA
        #     if(ROL != None):
        #         self.users[NAM].ROL = ROL
        #     return True
        # else:
        #     return False
    def Check_User(self,NAM):
        try:
            _return = self.client.table("User").select("*"
            ).eq("NAM",NAM).execute()
            print(_return)
            return len(_return.data) != 0
        except PostgrestAPIError as e:
            return False 
        # return NAM in self.users.keys()

    def Check_Validate_User(self,NAM,PAS):
        try:
            _return = self.client.table("User").select("*"
            ).eq("NAM",NAM).eq("PAS",PAS).execute()
            return len(_return.data) != 0
        except PostgrestAPIError as e:
            return False 
        # if NAM in self.users.keys():
        #     return self.users[NAM].PAS == PAS#type:ignore
        # else:
        #     return False
    def Get_User_role(self,NAM):
        try:
            _response = self.client.table("User").select("ROL"
            ).eq("NAM",NAM).execute()
            return _response.data[0]["ROL"]
        except PostgrestAPIError as e:
            return False 
        # if NAM in self.users.keys():
        #     return self.users[NAM].ROL

    def Create_Product(self,PNM,PCAT,PDES,PSTA):
        try:
            self.client.table("Products").insert(
                {
                    "PNM":PNM,
                    "PCAT":PCAT,
                    "PDES":PDES,
                    "PSTA":PSTA
                }
            ).execute()
            return True
        except PostgrestAPIError as e:
            return False 
        # self.products[self.counter_PID] = product(self.counter_PID,PNM,PCAT,PDES,PSTA)
        # self.counter_PID+=1
        # return True
    def Get_Products(self,i,j):
        if i>j:
            return (False,[])
        if i==-1 and j==-1:
            try:
                _return = self.client.table("Products").select("*"
                ).execute()
                return (True,_return.data)
            except PostgrestAPIError as e:
                print(e)
                return (False,[]) 
        try:
            _return = self.client.table("Products").select("*"
            ).gt("PID",i).lt("PID",j).execute()
            return (True,_return.data)
        except PostgrestAPIError as e:
            return (False,[])
        
    def Get_Product(self,PID):
        try:
            PID = int(PID)
            _request = self.client.table("Products").select("*"
            ).eq("PID",PID).execute()
            print(_request)
            return (True,_request.data[0])
        except PostgrestAPIError as e:
            return False 

    def Create_Complaint(self,CUS,PID,CDES,CST,CSEV,CDT,CUSER):
        try:
            self.client.table("Complaints").insert(
                {
                    "CUS":CUS,
                    "CDES":CDES,
                    "PID":PID,
                    "CST":CST,
                    "CSEV":CSEV,
                    "USER":CUSER
                }
            ).execute()
            return True
        except PostgrestAPIError as e:
            print(e)
            return False 
        # print(self.products,'\t',PID)
        # if int(PID) in self.products.keys():
        #     self.complaints[self.counter_CID] = Complaint(self.counter_CID,CUS,PID,CDES,CST,CSEV,CDT)
        #     self.counter_CID+=1
        #     return True
        # else:
        #     return False
    def Delete_Complaint(self,CID):
        try:
            self.client.table("Complaints").delete(
            ).eq("CID",CID).execute()
            return True
        except PostgrestAPIError as e:
            return False 
        # if int(CID) in self.complaints.keys():
        #     self.complaints.pop(CID)
        #     return True
        # else:
        #     return False
    def Update_Complaint(self,CID,CUS,PID,CDES,CST,CSEV,CDT):
        _query = {}
        try:
            if(CUS):
                _query["CUS"] = CUS
            if(CDES):
                _query["CDES"]= CDES
            if(PID):
                _query["PID"] = PID
            if(CST):
                _query["CST"] = CST
            if(CSEV):
                _query["CSEV"] = CSEV
            if(CDT) :
                _query["CDT"] = CDT
            self.client.table("Complaints").update(
                _query
            ).eq("CID",CID).execute()
            return True
        except PostgrestAPIError as e:
            return False 
        # if int(CID) in self.complaints.keys():
            # if(CUS):
            #     self.complaints[CID].CUS = CUS
            # if(CDES):
            #     self.complaints[CID].CDES = CDES
            # if(PID):
            #     self.complaints[CID].PID = PID
            # if(CST):
            #     self.complaints[CST].CST = CST
            # if(CSEV):
            #     self.CSEV = CSEV
            # if(CDT) :
            #     self.CDT = CDT
        #     return True
        # else:
        #     return False
    def Get_Complaints(self,i,j):
        if i>j:
            return (False,[])
        if i==-1 and j==-1:
            try:
                _return = self.client.table("Complaints").select("*"
                ).execute()
                return (True,_return.data)
            except PostgrestAPIError as e:
                print(e)
                return (False,[]) 
        #     return (True,list(v.get_dict() for v in self.complaints.values()))
        try:
            _return = self.client.table("Complaints").select("*"
            ).gt("CID",i).lt("CID",j).execute()
            return (True,_return.data)
        except PostgrestAPIError as e:
            return (False,[])
        # return (True,list(v.get_dict() for v in islice(self.complaints.values(),i,j)))
    
    def Get_Complaint(self,CID):
        try:
            CID = int(CID)
            _request = self.client.table("Complaints").select("*"
            ).eq("CID",CID).execute()
            print(_request)
            return (True,_request.data[0])
        except PostgrestAPIError as e:
            return False 
        # if int(CID ) in self.complaints.keys():
        #     return (True,self.complaints[CID].get_dict())
        # else:
        #     return (False,{})
    def Get_UserComplains(self,UNAM,i,j):
        if i>j:
            return (False,[])
        if i==-1 and j==-1:
            try:
                _return = self.client.table("Complaints").select("*"
                ).eq("USER",UNAM).execute()
                return (True,_return.data)
            except PostgrestAPIError as e:
                print(e)
                return (False,[]) 
        #     return (True,list(v.get_dict() for v in self.complaints.values()))
        try:
            _return = self.client.table("Complaints").select("*"
            ).eq("USER",UNAM).range(i,j).execute()
            return (True,_return.data)
        except PostgrestAPIError as e:
            return (False,[])
        
    def Get_UserComplain(self,UNAM,CID):
        try:
            CID = int(CID)
            _request = self.client.table("Complaints").select("*"
            ).eq("USER",UNAM).eq("CID",CID).execute()
            print(_request)
            return (True,_request.data[0])
        except PostgrestAPIError as e:
            return False 
    
    def Get_UserComplainLatest(self,UNAM):
        try:
            _request = self.client.table("Complaints").select("*"
            ).eq("USER",UNAM).order("CDT",desc=True).range(0,2).execute()
            print(_request)
            return (True,_request.data[0])
        except PostgrestAPIError as e:
            return False        

    def Check_Complaint(self,CID):
        try:
                _return = self.client.table("Complaints").select("*"
                ).execute()
                return len(_return.data) != 0
        except PostgrestAPIError as e:  
                return False 
        # return int(CID) in self.complaints.keys()
    
    def Create_Ticket(self,CID,DEP,PRI,STA,CRT,DES=None,ITO=False):
        try:
            self.client.table("Ticket").insert(
                {
                    "CID":CID,
                    "DEP":DEP,
                    "PRI":PRI,
                    "STA":STA,
                    "DES":DES,
                    "ITO":ITO
                }
            ).execute()
            return True
        except PostgrestAPIError as e:
            return False 
        # if int(CID) in self.complaints.keys():
        #     self.tickets[self.couter_TicketID] = Tickets(self.couter_TicketID,CID,DEP,PRI,STA,CRT)
        #     self.couter_TicketID+=1
        #     return True
        # else:
        #     return False
    def Delete_Ticket(self,TID):
        try:
            self.client.table("Ticket").delete(
            ).eq("TID",TID).execute()
            return True
        except PostgrestAPIError as e:
            return False 
        # if int(TID) in self.tickets.keys():
        #     self.tickets.pop(TID)
        #     return True
        # else:
        #     return False
    def Update_Ticket(self,TID,CID,DEP,PRI,STA,CRT,DES):
        _query = {}
        try:
            if(CID):
                _query["CID"] = CID
            if(DEP):
                _query["DEP"] = DEP
            if(PRI):
              _query[ "PRI"] = PRI
            if(STA):
                _query["STA"] = STA
            if DES:
                _query["DES"] = DES
            self.client.table("Ticket").update(
                _query
            ).eq("TID",TID).execute()
            return True
        except PostgrestAPIError as e:
            return False 
        # if int(TID) in self.tickets.keys():
        #     if(CID):
        #         self.tickets[TID].CID = CID
        #     if(DEP):
        #         self.tickets[TID].DEP = DEP
        #     if(PRI):
        #         self.tickets[TID].PRI = PRI
        #     if(STA):
        #         self.tickets[TID].STA = STA
        #     if(CRT):
        #         self.tickets[CRT].CRT = CRT
        #     return True
        # return False
    def Get_Tickets(self,i,j):
        if i>j:
            return (False,[])
        if i==-1 and j==-1:
            try:
                _return = self.client.table("Ticket").select("*"
                ).execute()
                return (True,_return.data)
            except PostgrestAPIError as e:
                print(e)
                return (False,[]) 
        try:
            _return = self.client.table("Ticket").select("*"
            ).gt("TID",i).lt("TID",j).execute()
            return (True,_return.data)
        except PostgrestAPIError as e:
            return (False,[])  

    def Get_Ticket(self,TID):
        try:
            TID = int(TID)
            _request = self.client.table("Ticket").select("*"
            ).eq("TID",TID).execute()
            print(_request)
            return (True,_request.data[0])
        except PostgrestAPIError as e:
            return False 
    
    def Get_UserTickets(self,UNAM,CID,ADM):
        if ADM:
            try:
                _request = self.client.table("Ticket").select("*"
                ).eq("CID",CID).order("TID",desc=False).execute()
                print(_request)
                return (True,_request.data)
            except PostgrestAPIError as e:
                return False             
        else:
            try:
                _request = self.client.table("Ticket").select("*"
                ).eq("CID",CID).eq("ITO",False).order("TID",desc=False).execute()
                print(_request)
                return (True,_request.data)
            except PostgrestAPIError as e:
                return False 
    
    def Create_KDocument(self,DNM,DTYPE,DPATH):
        try:
            self.client.table("KnowledgeDocument").insert(
                {
                    "DNM":DNM,
                    "DTYPE":DTYPE,
                    "DPATH":DPATH
                }
            ).execute()
            return True
        except PostgrestAPIError as e:
            return False 
        # self.KDocuments[self.counter_DID] = Knowlege_Document(self.counter_DID,DNM,DTYPE,DPATH)
        # self.counter_DID+=1
        # return True
    def Delete_KDocument(self,DID):
        try:
            self.client.table("KnowledgeDocument").delete(
            ).eq("DID",DID).execute()
            return True
        except PostgrestAPIError as e:
            return False
        # if int(DID) in self.KDocuments.keys():
        #     self.KDocuments.pop(DID)
        #     return True
        # else:
        #     return False
    def Get_KDocument(self):
        try:
            _return = self.client.table("KnowledgeDocument").select("*"
            ).execute()
            return _return.data
        except PostgrestAPIError as e:
            return False
    def GET_STAT(self):
        TP = self.client.table("Products").select("PID",count="exact",head=True).execute().count
        TD =self.client.table("KnowledgeDocument").select("DID",count="exact",head=True).execute().count
        TC=self.client.table("Complaints").select("CID",count="exact",head=True).execute().count
        TT =self.client.table("Ticket").select("TID",count="exact",head=True).execute().count
        TR =self.client.table("Ticket").select("TID",count="exact",head=True).eq("STA",True).execute().count
        return Stats(TP,TD,TC,TT,TR).get_dict()

    def Get_DasOverview(self):
        TC = (
            self.client.table("Complaints")
            .select("CID", count="exact")
            .execute()
            .count or 0
        )

        RC = (
            self.client.table("Complaints")
            .select("CID", count="exact")
            .neq("CST", "false")   # use "true" if STA is stored as text
            .execute()
            .count or 0
        )

        OC = (
            self.client.table("Complaints")
            .select("CID", count="exact")
            .eq("CST", "false")  # use "false" if STA is stored as text
            .execute()
            .count or 0
        )

        HS = (
            self.client.table("Complaints")
            .select("CID", count="exact")
            .eq("CSEV", "high")
            .execute()
            .count or 0
        )
        return DAS_overview(TC,RC,OC,HS).get_dict()

    def Create_RContext(self,QUERY,CONTEXT):
        self.RContent[self.counter_RID] = Retrived_context(self.counter_RID,QUERY,CONTEXT)
        return True
    def Delete_RContext(self,RID):
        if int(RID) in self.RContent.keys():
            self.RContent.pop(RID)
            return True
        else:
            return False
    def upload_file_to_supabase(self,file, bucket_name: str, remote_destination_path: str):
        try:
            # Open the file in binary read mode
            response = (
                self.supabase.storage
                .from_(bucket_name)
                .upload(
                    file=file,
                    path=remote_destination_path,
                    file_options={"cache-control": "3600", "upsert": "false"},
                ))
            print("Upload successful!")
            return response
            
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
