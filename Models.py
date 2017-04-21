import sqlite3
import hashlib
import os
import logging

class ScorePadDB():
    
    def __init__(self, nickname = ""):
        
        self.scorepaddb = "../ScorePad.activity/"+str(nickname)+"db.sqlite"
        self.connection = sqlite3.connect(self.scorepaddb)
        self.cursor = self.connection.cursor()
        
    def insert_rubric(self, rubric):
        temp = (rubric.title, rubric.author, rubric.description, rubric.is_predefined,
                rubric.xo_name, rubric.rubric_sha, rubric.enable_points)
        insert_str = "INSERT INTO rubric_table(title, author, description,is_predefined,\
                        xo_name, rubric_sha,enable_points)\
                        VALUES(?,?,?,?,?,?,?)"
        self.cursor.execute(insert_str,temp)
        self.connection.commit()
        
    def insert_category(self, category):
        temp = (category.name, category.rubric_id, category.category_sha, category.percentage)
        insert_str = "INSERT INTO category_table(name,rubric_id,category_sha,percentage) VALUES (?,?,?,?)"
        self.cursor.execute(insert_str, temp)
        self.connection.commit()
        
    def insert_level(self, level):
        temp = (level.name,level.description,level.category_id,level.rubric_id,level.level_sha,level.points)
        insert_str = "INSERT INTO level_table(name, description, category_id, rubric_id,level_sha,points) \
                        VALUES(?,?,?,?,?,?)"
        self.cursor.execute(insert_str, temp)
        self.connection.commit()
        
    def insert_criteria2(self, category, levels, rubric_id):
        temp = (category.name, rubric_id, category.category_sha,category.percentage)
        insert_str = "INSERT INTO category_table(name,rubric_id,category_sha,percentage) VALUES (?,?,?,?)"
        self.cursor.execute(insert_str, temp)
        self.connection.commit()
        
        query_str = "SELECT MAX(category_id) from category_table"
        self.cursor.execute(query_str)
        category_id = self.cursor.fetchone()[0]
        
        insert_str = "INSERT INTO level_table(name,description,category_id,rubric_id,level_sha,points)\
                            VALUES(?,?,?,?,?,?)"
        for level in levels:
            temp = (level.name, level.description,category_id,\
                    rubric_id, level.level_sha,level.points)
            self.cursor.execute(insert_str, temp)
            self.connection.commit()
        
    def query_maxrubric(self):
        query_str = "SELECT MAX(rubric_id) from rubric_table"
        self.cursor.execute(query_str)
        rubric_id = self.cursor.fetchone()[0]
        return rubric_id
    
    def query_level(self,category_id):
        
        query_str = "SELECT * from level_table where category_id ="+str(category_id)
        self.cursor.execute(query_str)
        
        level_list = []
        for row in self.cursor:
            level = Level(row[0], row[1], row[2], row[3], row[4], row[5],row[6])
            level_list.append(level)
        return level_list
    
    def rubric_exists(self, title, author):
        temp = (title, author)
        query_str = "SELECT * FROM rubric_table WHERE title = ? and author = ?"
        
        self.cursor.execute(query_str, temp)
        for row in self.cursor:
            rubric = Rubric(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7])
        
        try:
            if rubric.rubric_id == None:
                return None
            else:
                return rubric.rubric_id
        except:
            return None
    
    def close_db(self):
        self.cursor.close()

