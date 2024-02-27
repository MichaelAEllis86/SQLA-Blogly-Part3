import os
from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag, PostTag
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc



app=Flask(__name__)
app.app_context().push()
# app.config['SQLALCHEMY_DATABASE_URI']='postgresql:///blogly_db'

# set environment variable to NOTTEST if were working the real DB in app.py, if we are in test mode in test.py this variable is set to "TEST" and we use the test database
app.config['SQLALCHEMY_DATABASE_URI']='postgresql:///blogly_db' if os.environ.get("TEST", "NOTTEST") == "NOTTEST" else 'postgresql:///test_blogly_db' 

# 'postgresql:///test_blogly_db' ------->just referencing test db name here

# Related logic to line 13 but for the echo config. If we are in the test environment we are in the fake/test db and we dont echo sql. if we are in real db/app.py we echo sql.
app.config['SQLALCHEMY_ECHO']= True if os.environ.get("TEST", "NOTTEST") == "NOTTEST" else False
app.config['SECRET_KEY']="oh-so-secret"
debug=DebugToolbarExtension(app)

connect_db(app)
# <----------Blogly Home Page------------>

@app.route("/")
def show_base():
    """show home page and query/show for the 5 most recent posts"""
    
    posts=Post.query
    recent_posts=posts.order_by(desc('created_at')).limit(5).all()
   
    #could've also run the code below as the query logic! this syntax avoids the the import desc in line 6 and is springboard's solution
    # posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()


    return render_template("home.html", recent_posts=recent_posts)

# <----------Blogly User Routes------------>
@app.route("/users")
def show_user_list_page():
    """show all the users in our db"""
    users=User.query.all()
    return render_template("users.html", users=users )

@app.route("/users/new")
def show_new_user_form_page():
    """show the form page to create a new user"""
    return render_template("userform.html")

@app.route("/users/new", methods=['POST'] )
def handle_new_user_form():
    """handle the form page POST route submission to create a new user"""
    first_name=request.form["first_name"]
    last_name=request.form["last_name"]
    image_url=request.form["image_url"]
    print(f"the form data is first name={first_name} last_name={last_name} image url={image_url}")
    new_user=User(first_name=first_name, last_name=last_name, image_url=image_url)
    print(f"the new user is {new_user}")
    db.session.add(new_user)
    db.session.commit()
    flash("new user created!!")
    flash(f"your new user is {new_user.first_name} {new_user.last_name} with a user id of {new_user.id}", "success")
    return redirect("/users")

@app.route("/users/<user_id>")
def show_user_details(user_id):
    """show details about user page and the user's posts"""
    user=User.query.get_or_404(user_id)
    print("the user is", user)
    print(f"the user_id is {user_id}")
    print(f"the user_id type is {type(user_id)}")
    user_posts=user.post_info
    return render_template("userdetail.html", user=user, user_id=user_id, user_posts=user_posts)

@app.route("/users/<user_id>/edit")
def show_user_edit(user_id):
    """Show form page to edit an existing user"""
    user=User.query.get_or_404(user_id)
    return render_template("usereditform.html", user=user,user_id=user_id)

@app.route("/users/<user_id>/edit", methods=['POST'])
def handle_user_edit(user_id):
    """handle the user edit post form submission to edit a user"""
    first_name=request.form["first_name"]
    last_name=request.form["last_name"]
    image_url=request.form["image_url"]
    user=User.query.get_or_404(int(user_id))
    print(f"this is the intial user{user}")
    user.first_name=first_name
    user.last_name=last_name
    user.image_url=image_url
    print(f"this is user now {user}")
    db.session.add(user)
    db.session.commit()
    flash("user edited!!")
    flash(f"your user is now {user.first_name}{user.last_name} with a user id of {user.id}", "success")
    return redirect("/users")

@app.route("/users/<user_id>/delete", methods=['POST'])
def handle_user_delete(user_id):
    print(f" the initial user_id is {user_id} and it's type is {type(user_id)}")
    integer_user_id=int(user_id)
    user=User.query.get_or_404(int(user_id))
    User.query.filter_by(id=integer_user_id).delete()
    db.session.commit()
    flash("user deleted!!")
    flash(f"the previous user of {user.first_name}{user.last_name} with a user id of {user.id} is now deleted", "success")
    return redirect("/users")

# <----------Blogly Post Routes------------>

#updated for tags!
@app.route("/users/<user_id>/posts/new")
def show_new_post_form_page(user_id):
    user=User.query.get_or_404(int(user_id))
    integer_user_id=int(user_id)
    tags=Tag.query.all()
    return render_template("newpostform.html", user=user, integer_user_id=integer_user_id, tags=tags)
#updated for tags!
@app.route("/users/<user_id>/posts/new", methods=['POST'])
def handle_new_post_form_page(user_id):
    integer_user_id=int(user_id)
    post_title=request.form['title']
    post_content=request.form['content']
    post_tag_list=request.form.getlist('tags')
    print(f"the form data is post_title={post_title} post_content={post_content}")
    print(f" The post_tag_list form data is {post_tag_list}")
    new_post=Post(title=post_title, content=post_content, user_id=int(user_id))
    db.session.add(new_post)
    db.session.commit()
    for tag in post_tag_list:
        new_tag=Tag.query.get(int(tag))
        new_post.post_tags.append(new_tag)
        db.session.add(new_tag)
        db.session.commit()
    flash("new post created!!")
    flash(f"your new post is {new_post.title}, created by {new_post.user_info.first_name} {new_post.user_info.last_name} on {new_post.format_date()}", "success")
    return redirect (f"/users/{integer_user_id}")

