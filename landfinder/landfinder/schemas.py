from pymongo import TEXT
from pymongo.operations import IndexModel
from pymodm import connect, fields, MongoModel, EmbeddedMongoModel


# Connect to MongoDB first. PyMODM supports all URI options supported by
# PyMongo. Make sure also to specify a database in the connection string:
# connect('mongodb://localhost:27017/myApp')

class ListingResult(EmbeddedMongoModel):
    date_discovered = fields.DateTimeField()
    listing_name = fields.CharField()
    listing_html = fields.CharField()
    version = fields.IntegerField
    mail=fields.ListField(fields.CharField())

class Listing(MongoModel):
    listing_url = fields.URLField(primary_key=True)
    search_id = fields.CharField()
    iterations=fields.EmbeddedDocumentListField(ListingResult)
    class Meta:
        collection_name = "listings_realestate_com_au"

#####

# # Now let's define some Models.
# class User(MongoModel):
#     # Use 'email' as the '_id' field in MongoDB.
#     email = fields.EmailField(primary_key=True)
#     fname = fields.CharField()
#     lname = fields.CharField()


# class BlogPost(MongoModel):
#     # This field references the User model above.
#     # It's stored as a bson.objectid.ObjectId in MongoDB.
#     author = fields.ReferenceField(User)
#     title = fields.CharField(max_length=100)
#     content = fields.CharField()
#     tags = fields.ListField(fields.StringField(max_length=20))
#     # These Comment objects will be stored inside each Post document in the
#     # database.
#     comments = fields.EmbeddedDocumentListField('Comment')

#     class Meta:
#         # Text index on content can be used for text search.
#         indexes = [IndexModel([('content', TEXT)])]

# # This is an "embedded" model and will be stored as a sub-document.


# class Comment(EmbeddedMongoModel):
#     author = fields.ReferenceField(User)
#     body = fields.CharField()
#     vote_score = fields.IntegerField(min_value=0)


# # Start the blog.
# # We need to save these objects before referencing them later.
# han_solo = User('mongoblogger@reallycoolmongostuff.com', 'Han', 'Solo').save()
# chewbacca = User(
#     'someoneelse@reallycoolmongostuff.com', 'Chewbacca', 'Thomas').save()


# post = BlogPost(
#     # Since this is a ReferenceField, we had to save han_solo first.
#     author=han_solo,
#     title="Five Crazy Health Foods Jabba Eats.",
#     content="...",
#     tags=['alien health', 'slideshow', 'jabba', 'huts'],
#     comments=[
#         Comment(author=chewbacca, body='Rrrrrrrrrrrrrrrr!', vote_score=42)
#     ]
# ).save()


# # Find objects using familiar MongoDB-style syntax.
# slideshows = BlogPost.objects.raw({'tags': 'slideshow'})

# # Only retrieve the 'title' field.
# slideshow_titles = slideshows.only('title')

# # u'Five Crazy Health Foods Jabba Eats.'
# print(slideshow_titles.first().title)