class YardStickDB():
    
    def connect_db(self, nickname = ""):
        is_newlycreated = False
        self.yardstickdb = str(nickname)+"db.sqlite"
        if not os.path.isfile(self.yardstickdb):
            logging.debug("the database already exist")
        
        self.connection = sqlite3.connect(self.yardstickdb)
        logging.debug("ScorepadDB-->connect")
        self.cursor = self.connection.cursor()
        try:
            self.create_tables()
            is_newlycreated = True
            logging.debug("ScorepadDB -->create_tables")
        except:
            logging.debug("Exception here")
        
        return is_newlycreated
        
    def create_tables(self):
        rubric_table = "CREATE TABLE rubric_table (rubric_id INTEGER PRIMARY KEY,\
                                                title VARCHAR(40) NOT NULL,\
                                                author VARCHAR(40) NOT NULL,\
                                                description TEXT,\
                                                is_predefined INTEGER,\
                                                xo_name VARCHAR(50),\
                                                rubric_sha TEXT,\
                                                enable_points INTERGER)"
        category_table = "CREATE TABLE category_table (category_id INTEGER PRIMARY KEY,\
                                                    name VARCHAR(40) NOT NULL,\
                                                    rubric_id INTEGER NOT NULL REFERENCES rubric_table(rubric_id),\
                                                    category_sha TEXT,\
                                                    percentage FLOAT)"
        
        level_table = "CREATE TABLE level_table (level_id INTEGER PRIMARY KEY,\
                                            name VARCHAR(40) NOT NULL,\
                                            description TEXT NOT NULL,\
                                            category_id INTEGER NOT NULL REFERENCES category_table(category_id),\
                                            rubric_id INTEGER NOT NULL REFERENCES rubric_table(rubric_id),\
                                            level_sha TEXT,\
                                            points INTEGER)"
                                                    
        project_table = "CREATE TABLE project_table (project_id INTEGER PRIMARY KEY,\
                                                title VARCHAR(40) NOT NULL,\
                                                author VARCHAR(40) NOT NULL,\
                                                description TEXT,\
                                                subject VARCHAR(40),\
                                                publish_date TEXT,\
                                                is_owned INTEGER,\
                                                is_shared INTEGER,\
                                                rubric_id INTEGER NOT NULL REFERENCES rubric_table(rubric_id),\
                                                xo_name VARCHAR(50),\
                                                project_sha TEXT,\
                                                total_score FLOAT)"
        
        score_table = "CREATE TABLE score_table (score_id INTEGER PRIMARY KEY,\
                                                project_id INTEGER NOT NULL REFERENCES project_table(project_id),\
                                                rubric_id INTEGER NOT NULL REFERENCES rubric_table(rubric_id),\
                                                category_id INTEGER NOT NULL REFERENCES category_table(category_id),\
                                                level_id INTEGER NOT NULL REFERENCES level_table(level_id),\
                                                project_sha TEXT REFERENCES project_table(project_sha),\
                                                rubric_sha TEXT REFERENCES rubric_table(rubric_sha),\
                                                category_sha TEXT REFERENCES category_table(category_sha),\
                                                level_sha TEXT REFERENCES level_table(level_sha),\
                                                count INTEGER NOT NULL)"
        
        self.cursor.execute(rubric_table)
        print "rubric table created"       
        self.cursor.execute(category_table)
        print "category table created"
        self.cursor.execute(level_table)
        print "level table created"
        self.cursor.execute(project_table)
        print "project table created"
        self.cursor.execute(score_table)
        print "score table created"
        
    def insert_rubric(self, rubric):
        temp = (rubric.title, rubric.author, rubric.description, rubric.is_predefined,
                rubric.xo_name, rubric.rubric_sha, rubric.enable_points)
        insert_str = "INSERT INTO rubric_table(title, author, description,is_predefined,\
                        xo_name,rubric_sha,enable_points)\
                        VALUES(?,?,?,?,?,?,?)"
        self.cursor.execute(insert_str,temp)
        self.connection.commit()
        
    def query_maxrubric(self):
        query_str = "SELECT MAX(rubric_id) from rubric_table"
        self.cursor.execute(query_str)
        rubric_id = self.cursor.fetchone()[0]
        return rubric_id
    
    def insert_criteria(self, category, levels):
        temp = (category.name, category.rubric_id,category.category_sha,category.percentage)
        insert_str = "INSERT INTO category_table(name,rubric_id,category_sha,percentage) VALUES (?,?,?,?)"
        self.cursor.execute(insert_str, temp)
        self.connection.commit()
        
        query_str = "SELECT MAX(category_id) from category_table"
        self.cursor.execute(query_str)
        category_id = self.cursor.fetchone()[0]
        
        insert_str = "INSERT INTO level_table(name,description,category_id,rubric_id,level_sha,points)\
                            VALUES(?,?,?,?,?,?)"
        for i in range(len(levels)):
            temp = (levels[i].name, levels[i].description,category_id ,\
                    levels[i].rubric_id, levels[i].level_sha, levels[i].points)
            self.cursor.execute(insert_str, temp)
            self.connection.commit()
    
    def insert_project(self, project):
        temp = (project.title, project.author, project.description, project.subject,\
                project.publish_date, project.is_owned,\
                project.is_shared, project.rubric_id,project.xo_name,\
                project.project_sha,project.total_score)
        
        insert_str = "INSERT INTO project_table(title, author, description, subject,\
                        publish_date, is_owned, is_shared, rubric_id,xo_name,\
                        project_sha,total_score) VALUES (?,?,?,?,?,?,?,?,?,?,?)"
                        
        self.cursor.execute(insert_str,temp)
        self.connection.commit()
        
    def query_maxproject(self):
        query_str = "SELECT MAX(project_id) from project_table"
        self.cursor.execute(query_str)
        project_id = self.cursor.fetchone()[0]
        return project_id

    def insert_score(self, score):
        temp = (score.project_id, score.rubric_id, score.category_id, score.level_id,
                score.project_sha, score.rubric_sha, score.category_sha, score.level_sha, score.count)
        insert_str = "INSERT INTO score_table(project_id,rubric_id,category_id,level_id,\
                        project_sha, rubric_sha, category_sha, level_sha, count)\
                        VALUES (?,?,?,?,?,?,?,?,?)"
        self.cursor.execute(insert_str,temp)
        self.connection.commit()
        
    def insert_category(self, category):
        temp = (category.name,category.rubric_id,category.category_sha,category.percentage)
        insert_str = "INSERT INTO category_table(name,rubric_id,category_sha,percentage) VALUES (?,?,?,?)"
        self.cursor.execute(insert_str, temp)
        self.connection.commit()
        
    def insert_level(self, level):
        temp = (level.name, level.description, level.category_id, level.rubric_id, level.level_sha, level.points)
        insert_str = "INSERT INTO level_table(name, description, category_id, rubric_id, level_sha, points) \
                        VALUES(?,?,?,?,?,?)"
        self.cursor.execute(insert_str, temp)
        self.connection.commit()
        
    
    def query_maxscore(self):
        query_str = "SELECT MAX(score_id) from score_table"
        self.cursor.execute(query_str)
        score_id = self.cursor.fetchone()[0]
        return score_id
    
    def query_maxcategory(self):
        query_str = "SELECT MAX(category_id) from category_table"
        self.cursor.execute(query_str)
        category_id = self.cursor.fetchone()[0]
        return category_id
            
    def queryall_rubric(self, is_predefined):
        query_str = "SELECT * from rubric_table where is_predefined = "+str(is_predefined)
        self.cursor.execute(query_str)
        
        rubric_list = []
        for row in self.cursor:
            rubric = Rubric(row[0], row[1], row[2], row[3], row[4], row[5], row[6],row[7])
            rubric_list.append(rubric)
        return rubric_list
    
    def queryall_project(self, is_owned):
        query_str = "SELECT * from project_table where is_owned = "+str(is_owned)
        self.cursor.execute(query_str)
        
        project_list = []
        for row in self.cursor:
            project = Project(row[0],row[1],row[2],row[3],row[4],
                              row[5],row[6],row[7],row[8], row[9],row[10],row[11])
            project_list.append(project)
        return project_list
    
    def query_rubric(self, rubric_id):
        query_str = "SELECT * from rubric_table where rubric_id = "+str(rubric_id)
        self.cursor.execute(query_str)
        
        for row in self.cursor:
            rubric = Rubric(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7])
        
        return rubric
    
    def queryall_category(self, rubric_id):
        query_str = "SELECT * from category_table where rubric_id = "+str(rubric_id)
        self.cursor.execute(query_str)
        
        category_list = []
        for row in self.cursor:
            category = Category(row[0], row[1], row[2], row[3],row[4])
            category_list.append(category)
        return category_list
    
    def query_level(self,category_id):
        
        query_str = "SELECT * from level_table where category_id ="+str(category_id)
        self.cursor.execute(query_str)
        
        level_list = []
        for row in self.cursor:
            level = Level(row[0], row[1], row[2], row[3], row[4], row[5],row[6])
            level_list.append(level)
        return level_list
    
    def querylevel_id(self, category_id, level_name):
        temp = (category_id, level_name)
        query_str = "SELECT level_id from level_table WHERE category_id = ? and name = ?"
        self.cursor.execute(query_str,temp)
        level_id = self.cursor.fetchone()[0]
        return level_id

    def query_score(self, project_id, rubric_id, category_id, level_id):
        temp = (project_id, rubric_id, category_id, level_id)
        query_str = "SELECT count from score_table WHERE project_id = ? \
                    and rubric_id = ? and category_id = ? and \
                    level_id = ?"
        self.cursor.execute(query_str, temp)
        count = self.cursor.fetchone()[0]
        return count

    def query_score2(self, project_id, rubric_id, category_id, level_id):
        temp = (project_id, rubric_id, category_id, level_id)
        query_str = "SELECT * from score_table WHERE project_id = ? \
                    and rubric_id = ? and category_id = ? and \
                    level_id = ?"

        self.cursor.execute(query_str, temp)
        for row in self.cursor:
            score = Score(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9])
        return score

    def query_project_sha(self, project_id):
        query_str = "SELECT project_sha from project_table WHERE project_id = "+ str(project_id)
        self.cursor.execute(query_str)
        
        project_sha = self.cursor.fetchone()[0]
        return str(project_sha)
        
    def query_project(self, project_id):
        query_str = "SELECT * from project_table WHERE project_id ="+ str(project_id)
        self.cursor.execute(query_str)        

        for row in self.cursor:
            project = Project(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11])

        return project

    def query_rubric_sha(self, rubric_id):
        query_str = "SELECT rubric_sha from rubric_table WHERE rubric_id = "+ str(rubric_id)
        self.cursor.execute(query_str)
        
        rubric_sha = self.cursor.fetchone()[0]
        return str(rubric_sha)       

    def query_category_sha(self, category_id):
        query_str = "SELECT category_sha from category_table WHERE category_id = "+ str(category_id)
        self.cursor.execute(query_str)
        
        category_sha = self.cursor.fetchone()[0]
        return str(category_sha)
    
    def query_level_sha(self, level_id):
        query_str = "SELECT level_sha from level_table WHERE level_id = "+ str(level_id)
        self.cursor.execute(query_str)
        
        level_sha = self.cursor.fetchone()[0]
        return str(level_sha)
    
    def query_score_id(self, project_sha, rubric_sha, category_sha, level_sha):
        temp = (project_sha, rubric_sha, category_sha, level_sha)
        query_str = "SELECT score_id from score_table WHERE project_sha = ? \
                    and rubric_sha = ? and category_sha = ? and level_sha = ?"
        self.cursor.execute(query_str, temp)
        score_id = self.cursor.fetchone()[0]
        return score_id
    
    def is_points_enabled(self, rubric_id):
        query_str = "SELECT enable_points from rubric_table WHERE rubric_id = " + str(rubric_id)
        self.cursor.execute(query_str)
        enable_points = self.cursor.fetchone()[0]
        if enable_points == 0:
            return False
        else :
            return True
    
    def queryall_level(self, rubric_id):
        query_str = "SELECT * from level_table where rubric_id = "+str(rubric_id)
        self.cursor.execute(query_str)
        
        level_list = []
        for row in self.cursor:
            level = Level(row[0],row[1],row[2],row[3],row[4],row[5],row[6])
            level_list.append(level)
        return level_list
    
    def query_category_id(self, rubric_id, name):
        temp = (rubric_id, name)
        query_str = "SELECT * from category_table where rubric_id = ? and name = ?"
        self.cursor.execute(query_str, temp)
        category_id = self.cursor.fetchone()[0]
        
        return category_id
    
    def query_level_id(self, rubric_id, category_id, name):
        temp = (rubric_id, category_id, name)
        query_str = "SELECT * from level_table where rubric_id = ? and category_id = ? and name = ?"
        self.cursor.execute(query_str, temp)
        level_id = self.cursor.fetchone()[0]
        
        return level_id

    def update_project(self, modified_project):
        temp = (modified_project.title,modified_project.author,modified_project.description,\
                        modified_project.subject,\
                        modified_project.publish_date,\
                        modified_project.rubric_id,modified_project.project_sha,\
                        modified_project.total_score,\
                        modified_project.project_id)
        update_str = "UPDATE project_table SET title = ?,"+\
                        "author = ?, "+\
                        "description = ?,"+\
                        "subject = ?,"+\
                        "publish_date = ?,"+\
                        "rubric_id = ?,"+\
                        "project_sha = ?"+\
                        "total_score = ?"+\
                        "WHERE project_id = ?"
        self.cursor.execute(update_str,temp)
        self.connection.commit()
        
    def update_levels(self, modified_levels):
        
        for i in modified_levels:
            temp = (i.name,i.description,i.level_id,)
            update_str = "UPDATE level_table SET name = ?,"+\
                            "description = ?"+\
                            "WHERE level_id = ?"
            self.cursor.execute(update_str,temp)
            self.connection.commit()
            
    def update_level(self, modified_level):
        temp = (modified_level.name,modified_level.description,modified_level.level_id,)
        update_str = "UPDATE level_table SET name = ?,"+\
                            "description = ?"+\
                            "WHERE level_id = ?"
        self.cursor.execute(update_str,temp)
        self.connection.commit()
            
    def update_categories(self, modified_categories):
        for i in modified_categories:
            temp = (i.name,i.rubric_id,i.category_id)
            update_str = "UPDATE category_table SET name = ?"+\
                            "WHERE rubric_id = ? and category_id = ?"
            self.cursor.execute(update_str,temp)
            self.connection.commit()
            
    def update_category(self, modified_category):
        temp = (modified_category.name,modified_category.rubric_id,modified_category.category_id)
        update_str = "UPDATE category_table SET name = ?"+\
                            "WHERE rubric_id = ? and category_id = ?"
        self.cursor.execute(update_str,temp)
        self.connection.commit()
            
    def update_rubric(self, modified_rubric):
        temp = (modified_rubric.title,modified_rubric.author,modified_rubric.description,modified_rubric.enable_points,
                modified_rubric.rubric_id)
        update_str = "UPDATE rubric_table SET title = ?,"+\
                        "author = ?, "+\
                        "description = ?,"+\
                        "enable_points = ?"+\
                        "WHERE rubric_id = ?"
        self.cursor.execute(update_str,temp)
        self.connection.commit()
        
    def update_percentage(self, category_id, percentage):
        temp = (percentage, category_id)
        update_str = "UPDATE category_table SET percentage = ?"+\
                        "WHERE category_id = ?"
        self.cursor.execute(update_str, temp)
        self.connection.commit()
        
    def update_points(self, category_id, level_name, points):
        temp = (points, category_id, level_name)
        update_str = "UPDATE level_table SET points = ?"+\
                        "WHERE category_id = ? and name = ?"
        self.cursor.execute(update_str, temp)
        self.connection.commit()
        
    def update_enablepoints(self, rubric_id, is_enable):
        temp = (is_enable, rubric_id)
        update_str = "UPDATE rubric_table SET enable_points = ?"+\
                        "WHERE rubric_id = ?"
        self.cursor.execute(update_str, temp)
        self.connection.commit()
        
        
    
    def delete_project(self, project_id):
        delete_str = "DELETE FROM project_table WHERE project_id ="+ str(project_id)
        self.cursor.execute(delete_str)
        
        self.connection.commit()
        
    def delete_rubric(self, rubric_id):
        delete_str = "DELETE FROM rubric_table WHERE rubric_id ="+ str(rubric_id)
        self.cursor.execute(delete_str)
        
        delete_str = "DELETE FROM category_table WHERE rubric_id ="+ str(rubric_id)
        self.cursor.execute(delete_str)
        
        delete_str = "DELETE FROM level_table WHERE rubric_id ="+ str(rubric_id)
        self.cursor.execute(delete_str)
        
        self.connection.commit()
        
    def score_exists(self, project_id, rubric_id, category_id, level_id):
        temp = (project_id, rubric_id, category_id, level_id)
        query_str = "SELECT * FROM score_table WHERE project_id = ? and rubric_id = ? and \
                        category_id = ? and level_id = ?"
        
        self.cursor.execute(query_str, temp)
        for row in self.cursor:
            score = Score(row[0],row[1],row[2],row[3],row[4],row[5],row[6],\
                          row[7],row[8],row[9])
        
        try:
            if score.score_id == None:
                return False
            else:
                return True
        except:
            return False
        
    def project_exists(self, project_sha, author):
        temp = (project_sha, author)
        query_str = "SELECT * FROM project_table WHERE project_sha = ? and author = ?"
        
        self.cursor.execute(query_str, temp)
        for row in self.cursor:
            project = Project(row[0],row[1],row[2],row[3],row[4],row[5],row[6],\
                          row[7],row[8],row[9],row[10],row[11])
        
        try:
            if project.project_id == None:
                return False
            else:
                return True
        except:
            return False
    
    def rubric_exists(self, rubric_sha, description):
        temp = (rubric_sha, description)
        query_str = "SELECT * FROM rubric_table WHERE rubric_sha = ? and description = ?"
        
        self.cursor.execute(query_str, temp)
        for row in self.cursor:
            rubric = Rubric(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7])
        
        try:
            if rubric.rubric_id == None:
                return None
            else:
                return rubric.rubric_id
        except:
            return None
        
    def rubric_title_exists(self, rubric_title):
        query_str = "SELECT * FROM rubric_table WHERE title = \'" + str(rubric_title) +"\'"
        self.cursor.execute(query_str)
        count = 0
        for row in self.cursor:
            rubric = Rubric(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7])
            count = count+1
            
        try:
            if rubric.rubric_id == None:
                return None
            else:
                return count
        except:
            return None
        
    def query_score_attr(self, score_id):
        query_str = "SELECT * from score_table WHERE score_id = " + str(score_id)
        self.cursor.execute(query_str)
        
        for row in self.cursor:
            score = Score(row[0],row[1],row[2],row[3],row[4],row[5],row[6],\
                          row[7],row[8],row[9])
        
        attr = [score.project_id, score.rubric_id, score.category_id, score.level_id]
        return attr
        
        
    def increment_scorecount(self, project_id, rubric_id, category_id, level_id):
        temp = (project_id, rubric_id, category_id, level_id)
        query_str = "SELECT * FROM score_table WHERE project_id = ? and rubric_id = ? and \
                        category_id = ? and level_id = ?"
        self.cursor.execute(query_str, temp)
        
        for row in self.cursor:
            score = Score(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9])
        
        score_id = score.score_id
        count = score.count
        count = count +1
        temp = (count, score_id)
        update_str = "UPDATE score_table SET count = ?"+\
                        "WHERE score_id = ?"
        self.cursor.execute(update_str, temp)
        self.connection.commit()
        return score_id
    
    def close_db(self):
        self.cursor.close()
    
