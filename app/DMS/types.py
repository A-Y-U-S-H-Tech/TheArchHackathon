class product:
    __slots__ = "PID","PNM","PCAT","PDES","PSTA"
    def __init__(self,PID,PNM,PCAT,PDES,PSTA):
        self.PID = PID
        self.PNM = PNM
        self.PCAT = PCAT
        self.PDES = PDES
        self.PSTA = PSTA
    def get_dict(self):
        return {
            "PID":self.PID,
            "PNM":self.PNM,
            "PCAT":self.PCAT,
            "PDEs":self.PDES,
            "PSTA":self.PSTA
        }

class Complaint:
    def __init__(self,CID,CUS,PID,CDES,CST,CSEV,CDT):
        self.CID = CID
        self.CUS = CUS
        self.PID = PID
        self.CDES = CDES
        self.CST = CST
        self.CSEV = CSEV
        self.CDT = CDT
    def get_dict(self):
        return {
            "CID":self.CID,
            "CUS":self.CUS,
            "PID":self.PID,
            "CDES":self.CDES,
            "CST":self.CST,
            "CSEV":self.CSEV,
            "CDT":self.CDT
        }
    
class Tickets:
    def __init__(self,TID,CID,DEP,PRI,STA,CRT) -> None:
            self.TID = TID
            self.CID = CID
            self.DEP = DEP
            self.PRI = PRI
            self.STA = STA
            self.CRT = CRT
    def get_dict(self):
         return {
              "TID":self.TID,
              "CID":self.CID,
              "DEP":self.DEP,
              "PRI":self.PRI,
              "STA":self.STA,
              "CRT":self.CRT
         }
    
class Knowlege_Document:
    def __init__(self,DID,DNM,DTYPE,DPATH):
          self.DID = DID
          self.DNM = DNM
          self.DTYPE = DTYPE
          self.DPATH = DPATH
    def get_dict(self):
         return {
              "DID":self.DID,
              "DNM":self.DNM,
              "DTYPE":self.DTYPE,
              "DPATH":self.DPATH
         }         
    
class Retrived_context:
    def __init__(self,RID,QUERY,CONTEXT):
          self.RID = RID
          self.QUERY = QUERY
          self.CONTEXT = CONTEXT
    def get_dict(self):
        return {
             "RID":self.RID,
             "QUERY":self.QUERY,
             "CONTEXT":self.CONTEXT
        }

class USER:
    def __init__(self,NAM,PAS,EMA,ROL) -> None:
        self.NAM = NAM
        self.PAS = PAS
        self.EMA = EMA
        self.ROL = ROL
    def get_dict(self):
        return {
            "NAM":self.NAM,
            "PAS":self.PAS,
            "EMA":self.EMA,
            "ROL":self.ROL      
         }