from CreatorTableService import creators_to_dataframe


class UIService:

    def __init__(self, creator_database):
        self.creator_database = creator_database


    def get_table(self):
        return creators_to_dataframe(self.creator_database)


    def display(self, api_service):
        from CreatorIntelligenceUI import CreatorIntelligence

        uic = CreatorIntelligence(self.creator_database, api_service)
        uic.run()

