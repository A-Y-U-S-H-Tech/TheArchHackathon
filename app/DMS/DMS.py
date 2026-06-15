from DMS.types import * 
from itertools import islice
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
    def Create_User(self,NAM,PAS,EMA,ROL):
        if NAM not in self.users.keys():
            self.users[NAM] = USER(NAM,PAS,EMA,ROL)
            return True
        else:
            return False
    def Delete_User(self,NAM): 
        if NAM in self.users.keys():
            self.users.pop(NAM)
            return True
        return False
    def Update_User (self,NAM,PAS=None,EMA=None,ROL=None):
        if NAM in self.users.keys():
            if(PAS != None):
                self.users[NAM].PAS = PAS
            if(EMA != None):
                self.users[NAM].EMA = EMA
            if(ROL != None):
                self.users[NAM].ROL = ROL
            return True
        else:
            return False
    def Check_User(self,NAM):
        return NAM in self.users.keys()

    def Check_Validate_User(self,NAM,PAS):
        if NAM in self.users.keys():
            return self.users[NAM].PAS == PAS#type:ignore
        else:
            return False
    def Get_User_role(self,NAM):
        if NAM in self.users.keys():
            return self.users[NAM].ROL

    def Create_Product(self,PNM,PCAT,PDES,PSTA):
        self.products[self.counter_PID] = product(self.counter_PID,PNM,PCAT,PDES,PSTA)
        self.counter_PID+=1
        return True
    
    def Create_Complaint(self,CUS,PID,CDES,CST,CSEV,CDT):
        if PID in self.products.keys():
            self.complaints[self.counter_CID] = Complaint(self.counter_CID,CUS,PID,CDES,CST,CSEV,CDT)
            self.counter_CID+=1
            return True
        else:
            return False
    def Delete_Complaint(self,CID):
        if CID in self.complaints.keys():
            self.complaints.pop(CID)
            return True
        else:
            return False
    def Update_Complaint(self,CID,CUS,PID,CDES,CST,CSEV,CDT):
        if CID in self.complaints.keys():
            if(CUS):
                self.complaints[CID].CUS = CUS
            if(CDES):
                self.complaints[CID].CDES = CDES
            if(PID):
                self.complaints[CID].PID = PID
            if(CST):
                self.complaints[CST].CST = CST
            if(CSEV):
                self.CSEV = CSEV
            if(CDT) :
                self.CDT = CDT
            return True
        else:
            return False
    def Get_Complaints(self,i,j):
        if j >= len(self.complaints):
            return (False,[])
        if i>j:
            return (False,[])
        if i==-1 and j==-1:
            return (True,list(v.get_dict() for v in self.complaints.values()))
        return (True,list(v.get_dict() for v in islice(self.complaints.values(),i,j)))
    
    def Get_Complaint(self,CID):
        if CID in self.complaints.keys():
            return (True,self.complaints[CID].get_dict())
        else:
            return (False,{})

    def Check_Complaint(self,CID):
        return CID in self.complaints.keys()
    
    def Create_Ticket(self,CID,DEP,PRI,STA,CRT):
        if CID in self.complaints.keys():
            self.tickets[self.couter_TicketID] = Tickets(self.couter_TicketID,CID,DEP,PRI,STA,CRT)
            self.couter_TicketID+=1
            return True
        else:
            return False
    def Delete_Ticket(self,TID):
        if TID in self.tickets.keys():
            self.tickets.pop(TID)
            return True
        else:
            return False
    def Update_Ticket(self,TID,CID,DEP,PRI,STA,CRT):
        if TID in self.tickets.keys():
            if(CID):
                self.tickets[TID].CID = CID
            if(DEP):
                self.tickets[TID].DEP = DEP
            if(PRI):
                self.tickets[TID].PRI = PRI
            if(STA):
                self.tickets[TID].STA = STA
            if(CRT):
                self.tickets[CRT].CRT = CRT
            return True
        return False
    
    def Create_KDocument(self,DID,DNM,DTYPE,DPATH):
        self.KDocuments[DID] = Knowlege_Document(DID,DNM,DTYPE,DPATH)
        return True
    def Delete_KDocument(self,DID):
        if DID in self.KDocuments.keys():
            self.KDocuments.pop(DID)
            return True
        else:
            return False
        
    def Create_RContext(self,QUERY,CONTEXT):
        self.RContent[self.counter_RID] = Retrived_context(self.counter_RID,QUERY,CONTEXT)
        return True
    def Delete_RContext(self,RID):
        if RID in self.RContent.keys():
            self.RContent.pop(RID)
            return True
        else:
            return False