class Project():
    
    def __init__(self, project_id = 0, title = "", author = "",
                 description = "", subject = "", publish_date = "",
                 is_owned = 1, is_shared = 1, rubric_id = None, xo_name = "",
                 project_sha = "", total_score = 0):
        self.project_id = project_id
        self.title = title
        self.author = author
        self.description = description
        self.subject = subject
        self.publish_date = publish_date
        self.is_owned = is_owned
        self.is_shared = is_shared
        self.rubric_id = rubric_id
        self.xo_name = xo_name
        self.project_sha = self.get_sha(xo_name, title, publish_date)
        self.total_score = total_score
        
    
    def get_sha(self, xo_name, title, publish_date):
        text = xo_name + title + str(publish_date)
        h = hashlib.sha1()
        h.update(text)
        project_sha = str(h.hexdigest())
        
        return project_sha
        

        
class Rubric():
    
    def __init__(self, rubric_id = 0, title = "", author = "", description = "",\
                 is_predefined =None, xo_name = "", rubric_sha = "", enable_points = 0):
        self.rubric_id = rubric_id
        self.title = title
        self.author = author
        self.description = description
        self.is_predefined = is_predefined
        self.xo_name = xo_name
        self.rubric_sha = self.get_sha(xo_name, title, author)
        self.enable_points = enable_points
        
    def get_sha(self, xo_name, title, author):
        text = xo_name + title + author
        h = hashlib.sha1()
        h.update(text)
        rubric_sha = str(h.hexdigest())
        
        return rubric_sha
        

