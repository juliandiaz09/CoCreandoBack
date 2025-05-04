class project:
    def __init__(self, id, title, description, category, financial_goal,  
             funds_raised, deadline, development_city, creator_id, status="pending"):
        self.id = id
        self.title = title
        self.description = description
        self.category = category
        self.financial_goal = financial_goal
        self.funds_raised = funds_raised
        self.deadline = deadline
        self.development_city = development_city
        self.creator_id = creator_id
        self.status = status  # Status: "pending", "active", "completed", "cancelled"

    def to_json(self):
        return self.__dict__
    
