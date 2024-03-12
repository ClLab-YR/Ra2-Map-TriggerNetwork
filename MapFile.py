import globalvar as glob
from Logics import Trigger,Variable

class MapFile:
    triggers = {}
    localvar = {}
    deltatrigger = glob.triggerInit
    deltalocal = glob.localInit

    def __init__(self):
        self.triggers = {}
        self.localvar = {}

    def LoadFromIni(self, file):
        ent = file["Triggers"]
        for pair in ent.Data():
            trigger = Trigger()
            trigger.id = pair.Name
            trigger.LoadTag(pair.Value)
            self.triggers[pair.Name] = trigger
        ent = file["Events"]
        for pair in ent.Data():
            if (not pair.Name in self.triggers.keys()) or pair.IsNull():
                continue
            trigger = self.triggers[pair.Name]
            trigger.LoadEvent(pair.Value)
        ent = file["Actions"]
        for pair in ent.Data():
            if (not pair.Name in self.triggers.keys()) or pair.IsNull():
                continue
            trigger = self.triggers[pair.Name]
            trigger.LoadAction(pair.Value)
        ent = file["VariableNames"]
        if ent != None:
            for pair in ent.Data():
                sl = pair.Value.split(",")
                variable = Variable()
                variable.varname = sl[0]
                variable.varid = pair.Name
                self.localvar[pair.Name] = variable

    def Calculate(self):
        # may ignore variables interaction.
        eventids = [36, 37,  # original
                    500, 501, 502, 503, 504, 505]
        actionids = [56, 57,  # original
                     501, 502,]  # ext

        for trigger in self.triggers.values():
            for event in trigger.events:
                if event.eventid in eventids:
                    self.AddLocal(event.parameters[1])
                    self.AddTrigger(trigger.id)
                    trigger.readlocals.append(event.parameters[1])
            for action in trigger.actions:
                if action.actionid in [12, 22, 53, 54]:
                    if not action.parameters[1] in self.triggers.keys():
                        continue
                    self.AddTrigger(action.parameters[1])
                    self.AddTrigger(trigger.id)
                    trigger.movedtriggers.append(action.parameters[1])
                if action.actionid in actionids:
                    self.AddLocal(action.parameters[1])
                    self.AddTrigger(trigger.id)
                    trigger.setlocals.append(action.parameters[1])
            if trigger.associated != "<none>":
                self.AddTrigger(trigger.associated)
                self.AddTrigger(trigger.id)

    def GetNameFromID(self, id):
        return id + "-" + self.triggers[id].name

    def GetVarFromID(self, id):
        return  "Local-" + id + ":" + self.localvar[id].varname;

    def AddLocal(self, id):
        if not id in self.localvar.keys():
            return None
        self.localvar[id].varcount += self.deltalocal

    def AddTrigger(self, id):
        if not id in self.triggers.keys():
            return None
        self.triggers[id].count += self.deltatrigger