class Category():
    
    def __init__(self, category_id = None, name = "", rubric_id = None, 
                 category_sha = "", percentage = 0.0):
        self.category_id = category_id
        self.name = name
        self.rubric_id = rubric_id
        self.category_sha = self.get_sha(name)
        self.percentage = percentage
        
    def get_sha(self, name):
        text = name
        h = hashlib.sha1()
        h.update(text)
        category_sha = str(h.hexdigest())
        
        return category_sha
    

class Level():
    
    def __init__(self, level_id = None, name = "", description = "",
                category_id = None, rubric_id = None,
                level_sha = "", points = 0):
        self.level_id = level_id
        self.name = name
        self.description = description
        self.category_id = category_id
        self.rubric_id = rubric_id
        self.level_sha = self.get_sha(name,description)
        self.points = points
        
    def get_sha(self, name, description):
        text = name + description
        h = hashlib.sha1()
        h.update(text)
        level_sha = str(h.hexdigest())
        
        return level_sha

class Score():
    
    def __init__(self, score_id = 0, project_id = None, rubric_id = None, category_id = None,level_id = None,
                 project_sha = "", rubric_sha = "", category_sha = "", level_sha = "",count = 0):
        self.score_id = score_id
        self.project_id = project_id
        self.rubric_id = rubric_id
        self.category_id = category_id
        self.level_id = level_id
        self.project_sha = project_sha
        self.rubric_sha = rubric_sha
        self.category_sha = category_sha
        self.level_sha = level_sha
        self.count = count