#updated for tags!
@app.route("/posts/<post_id>")
def show_post(post_id):
    integer_post_id=int(post_id)
    post=Post.query.get_or_404(integer_post_id)
    post_tags=post.post_tags
    print(post_tags)
    integer_user_id=int(post.user_info.id)
    return render_template("showpost.html", post=post, integer_user_id=integer_user_id, post_tags=post_tags)

@app.route("/posts/<post_id>/edit")
def show_edit_post_form_page(post_id):
    integer_post_id=int(post_id)
    post=Post.query.get_or_404(integer_post_id)
    integer_user_id=int(post.user_info.id)
    tags=Tag.query.all()
    return render_template("posteditform.html", post=post, integer_user_id=integer_user_id, tags=tags)

@app.route("/posts/<post_id>/delete", methods=['POST'])
def handle_post_deletion(post_id):
    integer_post_id=int(post_id)
    post=Post.query.get_or_404(integer_post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted!!")
    flash(f"the previous post {post.title} is now deleted", "success")
    return redirect("/users")

#Under Construction! issue with repeat tags being added and causing pyscopig integrity error. Need to solve by preventing readdition of existing tags. Commented out lines concern tag logic!!!
# possible fixes 1. not show all the tags as an option, aka filter out tags already used and not render a box for them. 2. clear all tags associated with a post when we hit the edit screen for that post(this would cause loss of tags if not edit occurs!)
# 3. conditional logic, if a tag id is already associated with a post, we do not add and commit that change to the db! Fixed using this!!!
@app.route("/posts/<post_id>/edit", methods=['POST'])
def handle_edit_post(post_id):
    integer_post_id=int(post_id)
    post_title=request.form["title"]
    post_content=request.form["content"]
    post_tag_list=request.form.getlist('tags')
    post=Post.query.get_or_404(integer_post_id)
    print(f"the form data is post_title={post_title} post_content={post_content}")
    print(f" The post_tag_list form data is {post_tag_list}")
    used_tags=[idx.id for idx in post.post_tags]
    post.title=post_title
    post.content=post_content
    db.session.add(post)
    db.session.commit()
    for tag in post_tag_list:
        tag_query=Tag.query.get(int(tag))
        if tag_query.id not in used_tags:
            post.post_tags.append(tag_query)
            db.session.add(tag_query)
            db.session.commit()
    integer_user_id=int(post.user_info.id)
    flash("Post Edited!!", "success")
    return redirect (f"/posts/{integer_post_id}")


# <----------Blogly tag Routes------------>

@app.route("/tags")
def show_tag_list_page():
    """Display page that lists all existing tags"""
    tags=Tag.query.all()
    return render_template("tags.html", tags=tags)

@app.route("/tags/new")
def show_tag_form_page():
    """ display page with form to submit new tag"""
    return render_template("tagform.html")

@app.route("/tags/new", methods=['POST'] )
def handle_new_tag_form():
    """handle the tag form page POST route submission to create a new tag"""
    tag_name=request.form["name"]
    print(f"the form data is name={tag_name}")
    new_tag=Tag(name=tag_name)
    print(f"the new tag is {new_tag}")
    db.session.add(new_tag)
    db.session.commit()
    flash("new tag created!!")
    flash(f"the new tag is: {new_tag.name} with a tag id of: {new_tag.id}", "success")
    return redirect("/tags")

@app.route("/tags/<tag_id>")
def show_tags_detail(tag_id):
    """ display tag detail page with edit and delete links"""
    integer_tag_id=int(tag_id)
    tag=Tag.query.get_or_404(integer_tag_id)
    return render_template("tagdetail.html",  integer_tag_id=integer_tag_id, tag=tag )

@app.route("/tags/<tag_id>/edit")
def show_tag_edit_form(tag_id):
    """handle form submission to edit an existing tag"""
    integer_tag_id=int(tag_id)
    tag=Tag.query.get_or_404(integer_tag_id)
    return render_template("tageditform.html", tag=tag, integer_tag_id=integer_tag_id)

@app.route("/tags/<tag_id>/edit", methods=['POST'] )
def handle_tag_edit_form(tag_id):
    """handle form submission to edit an existing tag"""
    integer_tag_id=int(tag_id)
    tag=Tag.query.get_or_404(integer_tag_id)
    tag_name=request.form["name"]
    print(f"the form data is name={tag_name}")
    tag.name=tag_name
    print(f"the edited tag is {tag}")
    db.session.add(tag)
    db.session.commit()
    flash("tag edited!!", "success")
    return redirect("/tags")

@app.route("/tags/<tag_id>/delete", methods=['POST'])
def handle_tag_delete(tag_id):
    """Handle deletion of a tag via form submit on tags detail page"""
    integer_tag_id=int(tag_id)
    tag=Tag.query.get_or_404(integer_tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash("tag deleted!!")
    flash(f"the previous tag: {tag.name} is now deleted", "success")
    return redirect ("/tags")

    

#Routes for custom 404 page if a query is unsucessful or we use a bad user or post id somewhere/somehow

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error=e), 404
    
# to do!!!!!
# further study for part 3, new route testing, update  edit post routes so a user may apply tags to a post

# DONE!seems like what we should do is query for all the tags, loop over a list of those tags and display them in a multi-input form, then make sure we grab that data and update M2M/secondary table with form info



