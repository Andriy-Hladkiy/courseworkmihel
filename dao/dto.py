class StudentRequirementDTO:

    def __init__(self, ukey, student_recordbook, requirement_name):
        self.ukey = ukey
        self.student_recordbook = student_recordbook
        self.requirement_name = requirement_name

class LaboratoryRequirementDTO:

    def __init__(self, ukey, laboratory_name, requirement_name, requirement_point):
        self.ukey = ukey
        self.laboratory_name = laboratory_name
        self.requirement_name = requirement_name
        self.requirement_point = requirement_point