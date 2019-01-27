from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, States, Base, MenuItem

engine = create_engine('sqlite:///projectdatabase.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
user1 = User(name="admin", email="jyoshnamaniaddala@gmail.com")
session.add(user1)
session.commit()

state1 = States(name="Andhra pradesh", user_id=1)

session.add(state1)
session.commit()

menuItem1 = MenuItem(name="pulihora", state=state1, user_id=1)

session.add(menuItem1)
session.commit()
menuItem2 = MenuItem(name="pansapattu curry", state=state1, user_id=1)

session.add(menuItem2)
session.commit()
menuItem3 = MenuItem(name="palakova", state=state1, user_id=1)

session.add(menuItem3)
session.commit()
state2 = States(name="Telangana", user_id=1)

session.add(state2)
session.commit()

menuItem1 = MenuItem(name="hyderabadi dum birayani", state=state2, user_id=1)

session.add(menuItem1)
session.commit()
menuItem2 = MenuItem(name="haleem", state=state2, user_id=1)

session.add(menuItem2)
session.commit()
menuItem3 = MenuItem(name="gongura chutney", state=state2, user_id=1)

session.add(menuItem3)
session.commit()
