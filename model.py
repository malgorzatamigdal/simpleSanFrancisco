import config
import bcrypt
from datetime import datetime, date, timedelta

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, Text

from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref

from flask.ext.login import UserMixin

engine = create_engine(config.DB_URI, echo=False) 
session = scoped_session(sessionmaker(bind=engine,
                         autocommit = False,
                         autoflush = False))

Base = declarative_base()
Base.query = session.query_property()




class User(Base, UserMixin):
    __tablename__ = "users" 

    id = Column(Integer, primary_key=True)
    email = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)
    salt = Column(String(64), nullable=False)



    def set_password(self, password):
        self.salt = bcrypt.gensalt()
        password = password.encode("utf-8")
        self.password = bcrypt.hashpw(password, self.salt)

    def authenticate(self, password):
        password = password.encode("utf-8")
        return bcrypt.hashpw(password, self.salt.encode("utf-8")) == self.password


# Each plan can have many timelines 
class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User",backref="plans")
    timelines = relationship("Timeline", uselist=True)

    def date_range(self):
        result = []
        current = self.start_date
        while current <= self.end_date:
            result.append(current)
            current = current + timedelta(days=1)
        return result



# Timeline belongs to plan 
class Timeline(Base):
    __tablename__ = "timelines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime)
    plan_id = Column(Integer, ForeignKey("plans.id"))

    plan = relationship("Plan")
    timeline_activities = relationship("TimelineActivity", uselist=True)
    


class TimelineActivity(Base):
    __tablename__ = "timeline_activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey("activities.id"))
    timeline_id = Column(Integer, ForeignKey("timelines.id"))
    order = Column(Integer)

    timeline = relationship("Timeline")
    activity = relationship("Activity")



# Activity belong to category 
class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(80))
    photo_url = Column(String(120))
    description = Column(String(1000))
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    category = relationship("Category")
    timeline_activities = relationship("TimelineActivity", uselist=True)




# Each Category has many activities 
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer,primary_key=True, autoincrement=True)
    name = Column(String(80))
    symbol_url = Column(String(120))
    #time_string = Column(String(40))
    activities = relationship("Activity", uselist=True) 

    def suitable_time(self, time):
        #time looks like this : "10-12"
        #split the time_string so it looks like this : ["10-12", "12-2"]
        #if the time we've asked about is in the time_string array that we just split
        #if time in time_list:
            #return true
        #else
            #return false
            pass


def create_tables():
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    create_tables()



