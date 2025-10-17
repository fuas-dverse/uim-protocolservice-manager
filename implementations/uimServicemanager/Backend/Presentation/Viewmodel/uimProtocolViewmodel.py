from pydantic import BaseModel

class uimProtocolViewModel(BaseModel):
    uimpublickey: str
    uimpolicyfile: str
    uimApiDiscovery: str
    uimApiExceute: str