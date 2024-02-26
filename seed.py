from models import User, Post, Tag, PostTag, db
from app import app

#create all tables
db.drop_all()
db.create_all()

#imageURL strings--saving as var to shorten these so the code doesnt look sloppy--
default_user_imageURL="data:image/png;base64,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"
billy_zane_imageURL="data:image/jpeg;base64,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"



u1=User(first_name="Michael", last_name="Ellis", image_url="https://astrumpeople.com/wp-content/uploads/2016/06/Albert-Einstein-1-360x360.jpeg")
u2=User(first_name="Toasty", last_name="Toastada", image_url=default_user_imageURL)
u3=User(first_name="Billy", last_name="Zane", image_url=billy_zane_imageURL)
u4=User(first_name="Rosie", last_name="Ellis", image_url=default_user_imageURL)
u5=User(first_name="Daffy", last_name="Duck", image_url=default_user_imageURL)
u6=User(first_name="Roomie", last_name="TheRoomba", image_url="https://i.chzbgr.com/full/7889062656/h10C497C8/cat-spinning-on-a-roomba")



db.session.add_all([u1,u2,u3,u4,u5,u6])
db.session.commit()

P1=Post(title="White Bread is bad for you", content="I don't like white bread", user_id=1)
P2=Post(title="Bad things to say in a text message", content="I am breaking up with you",user_id=2)
P3=Post(title="Will Taylor Swifty make it to the super bowl?", content="I sure hope so",user_id=3)
P4=Post(title="Road work ahead", content="well yeah, I sure hope it does!",user_id=4)
P5=Post(title="Minimum safe distance from a moose", content="far away....a moose can run up to 35 mph",user_id=5)
P6=Post(title="Cats can ride on Roombas", content=" If they really figure this out, they might take over the world",user_id=6)


db.session.add_all([P1,P2,P3,P4,P5,P6])
db.session.commit()

T1=Tag(name="Music")
T2=Tag(name="Sports")
T3=Tag(name="Animals")
T4=Tag(name="Pop Culture")
T5=Tag(name="Art")
T6=Tag(name="Gaming")
T7=Tag(name="Science")
T8=Tag(name="food")
T9=Tag(name="memes")


db.session.add_all([T1,T2,T3,T4,T5,T6,T7,T8,T9])
db.session.commit()

#giving each post multiple tags to test M2M relations Tags used more than once are:2X T2=Tag(name="Sports"), 3X T3=Tag(name="Animals"), 2X T4=Tag(name="Pop Culture",3X T7=Tag(name="Science"), 2X T9=Tag(name="memes"))
PT1=PostTag(post_id=P1.id, tag_id=T8.id)
PT2=PostTag(post_id=P1.id, tag_id=T7.id)
PT3=PostTag(post_id=P2.id, tag_id=T4.id)
PT4=PostTag(post_id=P2.id, tag_id=T9.id)
PT5=PostTag(post_id=P2.id, tag_id=T7.id)
PT6=PostTag(post_id=P3.id, tag_id=T1.id)
PT7=PostTag(post_id=P3.id, tag_id=T2.id)
PT8=PostTag(post_id=P3.id, tag_id=T4.id)
PT9=PostTag(post_id=P4.id, tag_id=T3.id)
PT10=PostTag(post_id=P4.id, tag_id=T6.id)
PT11=PostTag(post_id=P5.id, tag_id=T3.id)
PT12=PostTag(post_id=P5.id, tag_id=T2.id)
PT13=PostTag(post_id=P5.id, tag_id=T7.id)
PT14=PostTag(post_id=P6.id, tag_id=T3.id)
PT15=PostTag(post_id=P6.id, tag_id=T9.id)
PT16=PostTag(post_id=P6.id, tag_id=T5.id)

db.session.add_all([PT1,PT2,PT3,PT4,PT5,PT6,PT7,PT8,PT9,PT10,PT11,PT12,PT13,PT14,PT15,PT16])
db.session.commit()
