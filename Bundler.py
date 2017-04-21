from Models import *

class Bundler():
    
    def bundle_rubric(self,rubric):
        
        rubric_bundle = "Rubric|" + str(rubric.rubric_id)+"|"+rubric.title+"|"+\
                        rubric.author+"|"+rubric.description+"|"+\
                        str(rubric.is_predefined) +"|"+rubric.xo_name +"|"+\
                        rubric.rubric_sha+"|"+str(rubric.enable_points)
                        
        return rubric_bundle
    
    def bundle_category(self, categories):
        
        categorylist = []
        for category in categories:
            bundle = "Category|" + str(category.category_id)+"|"+category.name+"|"+\
                str(category.rubric_id) +"|"+\
                category.category_sha+"|"+str(category.percentage)
            categorylist.append(bundle)
        
        return categorylist
    
    def bundle_level(self, levels):
        
        levelist = []
        for level in levels:
            bundle = "Level|" + str(level.level_id) +"|"+ level.name+"|"+level.description+"|"+\
                str(level.category_id)+"|"+str(level.rubric_id)+"|"+\
                level.level_sha+"|"+str(level.points)
            levelist.append(bundle)
                
        return levelist